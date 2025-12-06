import pytest
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.app.streaming.broker import Broker
from src.app.streaming.worker import StreamingWorker
from src.app.streaming.sse_endpoint import sse_stream, get_broker, get_connection_manager, get_cancellation_coordinator
from src.app.streaming.fakes import FakeBroker, FakeAnthropicStreamer
from src.app.streaming.lifecycle import ConnectionManager, CancellationToken
from src.app.streaming.cancellation import CancellationCoordinator

def test_connection_manager_lifecycle():
    """
    Test registration and unregistration logic.
    """
    cm = ConnectionManager()
    req_id = "req-1"
    conn_id = "conn-1"
    
    cm.register(req_id, conn_id)
    assert cm.active_subscribers(req_id) == 1
    
    cm.unregister(req_id, conn_id)
    assert cm.active_subscribers(req_id) == 0
    assert cm.cancel_request_if_no_subscribers(req_id) is True

def test_worker_cancellation():
    """
    Test that worker respects cancellation token.
    """
    fake_backend = FakeBroker()
    broker = Broker(client=fake_backend)
    streamer = FakeAnthropicStreamer(tokens=["A", "B", "C"])
    worker = StreamingWorker(broker, streamer)
    
    token = CancellationToken()
    req_id = "req-cancel"
    
    # Cancel immediately
    token.cancel()
    
    result = worker.handle_request(req_id, "prompt", cancellation_token=token)
    
    assert result["status"] == "cancelled"
    
    # Verify cancelled message in broker
    channel = f"request:{req_id}"
    messages = list(fake_backend.subscribe(channel))
    assert len(messages) == 1
    assert messages[0]["type"] == "cancelled"

def test_worker_backpressure_hint():
    """
    Test that worker adds backpressure hints for long sequences.
    """
    fake_backend = FakeBroker()
    broker = Broker(client=fake_backend)
    # 60 tokens to trigger 'high' backpressure
    tokens = ["x"] * 60
    streamer = FakeAnthropicStreamer(tokens=tokens)
    worker = StreamingWorker(broker, streamer)
    
    worker.handle_request("req-bp", "prompt")
    
    channel = "request:req-bp"
    messages = list(fake_backend.subscribe(channel))
    
    # Check early message (low)
    assert messages[0]["backpressure"] == "low"
    # Check middle message (medium)
    assert messages[25]["backpressure"] == "medium"
    # Check late message (high)
    assert messages[55]["backpressure"] == "high"

def test_sse_endpoint_disconnect_triggers_cancel():
    """
    Test that disconnecting from SSE endpoint triggers cancellation.
    """
    app = FastAPI()
    
    fake_backend = FakeBroker()
    broker = Broker(client=fake_backend)
    conn_manager = ConnectionManager()
    cancel_coord = CancellationCoordinator()
    
    app.dependency_overrides[get_broker] = lambda: broker
    app.dependency_overrides[get_connection_manager] = lambda: conn_manager
    app.dependency_overrides[get_cancellation_coordinator] = lambda: cancel_coord
    
    app.get("/stream/{request_id}")(sse_stream)
    
    client = TestClient(app)
    req_id = "req-disconnect"
    
    # Pre-populate some data so we can connect
    channel = f"request:{req_id}"
    fake_backend.publish(channel, json.dumps({"type": "chunk", "token": "A"}))
    
    # Ensure token exists before we try to cancel it
    cancel_coord.get_or_create_token(req_id)
    
    # Connect and consume partially
    with client.stream("GET", f"/stream/{req_id}") as response:
        # Read one event
        next(response.iter_lines())
        # Exit context manager simulates disconnect
        
    # Assert cancellation was triggered
    # Since SSE runs in a thread, we need to wait briefly for cleanup
    import time
    token = cancel_coord.get_or_create_token(req_id)
    for _ in range(10):
        if token.is_cancelled():
            break
        time.sleep(0.05)
    
    assert token.is_cancelled() is True
