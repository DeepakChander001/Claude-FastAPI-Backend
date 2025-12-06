import pytest
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.app.config import Settings
from src.app.security.headers_middleware import SecurityHeadersMiddleware
from src.app.security.csp_report import router as csp_router
from src.app.security.redis_rate_limiter import RedisRateLimiter

def test_security_headers_middleware():
    app = FastAPI()
    settings = Settings(HSTS_MAX_AGE=60, CSP_REPORT_ONLY=True)
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    
    @app.get("/")
    def root():
        return {"ok": True}
        
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=60" in response.headers["Strict-Transport-Security"]
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy-Report-Only" in response.headers
    assert "report-uri /security/csp-report" in response.headers["Content-Security-Policy-Report-Only"]

def test_csp_report_endpoint():
    app = FastAPI()
    app.include_router(csp_router)
    
    client = TestClient(app)
    payload = {
        "csp-report": {
            "document-uri": "http://example.com",
            "referrer": "",
            "violated-directive": "script-src 'self'",
            "original-policy": "script-src 'self'; report-uri /security/csp-report",
            "blocked-uri": "http://evil.com/script.js"
        }
    }
    
    response = client.post("/security/csp-report", json=payload)
    assert response.status_code == 204

def test_redis_rate_limiter_fallback():
    # Test in-memory fallback
    limiter = RedisRateLimiter(redis_client=None, limit=2, window=60)
    client_id = "test_user"
    
    # 1st Request
    allowed, headers = limiter.is_allowed(client_id)
    assert allowed is True
    assert headers["X-RateLimit-Remaining"] == "1"
    
    # 2nd Request
    allowed, headers = limiter.is_allowed(client_id)
    assert allowed is True
    assert headers["X-RateLimit-Remaining"] == "0"
    
    # 3rd Request (Blocked)
    allowed, headers = limiter.is_allowed(client_id)
    assert allowed is False
    assert "Retry-After" in headers
