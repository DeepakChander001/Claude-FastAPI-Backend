
import os
import sqlite3
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
from src.app.core.config import settings

# Initialize Router
router = APIRouter()

# Templates
try:
    templates = Jinja2Templates(directory="src/app/templates")
except:
    templates = None # Fallback if directory missing

# Simple SQLite Access
DB_PATH = "/home/ubuntu/EC2-Backend/auth_sessions.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                access_token TEXT,
                user_info TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

# Run Init on module load (safe for now)
init_db()

# --- Models ---
class AuthInitResponse(BaseModel):
    session_id: str
    auth_url: str

class PollResponse(BaseModel):
    status: str
    token: dict = None
    user: dict = None

# --- Configuration ---
def get_google_config():
    # Load from Env or Settings
    # NOTE: Accessing os.environ directly to ensure we get latest values
    client_id = os.environ.get("GOOGLE_CLIENT_ID") or settings.GOOGLE_CLIENT_ID
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET") or settings.GOOGLE_CLIENT_SECRET
    # Discovery URL is usually standard, but we honor config
    discovery_url = os.environ.get("GOOGLE_DISCOVERY_URL") or "https://accounts.google.com/.well-known/openid-configuration"
    
    # Dynamic Redirect URI based on Host?
    # For now, we HARDCODE the recommended IP-based URI
    # Or use headers. For MVP, we use the server's public IP
    # We will need to update this if we add a domain.
    # We assume Port 80
    redirect_uri = "http://16.171.194.43/api/auth/callback" 
    
    return client_id, client_secret, discovery_url, redirect_uri

def get_google_endpoints():
    try:
        _, _, discovery_url, _ = get_google_config()
        resp = requests.get(discovery_url)
        resp.raise_for_status()
        return resp.json()
    except:
        # Fallback defaults
        return {
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_endpoint": "https://oauth2.googleapis.com/token",
            "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
        }

# --- Endpoints ---

@router.post("/init", response_model=AuthInitResponse)
async def init_session():
    """CLI calls this to start a login session."""
    session_id = str(uuid.uuid4())
    
    # Create Record in DB
    conn = get_db_connection()
    conn.execute("INSERT INTO sessions (session_id, status) VALUES (?, ?)", (session_id, "pending"))
    conn.commit()
    conn.close()
    
    # Generate URL
    client_id, _, _, redirect_uri = get_google_config()
    meta = get_google_endpoints()
    auth_endpoint = meta.get("authorization_endpoint")
    
    # Construct OAuth URL
    # We pass session_id as 'state' to track it callback
    url = f"{auth_endpoint}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=email profile openid&state={session_id}&access_type=offline&prompt=consent"
    
    return AuthInitResponse(session_id=session_id, auth_url=url)

@router.get("/callback")
async def auth_callback(request: Request):
    """Google redirects here."""
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    state = request.query_params.get("state") # session_id

    if error:
        return HTMLResponse(f"<h1>Login Failed</h1><p>{error}</p>")
    
    if not code or not state:
        return HTMLResponse("<h1>Invalid Request</h1><p>Missing code or state</p>")

    # Exchange Code for Token
    client_id, client_secret, _, redirect_uri = get_google_config()
    meta = get_google_endpoints()
    token_endpoint = meta.get("token_endpoint")
    
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    try:
        token_resp = requests.post(token_endpoint, data=payload)
        token_data = token_resp.json()
        
        if "error" in token_data:
             return HTMLResponse(f"<h1>Token Error</h1><p>{token_data}</p>")

        # Get User Info
        access_token = token_data.get("access_token")
        id_token = token_data.get("id_token") # TODO: Verify signature
        
        user_resp = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        user_info = user_resp.json()
        
        # Validation
        if not user_info.get("email"):
             return HTMLResponse("<h1>Error</h1><p>Could not retrieve email</p>")

        # Update Session in DB
        conn = get_db_connection()
        conn.execute(
            "UPDATE sessions SET status=?, access_token=?, user_info=? WHERE session_id=?",
            ("complete", json.dumps(token_data), json.dumps(user_info), state)
        )
        conn.commit()
        conn.close()
        
        # Render Success
        if templates:
            return templates.TemplateResponse("success.html", {"request": request, "email": user_info.get("email")})
        else:
            return HTMLResponse(f"<h1>Login Successful!</h1><p>Welcome {user_info.get('email')}. You can close this window.</p>")

    except Exception as e:
        return HTMLResponse(f"<h1>Server Error</h1><p>{str(e)}</p>")

@router.get("/poll")
async def poll_session(session_id: str):
    """CLI polls this."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, access_token, user_info FROM sessions WHERE session_id=?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    
    status = row["status"]
    
    if status == "pending":
        return {"status": "pending"}
    
    if status == "complete":
        # Return the Token Data the CLI needs
        # We can implement User creation here or let CLI do it?
        # Better: Do user creation here if needed.
        # For parity, we define an 'access_token' for Nexus
        
        user_info = json.loads(row["user_info"])
        token_data = json.loads(row["access_token"])
        
        # Upsert User logic (Simplified)
        from src.app.services.user_service import UserService
        try:
            svc = UserService()
            u_res = svc.get_or_create_user(user_info["email"])
            user_id = u_res["user"]["id"]
        except:
            user_id = "temp-id"

        return {
            "status": "complete",
            "access_token": f"nexus-v1-{user_id}", # Minimal token
            "google_token": token_data,
            "user": user_info
        }
    
    return {"status": "error"}
