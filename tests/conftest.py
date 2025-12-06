import pytest
import os
from fastapi.testclient import TestClient
from src.app.main import app
from src.app.services.anthropic_client import MockAnthropicClient

@pytest.fixture
def test_client():
    """
    Fixture for FastAPI TestClient.
    """
    return TestClient(app)

@pytest.fixture
def mock_client():
    """
    Fixture for a mock AnthropicClientProtocol.
    """
    class MockClient:
        def generate_text(self, prompt, model, max_tokens, temperature):
            return {
                "request_id": "mock-req-123",
                "output": f"MOCK RESPONSE: {prompt}",
                "model": model,
                "usage": {"input_tokens": 5, "output_tokens": 10},
                "warnings": []
            }
    return MockClient()

@pytest.fixture(autouse=True)
def force_mock_env():
    """
    Ensure USE_MOCK_CLIENT is True for all tests.
    """
    os.environ["USE_MOCK_CLIENT"] = "true"
    yield
    # Cleanup if necessary, though os.environ changes might persist in the process
