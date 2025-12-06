from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    """Request model for generating text via Claude."""
    prompt: str = Field(..., description="The input prompt for generation.")
    model: Optional[str] = Field("claude-3-haiku-20240307", description="The model version to use.")
    stream: bool = Field(False, description="Whether to stream the response.")
    max_tokens: Optional[int] = Field(800, description="Maximum tokens to generate.")
    temperature: float = Field(0.0, description="Sampling temperature.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the request.")

class GenerateResponse(BaseModel):
    """Response model for a completed generation request."""
    request_id: str = Field(..., description="Unique identifier for the request.")
    output: str = Field(..., description="The generated text output.")
    model: str = Field(..., description="The model used for generation.")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage statistics.")
    warnings: Optional[List[str]] = Field(None, description="Any warnings returned by the provider.")

class StatusResponse(BaseModel):
    """Response model for checking the status of an asynchronous request."""
    request_id: str = Field(..., description="Unique identifier for the request.")
    status: str = Field(..., description="Current status: queued, running, done, or failed.")
    created_at: str = Field(..., description="ISO 8601 timestamp of creation.")
    completed_at: Optional[str] = Field(None, description="ISO 8601 timestamp of completion.")
    partial_output: Optional[str] = Field(None, description="Partial output if available/streaming.")
