from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.app.models import GenerateRequest, GenerateResponse
from src.app.dependencies import get_settings, get_anthropic_client
from src.app.services.anthropic_client import AnthropicClientProtocol
from src.app.config import Settings
from src.app.db import SupabaseClientWrapper
from typing import Generator, Optional
from datetime import datetime
import logging

from src.app.api.enqueue import router as enqueue_router
from src.app.api.agentic import router as agentic_router

logger = logging.getLogger(__name__)

app = FastAPI(title="claude-proxy-poc")

app.include_router(enqueue_router)
app.include_router(agentic_router)

# Global database client (initialized on startup)
_db_client: Optional[SupabaseClientWrapper] = None


def get_db_client(settings: Settings = Depends(get_settings)) -> Optional[SupabaseClientWrapper]:
    """Get or create the database client."""
    global _db_client
    if _db_client is None and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        _db_client = SupabaseClientWrapper(
            url=settings.SUPABASE_URL,
            key=settings.SUPABASE_KEY
        )
    return _db_client


@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


def stream_generator(
    client: AnthropicClientProtocol,
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float
) -> Generator[str, None, None]:
    """
    Generator that yields streaming tokens from the client.
    """
    for chunk in client.stream_generate(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    ):
        yield chunk


@app.post("/api/generate")
def generate(
    request: GenerateRequest,
    settings: Settings = Depends(get_settings),
    client: AnthropicClientProtocol = Depends(get_anthropic_client),
    db: Optional[SupabaseClientWrapper] = Depends(get_db_client)
):
    """
    Generate text using the configured Claude model.
    Supports both streaming and non-streaming responses.
    All requests are logged to Supabase database.
    
    Set stream=true in the request body for real-time streaming.
    """
    model = request.model or settings.DEFAULT_MODEL
    
    # Log request to database
    request_record = None
    if db and db.client:
        try:
            request_record = db.create_request(
                prompt=request.prompt,
                model=model,
                stream=request.stream,
                user_id=None  # Can be extracted from auth later
            )
            logger.info(f"Request logged to database: {request_record.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to log request to database: {e}")
    
    # If streaming is requested, return a StreamingResponse
    if request.stream:
        return StreamingResponse(
            stream_generator(
                client=client,
                prompt=request.prompt,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ),
            media_type="text/plain"
        )
    
    # Non-streaming: return full response
    try:
        result = client.generate_text(
            prompt=request.prompt,
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Update database with response
        if db and db.client and request_record:
            try:
                db.update_request_status(
                    request_id=request_record.get("id", ""),
                    status="done",
                    partial_output=result.get("output", ""),
                    completed_at=datetime.utcnow().isoformat()
                )
                
                # Record token usage
                usage = result.get("usage", {})
                total_tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                if total_tokens > 0:
                    db.record_usage(
                        request_id=request_record.get("id", ""),
                        tokens=total_tokens,
                        cost=0.0  # Calculate cost based on model pricing
                    )
                logger.info(f"Request completed and logged: {request_record.get('id', 'unknown')}")
            except Exception as e:
                logger.error(f"Failed to update request in database: {e}")
        
        return GenerateResponse(**result)
    except Exception as e:
        # Log failure to database
        if db and db.client and request_record:
            try:
                db.update_request_status(
                    request_id=request_record.get("id", ""),
                    status="failed",
                    partial_output=str(e)
                )
            except Exception as db_error:
                logger.error(f"Failed to log error to database: {db_error}")
        
        raise HTTPException(status_code=500, detail=str(e))


