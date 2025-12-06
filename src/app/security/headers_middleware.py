from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response
from src.app.config import Settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, settings: Settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # HSTS
        if self.settings.HSTS_MAX_AGE > 0:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.settings.HSTS_MAX_AGE}; includeSubDomains"
            )
            
        # Anti-Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # MIME Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        
        # Content Security Policy (CSP)
        csp_policy = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "report-uri /security/csp-report;"
        )
        
        header_name = (
            "Content-Security-Policy-Report-Only" 
            if self.settings.CSP_REPORT_ONLY 
            else "Content-Security-Policy"
        )
        
        response.headers[header_name] = csp_policy
        
        return response

def configure_security_headers(app, settings: Settings):
    """
    Helper to add middleware to app.
    """
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
