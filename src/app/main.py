"""
Claude Proxy API - Unified Endpoint

Single endpoint /api/generate handles all functionality:
- Simple text generation
- Streaming responses  
- Tool use with confirmation (create files, run commands, etc.)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api import health, chat, tools, agents, workflow, auth, web_auth

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
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth (Device Flow)"]) # Deprecated but kept for reference
app.include_router(web_auth.router, prefix="/api/auth", tags=["Auth (Web Flow)"]) # New Web Flow
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(tools.router, prefix="/api/tools", tags=["Tools"])


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



