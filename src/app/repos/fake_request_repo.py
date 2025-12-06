from typing import Optional, Dict, Any
from datetime import datetime
from src.app.repos.request_repo import RequestRepo

class FakeRequestRepo(RequestRepo):
    """
    In-memory fake repository for testing.
    """
    def __init__(self):
        self.requests: Dict[str, Dict[str, Any]] = {}

    def create_request(self, request_id: str, user_id: Optional[str] = None, 
                      prompt: str = "", model: str = "") -> Dict[str, Any]:
        self.requests[request_id] = {
            "id": request_id,
            "user_id": user_id,
            "prompt": prompt,
            "model": model,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return self.requests[request_id]

    def update_request_status(self, request_id: str, status: str, 
                            error_message: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if request_id in self.requests:
            self.requests[request_id]["status"] = status
            self.requests[request_id]["updated_at"] = datetime.now()
            if error_message:
                self.requests[request_id]["error_message"] = error_message
            return self.requests[request_id]
        return None

    def record_usage(self, request_id: str, prompt_tokens: int, 
                    completion_tokens: int, cost: float) -> Optional[Dict[str, Any]]:
        if request_id in self.requests:
            self.requests[request_id]["prompt_tokens"] = prompt_tokens
            self.requests[request_id]["completion_tokens"] = completion_tokens
            self.requests[request_id]["cost"] = cost
            return self.requests[request_id]
        return None

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        return self.requests.get(request_id)
