import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from src.app.observability import (
    increment_request_counter,
    observe_request_duration,
    track_in_flight,
    get_tracer
)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to capture metrics and traces for every request.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        method = request.method
        
        # Skip metrics for health checks or metrics endpoint itself to reduce noise
        if path in ["/health", "/metrics", "/favicon.ico"]:
            return await call_next(request)

        start_time = time.time()
        track_in_flight(method, path, increment=True)
        
        tracer = get_tracer()
        
        # Create a server span
        # In a real OTel setup, we would extract context from headers here (propagation)
        with tracer.start_as_current_span(f"{method} {path}") as span:
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", str(request.url))
            
            try:
                response = await call_next(request)
                status_code = response.status_code
                span.set_attribute("http.status_code", status_code)
                
                increment_request_counter(method, path, status_code)
                return response
            except Exception as e:
                # Record exception in span
                span.record_exception(e)
                span.set_status(status=2) # Error
                increment_request_counter(method, path, 500)
                raise e
            finally:
                duration = time.time() - start_time
                observe_request_duration(method, path, duration)
                track_in_flight(method, path, increment=False)

# Usage in main.py:
# app.add_middleware(ObservabilityMiddleware)
