import pytest
from src.app.models import GenerateRequest, GenerateResponse, StatusResponse

def test_generate_request_serialization():
    """Test that GenerateRequest can be instantiated and serialized to JSON."""
    req = GenerateRequest(
        prompt="Hello",
        model="claude-3.5",
        stream=False,
        max_tokens=100,
        temperature=0.5,
        metadata={"user_id": "123"}
    )
    json_output = req.model_dump_json()
    assert "Hello" in json_output
    assert "claude-3.5" in json_output

def test_generate_response_serialization():
    """Test that GenerateResponse can be instantiated and serialized to JSON."""
    res = GenerateResponse(
        request_id="req_test",
        output="World",
        model="claude-3.5",
        usage={"input": 10, "output": 5}
    )
    json_output = res.model_dump_json()
    assert "req_test" in json_output
    assert "World" in json_output

def test_status_response_serialization():
    """Test that StatusResponse can be instantiated and serialized to JSON."""
    stat = StatusResponse(
        request_id="req_test",
        status="running",
        created_at="2023-01-01T00:00:00Z"
    )
    json_output = stat.model_dump_json()
    assert "running" in json_output
