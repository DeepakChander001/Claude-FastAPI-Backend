"""
Claude Proxy API - Unified Endpoint

Single endpoint /api/generate handles all functionality:
- Simple text generation
- Streaming responses  
- Tool use with confirmation (create files, run commands, etc.)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api import auth, unified, workspace

app = FastAPI(title="Claude Proxy Backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(unified.router, prefix="/api", tags=["Unified"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["Workspace"])


@app.get("/health")
@app.get("/api/health")
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
