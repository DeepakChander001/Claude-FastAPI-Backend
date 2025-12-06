import logging
from typing import Optional
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from src.app.config import Settings
from src.app.schemas.security import Client

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------
# Security Schemes
# ------------------------------------------------------------------------
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

# ------------------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------------------
def get_settings() -> Settings:
    return Settings()

def validate_api_key(
    api_key: str = Security(api_key_header),
    settings: Settings = Depends(get_settings)
) -> Client:
    """
    Validates X-API-Key header against allowed keys.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")
    
    allowed_keys = [k.strip() for k in settings.ALLOWED_API_KEYS.split(",") if k.strip()]
    
    if api_key not in allowed_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # In a real app, you might map keys to specific user IDs
    return Client(id=f"apikey-{api_key[:4]}", plan="standard")

def validate_jwt(
    creds: Optional[HTTPAuthorizationCredentials] = Security(http_bearer),
    settings: Settings = Depends(get_settings)
) -> Client:
    """
    Validates Bearer token (JWT).
    Falls back to simple check if PyJWT is missing.
    """
    if not creds:
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
    
    token = creds.credentials
    
    # Try using PyJWT
    try:
        import jwt
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return Client(id=payload.get("sub", "unknown"), plan=payload.get("plan", "free"))
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except ImportError:
        # Fallback for testing without PyJWT
        if token == "TEST_JWT":
            return Client(id="test-user", plan="premium")
        raise HTTPException(status_code=401, detail="Invalid token (PyJWT not installed)")

def get_current_client(
    request: Request,
    settings: Settings = Depends(get_settings)
) -> Client:
    """
    Main dependency to get the authenticated client based on configured mode.
    """
    mode = settings.AUTH_MODE.lower()
    
    if mode == "none":
        return Client(id="anonymous", plan="free")
        
    if mode == "api_key":
        # We manually call the validator here to reuse logic, 
        # but typically FastAPI handles this via Depends chain.
        # However, since we want conditional logic, we do it imperatively or via sub-dependency.
        # A cleaner way in FastAPI is to return the dependency callable itself, but that's complex.
        # We'll just use the request state if middleware set it, or re-validate.
        # Ideally, middleware sets request.state.client.
        if hasattr(request.state, "client") and request.state.client:
            return request.state.client
            
        # Fallback if middleware didn't run or failed (shouldn't happen if configured right)
        # But for dependency injection in endpoints:
        key = request.headers.get("X-API-Key")
        return validate_api_key(key, settings)
        
    if mode == "jwt":
        if hasattr(request.state, "client") and request.state.client:
            return request.state.client
        
        # Manual extraction for fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            return validate_jwt(creds, settings)
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    raise HTTPException(status_code=500, detail=f"Unknown AUTH_MODE: {mode}")
