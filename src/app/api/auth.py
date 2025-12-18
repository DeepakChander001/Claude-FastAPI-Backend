
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# In-Memory Storage for Device Codes (Use Redis/DB in Production)
DEVICE_CODES: Dict[str, Dict[str, Any]] = {}
USER_TOKENS: Dict[str, str] = {} # Mock Token Store

# Config
BASE_URL = "http://16.171.194.43:8000" 

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
    """Step 1: Client requests a code."""
    device_code = str(uuid.uuid4())
    user_code = str(uuid.uuid4())[:8].upper() # Human readable-ish
    
    DEVICE_CODES[device_code] = {
        "user_code": user_code,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    return DeviceCodeResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=f"{BASE_URL}/activate",
        expires_in=300,
        interval=2
    )

@router.post("/device/poll")
async def poll_token(req: PollRequest):
    """Step 2: Client polls for completion."""
    data = DEVICE_CODES.get(req.device_code)
    if not data:
        raise HTTPException(status_code=404, detail="Invalid code")
    
    if data["status"] == "pending":
        raise HTTPException(status_code=400, detail="authorization_pending")
        
    if data["status"] == "denied":
         raise HTTPException(status_code=403, detail="access_denied")
         
    if data["status"] == "success":
        # Issue Token
        user_id = data.get("user_id", "u-generic")
        email = data.get("email", "unknown")
        
        # In real life, generate JWT here
        token = f"nexus-v1-{user_id}"
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": user_id,
            "email": email
        }

# --- Web UI for Activation ---

@router.get("/activate", response_class=HTMLResponse)
async def activate_page(user_code: Optional[str] = None):
    """Step 3: User visits URL to Authorize."""
    prefill = user_code or ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexus Login</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }}
            .card {{ background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }}
            h1 {{ margin-bottom: 1.5rem; }}
            input {{ padding: 0.75rem; font-size: 1.2rem; width: 100%; margin-bottom: 1rem; text-align: center; border: 1px solid #ccc; border-radius: 6px; }}
            button {{ background: #4285f4; color: white; border: none; padding: 0.75rem 2rem; border-radius: 6px; font-size: 1rem; cursor: pointer; width: 100%; }}
            button:hover {{ background: #357abd; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Nexus CLI Login</h1>
            <p>Enter the code displayed in your terminal</p>
            <form action="/api/auth/approve" method="post">
                <input type="text" name="user_code" value="{prefill}" placeholder="ABCD-1234" required>
                <button type="submit">Login with Google</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/approve", response_class=HTMLResponse)
async def approve_code(user_code: str = Form(...)):
    """Step 4: User submits code (Simulated Google Auth for now)."""
    
    # 1. Find the Device Code for this User Code
    target_device = None
    for d_code, data in DEVICE_CODES.items():
        if data["user_code"] == user_code.strip():
            target_device = d_code
            break
            
    if not target_device:
        return HTMLResponse("<h1>Error: Invalid Code</h1><a href='/activate'>Try Again</a>")

    # 2. Simulate "Google Login" Success
    # In real life, this would actually redirect to Google first, handle callback, then do this.
    # To satisfy "User Perspective", we act AS IF we did that.
    
    # Mock User Email (Simulated for this flow, in real OAuth we get this from Google)
    user_email = "user@gmail.com" 
    
    # === REAL SUPABASE PERSISTENCE ===
    try:
        from src.app.services.user_service import UserService
        user_service = UserService()
        result = user_service.get_or_create_user(user_email)
        
        real_user = result["user"]
        is_new = result["is_new"]
        
        DEVICE_CODES[target_device]["status"] = "success"
        DEVICE_CODES[target_device]["user_id"] = real_user["id"]
        DEVICE_CODES[target_device]["email"] = real_user["email"]
        DEVICE_CODES[target_device]["is_new"] = is_new # Pass flag to CLI
        
    except Exception as e:
        logger.error(f"Auth Error: {e}")
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")
    
    return HTMLResponse("""
    <div style="text-align: center; font-family: sans-serif; padding-top: 50px;">
        <h1 style="color: green;">✅ Login Successful</h1>
        <p>You can close this window and return to your terminal.</p>
    </div>
    """)

