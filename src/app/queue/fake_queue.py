import uuid
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from src.app.queue.adapter import QueueAdapter
from src.app.queue.models import QueueJob

class FakeQueue(QueueAdapter):
    """
    In-memory queue for testing.
    """
    def __init__(self):
        self.queues: Dict[str, List[QueueJob]] = {}
        self.dlq: List[QueueJob] = []
        self.reserved: Dict[str, QueueJob] = {} # job_id -> job

    def enqueue(self, queue_name: str, job: Dict[str, Any]) -> str:
        if queue_name not in self.queues:
            self.queues[queue_name] = []
            
        job_id = job.get("id") or str(uuid.uuid4())
        # Ensure it matches our model structure
        q_job = QueueJob(
            id=job_id,
            queue=queue_name,
            payload=job.get("payload", job), # Handle if job is already payload or full dict
            created_at=datetime.now(),
            attempts=job.get("attempts", 0),
            visible_after=job.get("visible_after")
        )
        
        self.queues[queue_name].append(q_job)
        return job_id

    def reserve(self, queue_name: str, timeout: Optional[int] = 0) -> Optional[Dict[str, Any]]:
        if queue_name not in self.queues:
            return None
            
        now = datetime.now()
        
        # Find first visible job
        for i, job in enumerate(self.queues[queue_name]):
            if job.visible_after and job.visible_after > now:
                continue
                
            # Found one
            self.queues[queue_name].pop(i)
            job.attempts += 1
            self.reserved[job.id] = job
            
            # Return dict representation
            return job.model_dump()
            
        return None

    def ack(self, queue_name: str, job_id: str) -> None:
        if job_id in self.reserved:
            del self.reserved[job_id]

    def fail(self, queue_name: str, job_id: str, reason: Optional[str] = None) -> None:
        if job_id in self.reserved:
            job = self.reserved.pop(job_id)
            self.dlq.append(job)

    def requeue(self, queue_name: str, job: Dict[str, Any], delay_seconds: Optional[int] = 0) -> str:
        # If it was reserved, remove from reserved
        job_id = job.get("id")
        if job_id and job_id in self.reserved:
            del self.reserved[job_id]
            
        # Update visibility
        visible_after = None
        if delay_seconds:
            visible_after = datetime.now() + timedelta(seconds=delay_seconds)
            
        # Add back to queue
        if queue_name not in self.queues:
            self.queues[queue_name] = []
            
        q_job = QueueJob(
            id=job_id or str(uuid.uuid4()),
            queue=queue_name,
            payload=job.get("payload", job),
            created_at=datetime.now(),
            attempts=job.get("attempts", 0),
            visible_after=visible_after
        )
        self.queues[queue_name].append(q_job)
        return q_job.id

    def inspect_queue_length(self, queue_name: str) -> int:
        return len(self.queues.get(queue_name, []))
