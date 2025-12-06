from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class QueueJob(BaseModel):
    """
    Represents a job in the queue.
    """
    id: str
    queue: str
    payload: Dict[str, Any]
    attempts: int = 0
    created_at: datetime
    visible_after: Optional[datetime] = None
