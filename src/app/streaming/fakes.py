import json
from collections import deque
from typing import Dict, Any, Iterator, List, Optional
from src.app.streaming.lifecycle import CancellationToken

class FakeBroker:
    """
    In-memory fake broker for testing.
    """
    def __init__(self):
        self.channels: Dict[str, deque] = {}

    def publish(self, channel: str, message: str) -> None:
        if channel not in self.channels:
            self.channels[channel] = deque()
        self.channels[channel].append(message)

    def subscribe(self, channel: str) -> Iterator[Dict[str, Any]]:
        if channel in self.channels:
            # Yield all currently queued messages
            while self.channels[channel]:
                msg_str = self.channels[channel].popleft()
                yield json.loads(msg_str)
        else:
            return

    def unsubscribe(self, channel: str) -> None:
        pass

class FakeAnthropicStreamer:
    """
    Fake Anthropic client that yields deterministic tokens.
    """
    def __init__(self, tokens: List[str]):
        self.tokens = tokens

    def stream_generate(self, prompt: str, model: str, **kwargs) -> Iterator[str]:
        for token in self.tokens:
            yield token

class FakeCancellationCoordinator:
    """
    Fake coordinator that returns tokens.
    """
    def __init__(self):
        self.tokens: Dict[str, CancellationToken] = {}

    def get_or_create_token(self, request_id: str) -> CancellationToken:
        if request_id not in self.tokens:
            self.tokens[request_id] = CancellationToken()
        return self.tokens[request_id]

    def cancel(self, request_id: str) -> None:
        if request_id in self.tokens:
            self.tokens[request_id].cancel()

class FakeStreamingWorker:
    """
    Fake worker that simulates processing.
    """
    def __init__(self, broker: Any, cancel_coord: Any):
        self.broker = broker
        self.cancel_coord = cancel_coord

    async def process_request(self, request_id: str, prompt: str, model: str, stream: bool = True):
        # Check cancellation
        token = self.cancel_coord.get_or_create_token(request_id)
        if token.is_cancelled():
            return

        # Simulate processing
        if "fail" in prompt:
            raise ValueError("Simulated failure")
            
        # Publish some chunks
        self.broker.publish(f"request:{request_id}", json.dumps({"type": "chunk", "content": "fake"}))
        self.broker.publish(f"request:{request_id}", json.dumps({"type": "chunk", "content": " response"}))
        self.broker.publish(f"request:{request_id}", json.dumps({"type": "done"}))
        
        yield "fake"
        yield " response"
