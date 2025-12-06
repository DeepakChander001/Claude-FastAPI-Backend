from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.app.queue.adapter import QueueAdapter
from src.app.queue.fake_queue import FakeQueue
from src.app.repos.request_repo import RequestRepo
from src.app.repos.fake_request_repo import FakeRequestRepo
from src.app.config import Settings
from src.app.dependencies import get_settings

router = APIRouter()

class EnqueueRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    stream: bool = True
    user_id: Optional[str] = None

class EnqueueResponse(BaseModel):
    request_id: str
    queued: bool

# Dependencies (In a real app, these would be provided by a DI container or main.py)
# For now, we use singletons or fakes if not initialized
_QUEUE: Optional[QueueAdapter] = None
_REPO: Optional[RequestRepo] = None

def get_queue() -> QueueAdapter:
    global _QUEUE
    if _QUEUE is None:
        _QUEUE = FakeQueue() # Default to fake for safety/demo
    return _QUEUE

def get_repo() -> RequestRepo:
    global _REPO
    if _REPO is None:
        _REPO = FakeRequestRepo()
    return _REPO

@router.post("/api/enqueue", response_model=EnqueueResponse)
def enqueue_job(
    req: EnqueueRequest,
    queue: QueueAdapter = Depends(get_queue),
    repo: RequestRepo = Depends(get_repo),
    settings: Settings = Depends(get_settings)
):
    """
    Enqueues a new LLM generation job.
    """
    # 1. Create Request Record
    # We generate ID here or let repo do it. 
    # FakeRepo creates it. Real repo might need us to pass ID.
    # Let's assume we generate ID first.
    import uuid
    request_id = str(uuid.uuid4())
    
    repo.create_request(
        request_id=request_id,
        user_id=req.user_id,
        prompt=req.prompt,
        model=req.model or settings.DEFAULT_MODEL
    )
    
    # 2. Enqueue Job
    job_payload = {
        "request_id": request_id,
        "prompt": req.prompt,
        "model": req.model,
        "stream": req.stream
    }
    
    queue.enqueue("default", job_payload)
    
    return EnqueueResponse(request_id=request_id, queued=True)
