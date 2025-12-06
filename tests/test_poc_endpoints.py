from src.app.dependencies import get_anthropic_client

def test_health_check(test_client):
    """
    Test GET /health endpoint.
    """
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_endpoint_mock(test_client, mock_client, monkeypatch):
    """
    Test POST /api/generate with a mock client.
    """
    # Override the dependency to return the mock client
    from src.app.main import app
    app.dependency_overrides[get_anthropic_client] = lambda: mock_client

    payload = {
        "prompt": "Test prompt",
        "model": "claude-3.5",
        "max_tokens": 100
    }
    
    response = test_client.post("/api/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "mock-req-123"
    assert "MOCK RESPONSE: Test prompt" in data["output"]
    assert data["model"] == "claude-3.5"
    
    # Clean up override
    app.dependency_overrides = {}
