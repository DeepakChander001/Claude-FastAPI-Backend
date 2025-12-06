from fastapi import FastAPI, Depends, HTTPException
from src.app.models import GenerateRequest, GenerateResponse
from src.app.dependencies import get_settings, get_anthropic_client
from src.app.services.anthropic_client import AnthropicClientProtocol
from src.app.config import Settings

from src.app.api.enqueue import router as enqueue_router

app = FastAPI(title="claude-proxy-poc")

app.include_router(enqueue_router)

@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}

@app.post("/api/generate", response_model=GenerateResponse)
def generate(
    request: GenerateRequest,
    settings: Settings = Depends(get_settings),
    client: AnthropicClientProtocol = Depends(get_anthropic_client)
):
    """
    Generate text using the configured Claude model.
    Currently supports synchronous generation only.
    """
    # TODO: Implement streaming support when request.stream is True.
    
    try:
        result = client.generate_text(
            prompt=request.prompt,
            model=request.model or settings.DEFAULT_MODEL,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return GenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
