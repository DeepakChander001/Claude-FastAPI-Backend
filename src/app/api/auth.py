
import os
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from fastapi import APIRouter, HTTPException, BackgroundTasks, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Config from Environment
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL", "https://accounts.google.com/.well-known/openid-configuration")

# Google Endpoints
GOOGLE_DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Models
class DeviceCodeResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int

class PollRequest(BaseModel):
    device_code: str

# --- Endpoints ---

@router.post("/device/code", response_model=DeviceCodeResponse)
async def request_device_code():
    """Step 1: Client requests a code from Google (Proxy)."""
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="Server misconfigured: Missing GOOGLE_CLIENT_ID")

    try:
        payload = {
            "client_id": CLIENT_ID,
            "scope": "email profile openid"
        }
        resp = requests.post(GOOGLE_DEVICE_CODE_URL, data=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        return DeviceCodeResponse(
            device_code=data["device_code"],
            user_code=data["user_code"],
            verification_uri=data["verification_url"],
            expires_in=data["expires_in"],
            interval=data["interval"]
        )
    except Exception as e:
        logger.error(f"Google Device Code Error: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to contact Google: {str(e)}")

@router.post("/device/poll")
async def poll_token(req: PollRequest):
    """Step 2: Client polls for completion (Proxy)."""
    if not CLIENT_ID or not CLIENT_SECRET:
         raise HTTPException(status_code=500, detail="Server misconfigured: Missing Secrets")
         
    try:
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "device_code": req.device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        
        resp = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=10)
        
        # Handle "Waiting" State
        if resp.status_code == 428 or (resp.status_code == 400 and resp.json().get("error") == "authorization_pending"):
            raise HTTPException(status_code=400, detail="authorization_pending")
            
        if resp.status_code == 403 or (resp.status_code == 400 and resp.json().get("error") == "access_denied"):
             raise HTTPException(status_code=403, detail="access_denied")

        resp.raise_for_status() # Raise for other real errors
        
        data = resp.json()
        raw_id_token = data.get("id_token")
        
        # Verify ID Token
        id_info = id_token.verify_oauth2_token(
            raw_id_token, 
            google_requests.Request(), 
            CLIENT_ID
        )
        
        email = id_info.get("email")
        name = id_info.get("name")
        picture = id_info.get("picture")
        
        # Upsert User in Supabase
        from src.app.services.user_service import UserService
        user_service = UserService()
        result = user_service.get_or_create_user(email) # TODO: Pass name/picture if service supports it
        
        real_user = result["user"]
        
        # Return Session Token (For now, mimicking the ID token or creating a custom one)
        # We can return the Google ID Token or a custom JWT. 
        # For parity with existing CLI logic, we return access_token.
        return {
            "access_token": f"nexus-v1-{real_user['id']}", # Keep simple for now
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": real_user["id"],
            "email": email,
            "is_new": result["is_new"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google Token Poll Error: {e}")
        # Return 400 for pending to keep polling, unless it's a real crash
        if "authorization_pending" in str(e):
             raise HTTPException(status_code=400, detail="authorization_pending")
        raise HTTPException(status_code=500, detail=f"Auth Error: {str(e)}")

# Remove Mock Endpoints (activate/approve) as Google handles the UI now

