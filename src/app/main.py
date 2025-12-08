from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.app.models import GenerateRequest, GenerateResponse
from src.app.dependencies import get_settings, get_anthropic_client
from src.app.services.anthropic_client import AnthropicClientProtocol
from src.app.config import Settings
from typing import Generator

from src.app.api.enqueue import router as enqueue_router

app = FastAPI(title="claude-proxy-poc")

app.include_router(enqueue_router)

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
    client: AnthropicClientProtocol = Depends(get_anthropic_client)
):
    """
    Generate text using the configured Claude model.
    Supports both streaming and non-streaming responses.
    
    Set stream=true in the request body for real-time streaming.
    """
    model = request.model or settings.DEFAULT_MODEL
    
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
        return GenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

