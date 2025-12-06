import pytest
from fastapi.testclient import TestClient
from src.app.main import app
from src.app.client import AnthropicClientWrapper

@pytest.fixture
def test_client():
    """
    Fixture for FastAPI TestClient.
    """
    return TestClient(app)

@pytest.fixture
def mock_client():
    """
    Fixture for a mock AnthropicClientWrapper.
    """
    class MockClient:
        def generate_sync(self, prompt, model, max_tokens, temperature):
            return {
                "request_id": "mock-req-123",
                "output": f"MOCK RESPONSE: {prompt}",
                "model": model,
                "usage": {"input_tokens": 5, "output_tokens": 10},
                "warnings": []
            }
    return MockClient()
