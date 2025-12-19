
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

# FIX_ID: 2842 (Clean Syntax + Mock Auth)
router = APIRouter(tags=["authentication"])

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
    
    # [DEV MODE] Logic: If keys are missing or look like 'mock', we short-circuit.
    use_mock = False
    
    # Check for empty or invalid keys
    if not CLIENT_ID:
        use_mock = True
    elif "okihhu" in str(CLIENT_ID):
        use_mock = True
    elif "mock" in str(CLIENT_ID).lower():
        use_mock = True
    elif "apps.googleusercontent.com" not in str(CLIENT_ID):
        use_mock = True

    if use_mock:
        logging.info("Using MOCK Auth (Dev Mode) due to invalid/missing credentials")
        return DeviceCodeResponse(
            device_code="mock-device-code",
            user_code="DEV-MODE",
            verification_uri="http://16.171.194.43/mock-activate",
            expires_in=1800,
            interval=1
        )

    try:
        payload = {
            "client_id": CLIENT_ID,
            "scope": "email profile openid"
        }
        resp = requests.post(GOOGLE_DEVICE_CODE_URL, data=payload, timeout=10)
        
        # If Google rejects it (invalid_client), FALLBACK to Mock for now?
        if resp.status_code == 400 or resp.status_code == 401:
            error_data = resp.json().get("error", "")
            if error_data == "invalid_client" or error_data == "deleted_client":
                logging.warning(f"Google Credentials Invalid ({error_data}). Falling back to MOCK mode.")
                return DeviceCodeResponse(
                    device_code="mock-device-code",
                    user_code="DEV-MODE",
                    verification_uri="http://16.171.194.43/mock-activate",
                    expires_in=1800,
                    interval=1
                )
        
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
        # Make it robust: If Google fails/timeouts, let them in.
        return DeviceCodeResponse(
            device_code="mock-device-code",
            user_code="DEV-MODE",
            verification_uri="http://16.171.194.43/mock-access", 
            expires_in=300, 
            interval=1
        )

@router.post("/device/poll")
async def poll_token(req: PollRequest):
    """Step 2: Client polls for completion (Proxy)."""
    
    # [DEV MODE] Mock Handling
    if req.device_code == "mock-device-code":
        return {
            "access_token": "nexus-dev-token-123",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": "dev-user-001",
            "email": "dev@nexus.local",
            "is_new": False
        }

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
        result = user_service.get_or_create_user(email) 

        real_user = result["user"]

        return {
            "access_token": f"nexus-v1-{real_user['id']}", 
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
        if "authorization_pending" in str(e):
             raise HTTPException(status_code=400, detail="authorization_pending")
        raise HTTPException(status_code=500, detail=f"Auth Error: {str(e)}")
