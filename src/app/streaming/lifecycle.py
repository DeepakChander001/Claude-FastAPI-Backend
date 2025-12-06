import logging
import threading
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)

class CancellationToken:
    """
    A simple thread-safe token to signal cancellation.
    """
    def __init__(self):
        self._cancelled = threading.Event()

    def cancel(self) -> None:
        """Signal cancellation."""
        self._cancelled.set()

    def is_cancelled(self) -> bool:
        """Check if cancellation has been signaled."""
        return self._cancelled.is_set()

class ConnectionManager:
    """
    Manages active client connections for streaming requests.
    
    Thread-Safety:
        Uses a Lock to protect the internal mapping of request_id to connection_ids.
    
    Production Note:
        In a distributed environment (multiple API replicas), this in-memory manager
        would need to be replaced by a shared store like Redis Sets with TTLs 
        to track active subscribers globally.
    """
    def __init__(self):
        self._lock = threading.Lock()
        # Mapping: request_id -> Set[connection_id]
        self._connections: Dict[str, Set[str]] = {}

    def register(self, request_id: str, connection_id: str) -> None:
        """Register a new connection for a request."""
        with self._lock:
            if request_id not in self._connections:
                self._connections[request_id] = set()
            self._connections[request_id].add(connection_id)
            logger.debug(f"Registered conn {connection_id} for req {request_id}")

    def unregister(self, request_id: str, connection_id: str) -> None:
        """Unregister a connection."""
        with self._lock:
            if request_id in self._connections:
                self._connections[request_id].discard(connection_id)
                if not self._connections[request_id]:
                    del self._connections[request_id]
                logger.debug(f"Unregistered conn {connection_id} for req {request_id}")

    def active_subscribers(self, request_id: str) -> int:
        """Return the count of active subscribers for a request."""
        with self._lock:
            return len(self._connections.get(request_id, set()))

    def cancel_request_if_no_subscribers(self, request_id: str) -> bool:
        """
        Checks if there are no active subscribers.
        Returns True if the request should be cancelled.
        """
        count = self.active_subscribers(request_id)
        if count == 0:
            logger.info(f"No subscribers for {request_id}. Recommending cancellation.")
            return True
        return False
