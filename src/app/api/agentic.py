"""
Agentic API - Endpoints for tool use with human-in-the-loop confirmation.

This implements the Claude Code-like experience where:
1. User sends a request
2. AI proposes actions (create file, run command, etc.)
3. User approves/rejects the actions
4. System executes approved actions
5. AI continues with the results
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid

from src.app.config import Settings
from src.app.dependencies import get_settings
from src.app.tools import ToolExecutor, ToolType, ToolProposal, ToolResult
from src.app.services.agentic_client import AgenticAnthropicClient


router = APIRouter(prefix="/api/agent", tags=["agent"])


# Request/Response Models
class AgentRequest(BaseModel):
    """Request for agentic interaction."""
    prompt: str = Field(..., description="The user's request")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    max_tokens: int = Field(1024, description="Maximum tokens in response")
    working_directory: str = Field(".", description="Base directory for file operations")


class AgentResponse(BaseModel):
    """Response from agentic interaction."""
    session_id: str
    response_text: str
    tool_proposals: List[Dict[str, Any]] = Field(default_factory=list)
    requires_confirmation: bool = False
    message: str = ""


class ToolApproval(BaseModel):
    """User's approval/rejection of tool proposals."""
    session_id: str
    approvals: List[Dict[str, Any]] = Field(..., description="List of {tool_id, approved} objects")


class ToolExecutionResult(BaseModel):
    """Result after executing approved tools."""
    session_id: str
    results: List[Dict[str, Any]]
    response_text: str = ""
    tool_proposals: List[Dict[str, Any]] = Field(default_factory=list)
    requires_confirmation: bool = False


# In-memory session storage (use Redis in production)
_sessions: Dict[str, Dict[str, Any]] = {}


def get_agentic_client(settings: Settings = Depends(get_settings)) -> AgenticAnthropicClient:
    """Get the agentic client."""
    if settings.USE_MOCK_CLIENT or not settings.ANTHROPIC_API_KEY:
        # Return a simple mock for testing
        return None
    return AgenticAnthropicClient(
        api_key=settings.ANTHROPIC_API_KEY,
        model=settings.DEFAULT_MODEL
    )


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(
    request: AgentRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Start or continue an agentic conversation.
    
    The AI may propose tool actions that require your confirmation.
    If `requires_confirmation` is True, you must call `/api/agent/confirm` 
    with your approvals before the actions are executed.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    # Check if using mock mode
    if settings.USE_MOCK_CLIENT or not settings.ANTHROPIC_API_KEY:
        # Mock response for testing
        mock_proposals = []
        
        # Simulate tool proposals based on keywords
        if "create" in request.prompt.lower() and "file" in request.prompt.lower():
            mock_proposals.append({
                "tool_id": str(uuid.uuid4()),
                "tool_type": "create_file",
                "description": "Create file: example.py",
                "parameters": {"path": "example.py", "content": "# Example file\nprint('Hello!')"},
                "requires_confirmation": True,
                "risk_level": "medium"
            })
        
        if "run" in request.prompt.lower() or "command" in request.prompt.lower():
            mock_proposals.append({
                "tool_id": str(uuid.uuid4()),
                "tool_type": "run_command",
                "description": "Run command: echo 'Hello World'",
                "parameters": {"command": "echo 'Hello World'"},
                "requires_confirmation": True,
                "risk_level": "high"
            })
        
        # Store session
        _sessions[session_id] = {
            "prompt": request.prompt,
            "tool_proposals": mock_proposals,
            "working_directory": request.working_directory
        }
        
        return AgentResponse(
            session_id=session_id,
            response_text="I understand your request. Here are the actions I'd like to perform:",
            tool_proposals=mock_proposals,
            requires_confirmation=len(mock_proposals) > 0,
            message="Please approve or reject the proposed actions using /api/agent/confirm"
        )
    
    # Real client
    client = AgenticAnthropicClient(
        api_key=settings.ANTHROPIC_API_KEY,
        model=settings.DEFAULT_MODEL
    )
    
    result = client.generate_with_tools(
        prompt=request.prompt,
        max_tokens=request.max_tokens
    )
    
    # Store session
    _sessions[session_id] = {
        "prompt": request.prompt,
        "tool_proposals": result.get("tool_proposals", []),
        "working_directory": request.working_directory,
        "messages": [{"role": "user", "content": request.prompt}]
    }
    
    return AgentResponse(
        session_id=session_id,
        response_text=result.get("response_text", ""),
        tool_proposals=result.get("tool_proposals", []),
        requires_confirmation=result.get("requires_confirmation", False),
        message="Approve actions using /api/agent/confirm" if result.get("requires_confirmation") else ""
    )


@router.post("/confirm", response_model=ToolExecutionResult)
async def confirm_tools(
    approval: ToolApproval,
    settings: Settings = Depends(get_settings)
):
    """
    Confirm or reject proposed tool actions.
    
    After confirmation, approved tools are executed and results returned.
    The AI may propose additional actions based on the results.
    """
    session = _sessions.get(approval.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get approved tool IDs
    approved_ids = {a["tool_id"] for a in approval.approvals if a.get("approved", False)}
    
    # Execute approved tools
    executor = ToolExecutor(base_path=session.get("working_directory", "."))
    results = []
    
    for proposal in session.get("tool_proposals", []):
        tool_id = proposal.get("tool_id")
        
        if tool_id in approved_ids:
            # Execute the tool
            tool_type = ToolType(proposal["tool_type"])
            result = executor.execute(tool_type, proposal.get("parameters", {}))
            results.append({
                "tool_id": tool_id,
                "success": result.success,
                "output": result.output,
                "error": result.error
            })
        else:
            # Tool was rejected
            results.append({
                "tool_id": tool_id,
                "success": False,
                "output": None,
                "error": "Rejected by user"
            })
    
    # Update session
    _sessions[approval.session_id]["results"] = results
    
    return ToolExecutionResult(
        session_id=approval.session_id,
        results=results,
        response_text="Actions executed. See results above.",
        tool_proposals=[],
        requires_confirmation=False
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get the current state of a session."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Session not found")
