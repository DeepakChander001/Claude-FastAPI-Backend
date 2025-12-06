import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.app.logging.structured_logger import bind_logger
from src.app.tracing.otel_shim import get_tracer, inject_trace_context

logger = logging.getLogger(__name__)
tracer = get_tracer()

class LoggingTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"DEBUG: Middleware dispatching {request.url.path}")
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # 1. Start Span
        with tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind="SERVER"
        ) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("request_id", request_id)
            
            # 2. Attach Context to Request
            request.state.request_id = request_id
            request.state.trace_id = getattr(span, "trace_id", "unknown")
            request.state.span_id = getattr(span, "span_id", "unknown")
            
            # 3. Log Request Start (Debug)
            # logger.debug(f"Request started: {request.method} {request.url.path}", extra={"request_id": request_id})

            try:
                response = await call_next(request)
                
                # 4. Calculate Latency
                latency_ms = (time.time() - start_time) * 1000
                
                # 5. Log Structured Info
                log_extra = {
                    "request_id": request_id,
                    "trace_id": request.state.trace_id,
                    "span_id": request.state.span_id,
                    "route": request.url.path,
                    "latency_ms": latency_ms,
                    "status": response.status_code,
                    "method": request.method
                }
                
                # Use extra_data for our custom formatter
                logger.info(
                    f"Request processed: {response.status_code}", 
                    extra={"extra_data": log_extra}
                )
                
                span.set_attribute("http.status_code", response.status_code)
                
                return response
                
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Request failed: {str(e)}",
                    exc_info=True,
                    extra={
                        "extra_data": {
                            "request_id": request_id,
                            "trace_id": request.state.trace_id,
                            "route": request.url.path,
                            "latency_ms": latency_ms,
                            "status": 500
                        }
                    }
                )
                span.record_exception(e)
                span.set_status("ERROR")
                raise e

# Registration Snippet:
# app.add_middleware(LoggingTracingMiddleware)
