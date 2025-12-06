import logging
import threading
from typing import Dict, Optional
from src.app.streaming.lifecycle import CancellationToken

logger = logging.getLogger(__name__)

class CancellationCoordinator:
    """
    Coordinates cancellation tokens for requests.
    Allows workers to check for cancellation and endpoints to trigger it.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._tokens: Dict[str, CancellationToken] = {}

    def get_or_create_token(self, request_id: str) -> CancellationToken:
        """
        Get existing token or create a new one for the request.
        """
        with self._lock:
            if request_id not in self._tokens:
                self._tokens[request_id] = CancellationToken()
            return self._tokens[request_id]

    def cancel(self, request_id: str) -> None:
        """
        Trigger cancellation for a request.
        """
        with self._lock:
            token = self._tokens.get(request_id)
            if token:
                token.cancel()
                logger.info(f"Cancelled request {request_id}")

    def wait_for_cancel(self, request_id: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for a request to be cancelled.
        Returns True if cancelled, False if timeout.
        
        Note:
            Workers typically poll `token.is_cancelled()` inside their loop 
            rather than blocking on this, but this is useful for control threads.
        """
        token = self.get_or_create_token(request_id)
        # Accessing the internal event for wait. 
        # In a cleaner design, CancellationToken might expose wait().
        return token._cancelled.wait(timeout=timeout)
