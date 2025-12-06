from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Client(BaseModel):
    """
    Represents an authenticated client.
    """
    id: str
    plan: str = "free"
    scopes: list[str] = Field(default_factory=list)

class AuthError(BaseModel):
    """
    Standard error response for authentication failures.
    """
    detail: str

class RequestAudit(BaseModel):
    """
    Structured audit log entry.
    """
    timestamp: datetime
    client_id: Optional[str]
    method: str
    path: str
    status_code: int
    duration_ms: float
    ip_address: Optional[str]
    user_agent: Optional[str]
