import uuid
import anthropic
import openai
from typing import Dict, Any, Protocol, Iterator, Generator
from src.app.config import Settings

class AnthropicClientProtocol(Protocol):
    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float, tools: list = None) -> Dict[str, Any]:
        ...
    
    def stream_generate(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Generator[str, None, None]:
        ...

class MockAnthropicClient:
    """
    Mock client for local development and testing.
    """
    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float, tools: list = None) -> Dict[str, Any]:
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
    Supports both native Anthropic and OpenRouter (via OpenAI SDK).
    """
    def __init__(self, api_key: str, base_url: str = None):
        self.base_url = base_url
        self.api_key = api_key
        
        # Detect Client Type
        if base_url and "openrouter" in base_url:
            self.client_type = "openai"
            self.client = openai.OpenAI(
                api_key=api_key, 
                base_url=base_url
            )
        else:
            self.client_type = "anthropic"
            self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

    def _map_model(self, model: str) -> str:
        """
        Map model names for specific providers.
        """
        if self.base_url and "openrouter" in self.base_url:
            # Force DeepSeek Chat (V2.5/V3) as it includes coding & reasoning
            return "deepseek/deepseek-chat"
            
        if self.base_url and "z.ai" in self.base_url:
            return "GLM-4.6"
            
        return model

    def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float, tools: list = None) -> Dict[str, Any]:
        target_model = self._map_model(model)
        
        # === OpenAI SDK (OpenRouter) ===
        if self.client_type == "openai":
            try:
                # Prepare args
                kwargs = {
                    "model": target_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = self.client.chat.completions.create(**kwargs)
                
                message = response.choices[0].message
                content = message.content
                tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None
                
                return {
                    "request_id": response.id,
                    "output": content,
                    "model": response.model,
                    "tool_calls": tool_calls, # Pass raw tool calls back
                    "usage": {"input_tokens": 0, "output_tokens": 0}, 
                    "warnings": []
                }
            except Exception as e:
                raise e

        # === Anthropic SDK (Native/Z.AI) ===
        try:
            # Note: Tool use logic for Native Anthropic is slightly different
            # We are prioritizing OpenRouter for now.
            response = self.client.messages.create(
                model=target_model,
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
        target_model = self._map_model(model)
        
        # === OpenAI SDK (OpenRouter) ===
        if self.client_type == "openai":
            try:
                stream = self.client.chat.completions.create(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                yield f"\n\n[Error: {str(e)}]"
            return

        # === Anthropic SDK (Native/Z.AI) ===
        try:
            with self.client.messages.stream(
                model=target_model,
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

