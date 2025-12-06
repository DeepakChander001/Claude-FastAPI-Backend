import logging
import time
from typing import Optional, Any, Callable
from fastapi import FastAPI, Response

logger = logging.getLogger(__name__)

# Global Metrics Placeholders
REQUEST_COUNTER: Any = None
REQUEST_DURATION: Any = None
IN_FLIGHT_REQUESTS: Any = None

# Global Tracer Placeholder
_TRACER: Any = None

# ------------------------------------------------------------------------
# No-Op Fallbacks
# ------------------------------------------------------------------------
class NoOpMetric:
    def inc(self, amount=1): pass
    def dec(self, amount=1): pass
    def set(self, value): pass
    def observe(self, value): pass
    def labels(self, *args, **kwargs): return self

class NoOpSpan:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def set_attribute(self, key, value): pass
    def set_status(self, status): pass
    def record_exception(self, exception): pass

class NoOpTracer:
    def start_as_current_span(self, name: str, **kwargs):
        return NoOpSpan()

# ------------------------------------------------------------------------
# Metrics Setup
# ------------------------------------------------------------------------
def setup_metrics(app: Optional[FastAPI] = None):
    """
    Initialize Prometheus metrics.
    If prometheus_client is installed, register metrics and mount /metrics endpoint.
    Otherwise, use no-op metrics.
    """
    global REQUEST_COUNTER, REQUEST_DURATION, IN_FLIGHT_REQUESTS

    try:
        from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
        
        REQUEST_COUNTER = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "path", "status"]
        )
        REQUEST_DURATION = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "path"]
        )
        IN_FLIGHT_REQUESTS = Gauge(
            "http_requests_in_flight",
            "Number of HTTP requests currently being processed",
            ["method", "path"]
        )
        
        if app:
            @app.get("/metrics")
            def metrics():
                return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
        
        logger.info("Prometheus metrics enabled.")

    except ImportError:
        logger.warning("prometheus_client not found. Using No-Op metrics.")
        REQUEST_COUNTER = NoOpMetric()
        REQUEST_DURATION = NoOpMetric()
        IN_FLIGHT_REQUESTS = NoOpMetric()

def increment_request_counter(method: str, path: str, status: int):
    if REQUEST_COUNTER:
        REQUEST_COUNTER.labels(method=method, path=path, status=str(status)).inc()

def observe_request_duration(method: str, path: str, duration: float):
    if REQUEST_DURATION:
        REQUEST_DURATION.labels(method=method, path=path).observe(duration)

def track_in_flight(method: str, path: str, increment: bool = True):
    if IN_FLIGHT_REQUESTS:
        metric = IN_FLIGHT_REQUESTS.labels(method=method, path=path)
        if increment:
            metric.inc()
        else:
            metric.dec()

# ------------------------------------------------------------------------
# Tracing Setup
# ------------------------------------------------------------------------
def setup_tracing(service_name: str, enabled: bool = False, exporter: Any = None):
    """
    Initialize OpenTelemetry tracing.
    """
    global _TRACER

    if not enabled:
        _TRACER = NoOpTracer()
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource
        
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        
        if exporter:
            # Use provided exporter (e.g., OTLP)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        else:
            # Default to Console/No-op for local dev if enabled but no exporter
            # For tests, we might want a SimpleSpanProcessor with InMemoryExporter, 
            # but here we'll just log.
            logger.info("Tracing enabled but no exporter provided.")
        
        trace.set_tracer_provider(provider)
        _TRACER = trace.get_tracer(service_name)
        logger.info(f"OpenTelemetry tracing enabled for {service_name}.")

    except ImportError:
        logger.warning("opentelemetry-sdk not found. Using No-Op tracer.")
        _TRACER = NoOpTracer()

def get_tracer():
    global _TRACER
    if _TRACER is None:
        _TRACER = NoOpTracer()
    return _TRACER

def trace_request(name: str):
    """Decorator to trace a function."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
