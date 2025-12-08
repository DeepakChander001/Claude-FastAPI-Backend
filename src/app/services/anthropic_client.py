import uuid
import anthropic
from typing import Dict, Any, Protocol, Iterator, Generator
from src.app.config import Settings

class AnthropicClientProtocol(Protocol):
    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        ...
    
    def stream_generate(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Generator[str, None, None]:
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
    
    def stream_generate(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Generator[str, None, None]:
        """Mock streaming - yields word by word."""
        import time
        mock_response = f"This is a mock streaming response to your prompt about: {prompt[:30]}..."
        words = mock_response.split()
        for word in words:
            time.sleep(0.1)  # Simulate delay
            yield word + " "

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
            raise e
        except Exception as e:
            raise e

    def stream_generate(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Generator[str, None, None]:
        """
        Stream tokens from Anthropic API.
        Yields text chunks as they arrive.
        """
        try:
            with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except anthropic.APIError as e:
            yield f"\n\n[Error: {str(e)}]"
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"

