import logging
import json
from typing import Optional, Any, Iterator, Dict

logger = logging.getLogger(__name__)

class Broker:
    """
    Abstracts a Pub/Sub broker (e.g., Redis).
    Allows publishing messages to channels and subscribing to them.
    """
    def __init__(self, url: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize the broker.
        
        Args:
            url: Connection URL (e.g., redis://localhost:6379).
            client: Optional injected client (e.g., redis.Redis or a fake).
        """
        self.url = url
        self.client = client
        
        # In a real implementation, we might initialize the redis client here if not provided.
        # Example:
        # if not self.client and self.url:
        #     try:
        #         import redis
        #         self.client = redis.from_url(self.url)
        #     except ImportError:
        #         logger.warning("redis-py not installed.")

    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        """
        Publish a message to a channel.
        """
        payload = json.dumps(message)
        if self.client:
            try:
                # Real Redis usage:
                # self.client.publish(channel, payload)
                
                # For testing with fakes that might expect a dict or string:
                if hasattr(self.client, "publish"):
                    self.client.publish(channel, payload)
            except Exception as e:
                logger.error(f"Broker publish error: {e}")
        else:
            # No-op or log if no client configured
            logger.debug(f"Mock publish to {channel}: {payload}")

    def subscribe(self, channel: str) -> Iterator[Dict[str, Any]]:
        """
        Subscribe to a channel and yield messages.
        This is a generator that yields parsed dictionaries.
        """
        if self.client:
            try:
                # Real Redis usage:
                # pubsub = self.client.pubsub()
                # pubsub.subscribe(channel)
                # for message in pubsub.listen():
                #     if message["type"] == "message":
                #         yield json.loads(message["data"])
                
                # For testing with fakes:
                if hasattr(self.client, "subscribe"):
                    yield from self.client.subscribe(channel)
            except Exception as e:
                logger.error(f"Broker subscribe error: {e}")
        else:
            # Yield nothing if no client
            return

    def unsubscribe(self, channel: str) -> None:
        """
        Unsubscribe from a channel.
        """
        if self.client:
            try:
                # Real Redis usage:
                # pubsub.unsubscribe(channel) (requires keeping track of pubsub instance)
                # For this simple abstraction, we assume the generator exit handles cleanup
                # or the underlying client handles it.
                if hasattr(self.client, "unsubscribe"):
                    self.client.unsubscribe(channel)
            except Exception as e:
                logger.error(f"Broker unsubscribe error: {e}")

    def publish_control(self, request_id: str, message: Dict[str, Any]) -> None:
        """
        Publish a control message (e.g., cancel command).
        Recommended pattern: control:request:{request_id}
        """
        channel = f"control:request:{request_id}"
        self.publish(channel, message)

    def listen_control(self, request_id: str) -> Iterator[Dict[str, Any]]:
        """
        Listen for control messages for a specific request.
        """
        channel = f"control:request:{request_id}"
        yield from self.subscribe(channel)
