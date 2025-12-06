import time
from datetime import datetime, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from src.app.config import Settings
from src.app.security.auth import validate_api_key, validate_jwt, Client
from src.app.security.rate_limiter import get_rate_limiter
from src.app.security.audit import audit_event
from src.app.schemas.security import RequestAudit

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that handles:
    1. Authentication (sets request.state.client)
    2. Rate Limiting
    3. Audit Logging
    """
    def __init__(self, app, settings: Settings = Settings()):
        super().__init__(app)
        self.settings = settings
        self.rate_limiter = get_rate_limiter(settings)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # 1. Authentication
        client = None
        auth_error = None
        
        try:
            if self.settings.AUTH_MODE == "api_key":
                key = request.headers.get("X-API-Key")
                client = validate_api_key(key, self.settings)
            elif self.settings.AUTH_MODE == "jwt":
                # Manual extraction for middleware
                auth_header = request.headers.get("Authorization")
                creds = None
                if auth_header and auth_header.startswith("Bearer "):
                    from fastapi.security import HTTPAuthorizationCredentials
                    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_header.split(" ")[1])
                client = validate_jwt(creds, self.settings)
            else:
                # None or unknown
                client = Client(id="anonymous", plan="free")
                
            request.state.client = client
            
        except Exception as e:
            auth_error = str(e)
            # If auth is strictly required, we could return 401 here.
            # But typically we let the endpoint dependency handle the 401 if it requires auth.
            # However, for rate limiting, we might want to block unauth users early.
            # For this middleware, we'll proceed but mark client as None/Anonymous if failed?
            # Or better, return 401 immediately if AUTH_MODE is enabled.
            if self.settings.AUTH_MODE != "none":
                 return JSONResponse(status_code=401, content={"detail": str(e)})

        # 2. Rate Limiting
        client_id = client.id if client else (request.client.host if request.client else "unknown")
        
        if not self.rate_limiter.allow(client_id):
            usage = self.rate_limiter.get_usage(client_id)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={
                    "X-RateLimit-Limit": str(usage["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(usage["reset"] - int(time.time()))
                }
            )

        # 3. Process Request
        response = await call_next(request)
        
        # 4. Audit Logging
        duration = (time.time() - start_time) * 1000
        
        audit_entry = RequestAudit(
            timestamp=datetime.now(timezone.utc),
            client_id=client_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Fire and forget (sync in this case, but fast)
        audit_event(audit_entry, self.settings)
        
        return response
