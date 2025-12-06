import time
import logging
from typing import Optional, Tuple, Any, Dict
from src.app.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class RedisRateLimiter(RateLimiter):
    """
    Redis-backed rate limiter using fixed window counter.
    Falls back to in-memory if redis_client is None.
    """
    def __init__(self, redis_client: Any = None, limit: int = 60, window: int = 60):
        self.redis = redis_client
        self.limit = limit
        self.window = window
        self._memory_fallback = {}
        
    def is_allowed(self, client_id: str) -> Tuple[bool, Dict[str, str]]:
        if not self.redis:
            return self._check_memory(client_id)
            
        key = f"rate_limit:{client_id}"
        try:
            # Simple fixed window: INCR key, EXPIRE if new
            # For atomic operations in prod, use Lua script
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, self.window)
                
            remaining = max(0, self.limit - current)
            reset_time = int(time.time()) + self.window # Approx
            
            headers = {
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time)
            }
            
            if current > self.limit:
                headers["Retry-After"] = str(self.window)
                return False, headers
                
            return True, headers
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fail open or closed? Let's fail open for availability
            return True, {}

    def _check_memory(self, client_id: str) -> Tuple[bool, Dict[str, str]]:
        """
        Simple in-memory fallback for tests/local.
        Note: This implementation is not thread-safe or distributed.
        """
        now = int(time.time())
        window_key = f"{client_id}:{now // self.window}"
        
        count = self._memory_fallback.get(window_key, 0)
        count += 1
        self._memory_fallback[window_key] = count
        
        # Cleanup old keys (naive)
        if len(self._memory_fallback) > 1000:
            self._memory_fallback.clear()
            
        remaining = max(0, self.limit - count)
        
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(now + self.window)
        }
        
        if count > self.limit:
            headers["Retry-After"] = str(self.window)
            return False, headers
            
        return True, headers
