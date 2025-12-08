import logging
import decimal
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class SupabaseClientWrapper:
    """
    Wrapper for Supabase client operations.
    Encapsulates database interactions for request logging and usage tracking.
    """
    def __init__(self, url: str, key: str, client: Optional[Any] = None):
        """
        Initialize the wrapper.
        
        Args:
            url: Supabase URL.
            key: Supabase API Key.
            client: Optional pre-configured client (useful for testing).
        """
        self.url = url
        self.key = key
        self.client = client

        if self.client is None and url and key and url != "REPLACE_ME":
            try:
                from supabase import create_client, Client
                self.client: Client = create_client(url, key)
                logger.info("Supabase client initialized successfully")
            except ImportError:
                logger.warning("supabase-py not installed. Cannot connect to real database.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")

    def create_request(self, prompt: str, model: str, stream: bool, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new request log entry.
        """
        data = {
            "prompt": prompt,
            "model": model,
            "stream": stream,
            "user_id": user_id,
            "status": "queued"
        }
        
        if self.client:
            try:
                # Real client usage:
                # response = self.client.table("request_logs").insert(data).execute()
                # return response.data[0]
                
                # Mock client usage (for tests):
                return self.client.table("request_logs").insert(data).execute().data[0]
            except Exception as e:
                logger.error(f"DB Error create_request: {e}")
                return {}
        
        # Fallback if no client
        return {"id": "fallback-id", "created_at": "now"}

    def update_request_status(
        self, 
        request_id: str, 
        status: str, 
        partial_output: Optional[str] = None, 
        completed_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates the status and output of a request.
        """
        data = {"status": status}
        if partial_output is not None:
            data["partial_output"] = partial_output
        if completed_at is not None:
            data["completed_at"] = completed_at

        if self.client:
            try:
                # Real client usage:
                # response = self.client.table("request_logs").update(data).eq("id", request_id).execute()
                # return response.data[0]
                
                return self.client.table("request_logs").update(data).eq("id", request_id).execute().data[0]
            except Exception as e:
                logger.error(f"DB Error update_request_status: {e}")
                return {}
        return {}

    def record_usage(self, request_id: str, tokens: int, cost: decimal.Decimal) -> Dict[str, Any]:
        """
        Records token usage and cost for a request.
        """
        data = {
            "request_id": request_id,
            "tokens": tokens,
            "cost": float(cost) # Supabase/JSON handles floats better than Decimal usually
        }
        
        if self.client:
            try:
                return self.client.table("usage").insert(data).execute().data[0]
            except Exception as e:
                logger.error(f"DB Error record_usage: {e}")
                return {}
        return {}

    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Retrieves the current status of a request.
        """
        if self.client:
            try:
                # Real client usage:
                # response = self.client.table("request_logs").select("*").eq("id", request_id).execute()
                # return response.data[0] if response.data else {}
                
                response = self.client.table("request_logs").select("*").eq("id", request_id).execute()
                return response.data[0] if response.data else {}
            except Exception as e:
                logger.error(f"DB Error get_request_status: {e}")
                return {}
        return {}
