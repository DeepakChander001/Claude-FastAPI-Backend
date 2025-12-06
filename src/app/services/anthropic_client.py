import uuid
import anthropic
from typing import Dict, Any, Protocol
from src.app.config import Settings

class AnthropicClientProtocol(Protocol):
    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        ...

class MockAnthropicClient:
    """
    Mock client for local development and testing.
    """
    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        return {
            "request_id": f"local-{uuid.uuid4()}",
            "output": f"MOCK: {prompt[:50]}..." if len(prompt) > 50 else f"MOCK: {prompt}",
            "model": model,
            "usage": {"input_tokens": 10, "output_tokens": 20},
            "warnings": ["This is a mock response."]
        }

class RealAnthropicClient:
    """
    Real client wrapper for Anthropic API.
    """
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "request_id": response.id,
                "output": response.content[0].text,
                "model": response.model,
                "usage": response.usage.model_dump(),
                "warnings": []
            }
        except anthropic.APIError as e:
            # In a real app, we might want to map these to specific HTTP exceptions
            # or let the caller handle them.
            raise e
        except Exception as e:
            raise e
