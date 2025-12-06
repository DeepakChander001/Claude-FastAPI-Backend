import json
import logging
import uuid
from typing import Iterator
from fastapi import Depends
from fastapi.responses import StreamingResponse
from src.app.streaming.broker import Broker
from src.app.streaming.lifecycle import ConnectionManager
from src.app.streaming.cancellation import CancellationCoordinator

# Global Singletons (In a real app, use dependency injection framework)
_connection_manager = ConnectionManager()
_cancellation_coordinator = CancellationCoordinator()

def get_broker() -> Broker:
    return Broker()

def get_connection_manager() -> ConnectionManager:
    return _connection_manager

def get_cancellation_coordinator() -> CancellationCoordinator:
    return _cancellation_coordinator

logger = logging.getLogger(__name__)

def sse_stream(
    request_id: str, 
    broker: Broker = Depends(get_broker),
    conn_manager: ConnectionManager = Depends(get_connection_manager),
    cancel_coord: CancellationCoordinator = Depends(get_cancellation_coordinator)
) -> StreamingResponse:
    """
    SSE Endpoint that subscribes to a request channel and streams events to the client.
    Handles lifecycle registration and cancellation on disconnect.
    """
    channel = f"request:{request_id}"
    connection_id = str(uuid.uuid4())
    
    def event_generator() -> Iterator[str]:
        try:
            # Register connection
            conn_manager.register(request_id, connection_id)
            
            # Subscribe to the broker channel
            for message in broker.subscribe(channel):
                yield f"data: {json.dumps(message)}\n\n"
                
                # Stop stream if we see a terminal message
                msg_type = message.get("type")
                if msg_type in ("done", "error", "cancelled"):
                    break
                    
        except Exception as e:
            logger.error(f"SSE stream error for {request_id}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            # Cleanup
            broker.unsubscribe(channel)
            conn_manager.unregister(request_id, connection_id)
            
            # Check if we should cancel the backend work
            if conn_manager.cancel_request_if_no_subscribers(request_id):
                cancel_coord.cancel(request_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
