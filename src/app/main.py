from fastapi import FastAPI, Depends, HTTPException
from src.app.models import GenerateRequest, GenerateResponse
from src.app.deps import get_settings, get_client
from src.app.client import AnthropicClientWrapper
from src.app.config import Settings

app = FastAPI(title="claude-proxy-poc")

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
    client: AnthropicClientWrapper = Depends(get_client)
):
    """
    Generate text using the configured Claude model.
    Currently supports synchronous generation only.
    """
    # TODO: Implement streaming support when request.stream is True.
    # For now, we ignore request.stream or return an error if strictly required.
    
    try:
        result = client.generate_sync(
            prompt=request.prompt,
            model=request.model or settings.DEFAULT_MODEL,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return GenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
