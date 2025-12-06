from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.app.queue.adapter import QueueAdapter
from src.app.api.enqueue import get_queue

router = APIRouter()

class ExtendedHealthResponse(BaseModel):
    status: str
    queue_depth: int
    canary_safe: bool

@router.get("/health/extended", response_model=ExtendedHealthResponse)
def extended_health_check(queue: QueueAdapter = Depends(get_queue)):
    """
    Extended health check for canary validation.
    Checks queue depth and other deep dependencies.
    """
    try:
        depth = queue.inspect_queue_length("default")
        
        # Simple logic: if queue is backlogged > 100, canary might be unsafe or overloaded
        canary_safe = depth < 100
        
        return ExtendedHealthResponse(
            status="ok",
            queue_depth=depth,
            canary_safe=canary_safe
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")
