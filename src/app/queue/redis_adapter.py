import json
import uuid
import time
from typing import Optional, Dict, Any
from src.app.queue.adapter import QueueAdapter

class RedisAdapter(QueueAdapter):
    """
    Redis-backed queue adapter.
    Uses lists for queues and sorted sets for delayed/scheduled jobs.
    
    NOTE: This is a simplified implementation. Production systems might use 
    Redis Streams or a library like RQ/Celery/Bull.
    """
    def __init__(self, redis_url: Optional[str] = None, client=None):
        self.client = client
        if not self.client and redis_url:
            # Safe import
            try:
                import redis
                self.client = redis.Redis.from_url(redis_url)
            except ImportError:
                pass # Client remains None, methods will raise if called

    def _check_client(self):
        if not self.client:
            raise RuntimeError("Redis client not initialized. Install 'redis' package or inject a client.")

    def enqueue(self, queue_name: str, job: Dict[str, Any]) -> str:
        self._check_client()
        job_id = job.get("id") or str(uuid.uuid4())
        job["id"] = job_id
        # LPUSH to list
        self.client.lpush(f"queue:{queue_name}", json.dumps(job))
        return job_id

    def reserve(self, queue_name: str, timeout: Optional[int] = 0) -> Optional[Dict[str, Any]]:
        self._check_client()
        # RPOP from list
        # In a real system, we'd use RPOPLPUSH to a processing queue for safety
        raw = self.client.rpop(f"queue:{queue_name}")
        if raw:
            return json.loads(raw)
        return None

    def ack(self, queue_name: str, job_id: str) -> None:
        self._check_client()
        # If using RPOPLPUSH, we would LREM from the processing queue here.
        pass

    def fail(self, queue_name: str, job_id: str, reason: Optional[str] = None) -> None:
        self._check_client()
        # Move to DLQ
        # We assume the job payload isn't readily available here in this simple RPOP model
        # unless passed in. But the interface assumes we know the ID.
        # For this simple adapter, we might need the full job to move it.
        # If we can't move it, we just log.
        pass

    def requeue(self, queue_name: str, job: Dict[str, Any], delay_seconds: Optional[int] = 0) -> str:
        self._check_client()
        if delay_seconds and delay_seconds > 0:
            # ZADD to delayed set
            score = time.time() + delay_seconds
            self.client.zadd(f"queue:{queue_name}:delayed", {json.dumps(job): score})
        else:
            self.enqueue(queue_name, job)
        return job["id"]

    def inspect_queue_length(self, queue_name: str) -> int:
        self._check_client()
        return self.client.llen(f"queue:{queue_name}")
