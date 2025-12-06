import pytest
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.app.streaming.broker import Broker
from src.app.streaming.worker import StreamingWorker
from src.app.streaming.sse_endpoint import sse_stream, get_broker
from src.app.streaming.fakes import FakeBroker, FakeAnthropicStreamer

def test_streaming_worker_flow():
    """
    Test that StreamingWorker publishes expected messages to the broker.
    """
    # Setup fakes
    fake_backend = FakeBroker()
    broker = Broker(client=fake_backend)
    streamer = FakeAnthropicStreamer(tokens=["Hello", " ", "World"])
    worker = StreamingWorker(broker, streamer)
    
    # Run worker
    request_id = "req-123"
    worker.handle_request(request_id, "prompt")
    
    # Verify messages in broker
    channel = f"request:{request_id}"
    assert channel in fake_backend.channels
    messages = list(fake_backend.subscribe(channel))
    
    # Expect 3 chunks + 1 done
    assert len(messages) == 4
    assert messages[0]["type"] == "chunk"
    assert messages[0]["token"] == "Hello"
    assert messages[1]["token"] == " "
    assert messages[2]["token"] == "World"
    assert messages[3]["type"] == "done"
    assert messages[3]["final"] == "Hello World"

def test_sse_endpoint_flow():
    """
    Test that sse_stream endpoint yields SSE formatted events from the broker.
    """
    # Setup app and dependency override
    app = FastAPI()
    
    # Pre-populate a fake broker with messages
    fake_backend = FakeBroker()
    # Manually inject messages as if worker ran
    channel = "request:req-sse"
    fake_backend.publish(channel, json.dumps({"type": "chunk", "token": "A"}))
    fake_backend.publish(channel, json.dumps({"type": "done", "final": "A"}))
    
    broker = Broker(client=fake_backend)
    
    app.dependency_overrides[get_broker] = lambda: broker
    app.get("/stream/{request_id}")(sse_stream)
    
    client = TestClient(app)
    
    # Request stream
    response = client.get("/stream/req-sse")
    assert response.status_code == 200
    content = response.text
    
    # Verify SSE format
    assert "data: " in content
    assert '{"type": "chunk", "token": "A"}' in content
    assert '{"type": "done", "final": "A"}' in content
