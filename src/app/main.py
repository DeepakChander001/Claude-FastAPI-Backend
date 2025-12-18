"""
Claude Proxy API - Unified Endpoint

Single endpoint /api/generate handles all functionality:
- Simple text generation
- Streaming responses  
- Tool use with confirmation (create files, run commands, etc.)
"""

from fastapi import FastAPI
from src.app.api.unified import router as unified_router
from src.app.api.agentic import router as agentic_router
from src.app.api.auth import router as auth_router

app = FastAPI(
    title="Claude Proxy API",
    description="Unified AI endpoint with tool use and confirmation",
    version="2.0.0"
)

# Include the unified router (main endpoint: /api/generate)
app.include_router(unified_router)

# Include Authentication Router
app.include_router(auth_router)

# Keep agentic router for backward compatibility
app.include_router(agentic_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def root():
    """API documentation redirect."""
    return {
        "message": "Claude Proxy API",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /api/generate - Unified endpoint for all operations",
            "health": "GET /health - Health check"
        }
    }



