from decimal import Decimal
from typing import Optional, Dict, Any
from src.app.db import SupabaseClientWrapper

class RequestRepo:
    """
    Repository for managing request logs and usage data.
    """
    def __init__(self, db: SupabaseClientWrapper):
        self.db = db

    def create_request(self, prompt: str, model: str, stream: bool, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new request record.
        """
        return self.db.create_request(prompt, model, stream, user_id)

    def set_running(self, request_id: str) -> Dict[str, Any]:
        """
        Updates request status to 'running'.
        """
        return self.db.update_request_status(request_id, status="running")

    def set_done(self, request_id: str, output: str) -> Dict[str, Any]:
        """
        Updates request status to 'done', saves final output, and sets completion time.
        """
        # In a real app, we'd generate the timestamp here or let DB handle it.
        # For simplicity, we pass the output.
        return self.db.update_request_status(request_id, status="done", partial_output=output, completed_at="now()")

    def set_failed(self, request_id: str, reason: str) -> Dict[str, Any]:
        """
        Updates request status to 'failed' and logs the reason (as output).
        """
        return self.db.update_request_status(request_id, status="failed", partial_output=reason, completed_at="now()")

    def add_usage(self, request_id: str, tokens: int, cost: Decimal) -> Dict[str, Any]:
        """
        Records usage metrics for a request.
        """
        return self.db.record_usage(request_id, tokens, cost)

    def get_status(self, request_id: str) -> Dict[str, Any]:
        """
        Gets the current status of a request.
        """
        return self.db.get_request_status(request_id)
