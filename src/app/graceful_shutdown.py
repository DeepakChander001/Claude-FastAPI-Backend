import signal
import asyncio
import logging
import os
from typing import Callable, List

logger = logging.getLogger(__name__)

_shutdown_handlers: List[Callable[[], None]] = []

def register_shutdown_handler(handler: Callable[[], None]):
    """
    Register a function to be called during graceful shutdown.
    """
    _shutdown_handlers.append(handler)

async def _run_shutdown_handlers():
    logger.info("Running shutdown handlers...")
    for handler in _shutdown_handlers:
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
        except Exception as e:
            logger.error(f"Error in shutdown handler: {e}")
    logger.info("Shutdown handlers completed.")

def serve_with_uvicorn(app, host="0.0.0.0", port=8000):
    """
    Programmatic uvicorn execution with graceful shutdown support.
    Useful if running uvicorn directly (not via gunicorn).
    """
    import uvicorn
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        loop="asyncio",
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Override signal handlers if needed, but uvicorn handles SIGTERM/SIGINT well.
    # We can hook into the 'shutdown' event of the lifespan.
    
    server.run()

# Integration Note:
# When using Gunicorn + UvicornWorker (as in Dockerfile.prod), 
# Gunicorn handles the signals and passes them to the worker.
# FastAPI's lifespan 'shutdown' event is the standard place to put cleanup logic.
#
# Example in main.py:
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield
#     await _run_shutdown_handlers()
