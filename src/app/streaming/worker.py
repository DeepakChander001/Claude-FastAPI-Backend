import logging
import time
from typing import Any, Dict, Optional
from src.app.streaming.broker import Broker

logger = logging.getLogger(__name__)

class StreamingWorker:
    """
    Worker that handles generation requests, streams tokens from Anthropic,
    and publishes them to the Broker.
    """
    def __init__(self, broker: Broker, anthropic_client: Any, model: str = "claude-3.5"):
        self.broker = broker
        self.client = anthropic_client
        self.model = model

    def handle_request(
        self, 
        request_id: str, 
        prompt: str, 
        cancellation_token: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a generation request.
        
        Args:
            request_id: Unique ID for the request.
            prompt: The input prompt.
            cancellation_token: Optional CancellationToken to check for abort signals.
            **kwargs: Additional generation parameters.
            
        Returns:
            Summary dictionary.
        """
        channel = f"request:{request_id}"
        full_text = []
        
        try:
            # We assume the injected client has a 'stream_generate' method or similar
            if hasattr(self.client, "stream_generate"):
                stream = self.client.stream_generate(prompt=prompt, model=self.model, **kwargs)
            else:
                logger.warning("Client does not support stream_generate. Using mock stream.")
                stream = ["Mock", " ", "stream", " ", "response"]

            seq = 0
            for token in stream:
                # Check cancellation
                if cancellation_token and cancellation_token.is_cancelled():
                    logger.info(f"Worker detected cancellation for {request_id}")
                    self.broker.publish(channel, {
                        "type": "cancelled",
                        "request_id": request_id
                    })
                    return {"request_id": request_id, "status": "cancelled"}

                seq += 1
                
                # Naive backpressure hint
                # In a real system, we might check broker queue depth or client ack rate.
                # Here we just simulate it based on sequence number for demonstration.
                backpressure_hint = "low"
                if seq > 50:
                    backpressure_hint = "high"
                elif seq > 20:
                    backpressure_hint = "medium"

                message = {
                    "type": "chunk",
                    "token": token,
                    "seq": seq,
                    "request_id": request_id,
                    "backpressure": backpressure_hint
                }
                self.broker.publish(channel, message)
                full_text.append(token)
            
            # Publish done message
            final_output = "".join(full_text)
            self.broker.publish(channel, {
                "type": "done",
                "request_id": request_id,
                "final": final_output
            })
            
            return {"request_id": request_id, "status": "done", "output_length": len(final_output)}

        except Exception as e:
            logger.error(f"Streaming error for {request_id}: {e}")
            self.broker.publish(channel, {
                "type": "error",
                "request_id": request_id,
                "error": str(e)
            })
            return {"request_id": request_id, "status": "failed", "error": str(e)}
