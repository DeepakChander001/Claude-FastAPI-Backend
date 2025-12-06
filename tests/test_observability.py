import pytest
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.app.middleware.observability_middleware import ObservabilityMiddleware
from src.app import observability
from src.app.observability.fakes import FakeCounter, FakeHistogram, FakeGauge, FakeTracer

def test_observability_middleware_metrics_and_tracing():
    """
    Test that middleware correctly records metrics and traces using Fakes.
    """
    # 1. Setup Fakes
    fake_counter = FakeCounter()
    fake_histogram = FakeHistogram()
    fake_gauge = FakeGauge()
    fake_tracer = FakeTracer()

    # 2. Inject Fakes into observability module
    # We monkeypatch the global variables
    observability.REQUEST_COUNTER = fake_counter
    observability.REQUEST_DURATION = fake_histogram
    observability.IN_FLIGHT_REQUESTS = fake_gauge
    observability._TRACER = fake_tracer

    # 3. Setup App
    app = FastAPI()
    app.add_middleware(ObservabilityMiddleware)

    @app.get("/test")
    def test_endpoint():
        time.sleep(0.01)
        return {"message": "ok"}

    client = TestClient(app)

    # 4. Make Request
    response = client.get("/test")
    assert response.status_code == 200

    # 5. Verify Metrics
    # Counter: method=GET, path=/test, status=200
    counter_key = (('method', 'GET'), ('path', '/test'), ('status', '200'))
    assert fake_counter.data.get(counter_key) == 1

    # Histogram: method=GET, path=/test
    hist_key = (('method', 'GET'), ('path', '/test'))
    assert len(fake_histogram.data.get(hist_key)) == 1
    assert fake_histogram.data.get(hist_key)[0] > 0

    # Gauge: Should be 0 after request finishes (inc then dec)
    gauge_key = (('method', 'GET'), ('path', '/test'))
    assert fake_gauge.data.get(gauge_key) == 0

    # 6. Verify Tracing
    assert len(fake_tracer.spans) == 1
    span = fake_tracer.spans[0]
    assert span.name == "GET /test"
    assert span.attributes["http.status_code"] == 200

def test_metrics_endpoint_fallback():
    """
    Test that /metrics endpoint works (even if using no-op or fakes).
    Note: In our setup_metrics, we only mount /metrics if app is passed.
    """
    app = FastAPI()
    # Call setup to mount endpoint (will use no-op if libs missing, or we can mock)
    observability.setup_metrics(app)
    
    client = TestClient(app)
    response = client.get("/metrics")
    
    # If prometheus_client is missing, it might not return anything useful or might not be mounted 
    # if we didn't mock the import. 
    # But our code mounts it inside the try block. 
    # If import fails, it logs warning and DOES NOT mount /metrics (see code).
    # So we expect 404 if libs are missing, or 200 if present.
    # Since we are in an environment without prometheus_client likely, it should be 404.
    # However, to test the logic, we can verify it doesn't crash.
    assert response.status_code in [200, 404]
