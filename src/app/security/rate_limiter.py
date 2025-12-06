import time
from typing import Dict, Tuple
from fastapi import Request, Response, HTTPException, Depends
from src.app.config import Settings

class RateLimiter:
    """
    Abstract base for rate limiting.
    """
    def allow(self, client_id: str) -> bool:
        raise NotImplementedError
    
    def get_usage(self, client_id: str) -> Dict[str, int]:
        raise NotImplementedError

class InMemoryRateLimiter(RateLimiter):
    """
    Simple token bucket / fixed window limiter for testing.
    Resets every minute.
    """
    def __init__(self, limit_per_minute: int):
        self.limit = limit_per_minute
        self.windows: Dict[str, Tuple[int, int]] = {} # client_id -> (timestamp_minute, count)

    def allow(self, client_id: str) -> bool:
        current_minute = int(time.time() / 60)
        
        window = self.windows.get(client_id)
        
        if not window or window[0] != current_minute:
            # New window
            self.windows[client_id] = (current_minute, 1)
            return True
        
        # Existing window
        timestamp, count = window
        if count < self.limit:
            self.windows[client_id] = (timestamp, count + 1)
            return True
            
        return False

    def get_usage(self, client_id: str) -> Dict[str, int]:
        current_minute = int(time.time() / 60)
        window = self.windows.get(client_id)
        
        if not window or window[0] != current_minute:
            return {
                "limit": self.limit,
                "remaining": self.limit,
                "reset": (current_minute + 1) * 60
            }
            
        count = window[1]
        return {
            "limit": self.limit,
            "remaining": max(0, self.limit - count),
            "reset": (current_minute + 1) * 60
        }

# Global instance for simplicity in this demo
_LIMITER = None

def get_rate_limiter(settings: Settings = Depends(Settings)) -> RateLimiter:
    global _LIMITER
    if _LIMITER is None:
        # In production, you would initialize a RedisRateLimiter here
        # e.g., RedisRateLimiter(redis_client, settings.RATE_LIMIT_PER_MINUTE)
        _LIMITER = InMemoryRateLimiter(settings.RATE_LIMIT_PER_MINUTE)
    return _LIMITER

async def check_rate_limit(
    request: Request, 
    response: Response,
    limiter: RateLimiter = Depends(get_rate_limiter)
):
    """
    Dependency to enforce rate limits.
    """
    # Identify client: prefer authenticated ID, fallback to IP
    client_id = "anonymous"
    if hasattr(request.state, "client") and request.state.client:
        client_id = request.state.client.id
    else:
        client_id = request.client.host if request.client else "unknown"
        
    if not limiter.allow(client_id):
        usage = limiter.get_usage(client_id)
        response.headers["X-RateLimit-Limit"] = str(usage["limit"])
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["Retry-After"] = str(usage["reset"] - int(time.time()))
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
    usage = limiter.get_usage(client_id)
    response.headers["X-RateLimit-Limit"] = str(usage["limit"])
    response.headers["X-RateLimit-Remaining"] = str(usage["remaining"])
