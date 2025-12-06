import logging
import contextlib
import uuid
from typing import Optional, Dict, Any, Generator

logger = logging.getLogger(__name__)

# Try to import OpenTelemetry, fallback to shim if missing
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.propagate import inject, extract
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None

# ------------------------------------------------------------------------
# In-Memory Shim (for tests or when OTEL is disabled)
# ------------------------------------------------------------------------

class InMemorySpan:
    def __init__(self, name: str, context: Optional[Dict] = None):
        self.name = name
        self.context = context or {}
        self.attributes = {}
        self.status = "UNSET"
        self.trace_id = str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_id = None
        
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
        
    def set_status(self, status: Any):
        self.status = str(status)
        
    def record_exception(self, exception: Exception):
        self.attributes["exception.type"] = type(exception).__name__
        self.attributes["exception.message"] = str(exception)

    def get_span_context(self):
        return self

class InMemoryTracer:
    def __init__(self):
        self.spans = []
        
    @contextlib.contextmanager
    def start_as_current_span(self, name: str, context: Any = None, kind: Any = None):
        span = InMemorySpan(name, context)
        self.spans.append(span)
        try:
            yield span
        finally:
            pass # Span ended

    def start_span(self, name: str, context: Any = None):
        span = InMemorySpan(name, context)
        self.spans.append(span)
        return span

_IN_MEMORY_TRACER = InMemoryTracer()

# ------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------

def setup_tracing(service_name: str, enabled: bool = False, exporter_config: Optional[Dict] = None):
    """
    Configures OpenTelemetry if available and enabled.
    """
    if not enabled or not OTEL_AVAILABLE:
        logger.info("Tracing disabled or OTEL not installed. Using InMemoryShim.")
        return

    # Real OTEL Setup
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    # Exporter Setup (Guidance)
    # if exporter_config and exporter_config.get("type") == "otlp":
    #     from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    #     exporter = OTLPSpanExporter(endpoint=exporter_config["endpoint"])
    #     processor = BatchSpanProcessor(exporter)
    #     provider.add_span_processor(processor)
    
    # For now, we don't add a processor to avoid real network calls in this demo
    trace.set_tracer_provider(provider)
    logger.info(f"OpenTelemetry tracing enabled for {service_name}")

def get_tracer(name: str = "claude-proxy"):
    if OTEL_AVAILABLE and trace.get_tracer_provider():
        return trace.get_tracer(name)
    return _IN_MEMORY_TRACER

def inject_trace_context(headers: Dict[str, str], span: Any = None):
    """
    Injects trace context into headers.
    """
    if OTEL_AVAILABLE:
        inject(headers)
    else:
        # Simple shim injection
        if span and hasattr(span, "trace_id"):
            headers["x-trace-id"] = span.trace_id

def extract_trace_context(headers: Dict[str, str]):
    """
    Extracts trace context from headers.
    """
    if OTEL_AVAILABLE:
        return extract(headers)
    return None
