import pytest
import logging
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.app.middleware.logging_tracing_middleware import LoggingTracingMiddleware
from src.app.logging.structured_logger import configure_logging
from src.app.tracing.otel_shim import get_tracer

# Setup App
app = FastAPI()
app.add_middleware(LoggingTracingMiddleware)

@app.get("/test-log")
def endpoint_log():
    return {"message": "hello"}

@app.get("/test-error")
def endpoint_error():
    raise ValueError("Simulated error")

class CapturingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.records.append(json.loads(msg))
        except Exception:
            self.records.append(record)

@pytest.fixture
def capture_logs():
    configure_logging(json_format=True)
    # Attach to the specific logger used in middleware
    logger = logging.getLogger("src.app.middleware.logging_tracing_middleware")
    logger.setLevel(logging.INFO)
    
    handler = CapturingHandler()
    
    # IMPORTANT: Set the formatter so self.format(record) produces JSON
    from src.app.logging.structured_logger import StructuredFormatter
    handler.setFormatter(StructuredFormatter())
    
    logger.addHandler(handler)
    # Also attach to root to be safe
    root = logging.getLogger()
    root.addHandler(handler)
    
    yield handler
    
    logger.removeHandler(handler)
    root.removeHandler(handler)

def test_request_logging_correlation(capture_logs):
    client = TestClient(app)
    response = client.get("/test-log")
    assert response.status_code == 200
    
    # Verify Logs
    # Filter for our specific log message to avoid noise
    logs = [r for r in capture_logs.records if isinstance(r, dict) and r.get("route") == "/test-log"]
    
    if not logs:
        print("\nCaptured Records:", capture_logs.records)
        
    assert len(logs) >= 1
    log_entry = logs[0]
    
    # Check Fields
    assert "request_id" in log_entry
    assert "trace_id" in log_entry
    assert "latency_ms" in log_entry
    assert log_entry["status"] == 200
    assert log_entry["service"] == "claude-proxy"

def test_error_logging_correlation(capture_logs):
    # Prevent TestClient from re-raising the exception so we can verify the 500 response and logs
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test-error")
    assert response.status_code == 500
        
    # Verify Logs
    logs = [r for r in capture_logs.records if isinstance(r, dict) and r.get("route") == "/test-error"]
    
    if not logs:
        print("\nCaptured Records:", capture_logs.records)

    assert len(logs) >= 1
    log_entry = logs[0]
    
    assert log_entry["level"] == "ERROR"
    assert log_entry["status"] == 500
    assert "Simulated error" in log_entry["message"] or "Simulated error" in str(log_entry)

def test_tracer_capture():
    tracer = get_tracer()
    with tracer.start_as_current_span("test-span") as span:
        span.set_attribute("foo", "bar")
        
    # Since we use InMemoryShim by default in tests (OTEL not installed/mocked)
    # We can inspect the shim if we exposed it. 
    # But for now, just ensuring it doesn't crash is the baseline.
    assert span is not None
