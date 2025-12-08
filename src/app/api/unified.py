"""
Unified API Endpoint - Single endpoint that handles all functionality.

This merges:
- Simple text generation
- Streaming responses
- Agentic tool use with confirmation
- Intent detection and routing

All through ONE endpoint: /api/generate
"""

import uuid
import logging
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.app.config import Settings
from src.app.dependencies import get_settings, get_anthropic_client
from src.app.services.anthropic_client import AnthropicClientProtocol
from src.app.db import SupabaseClientWrapper
from src.app.tools import ToolExecutor, ToolType, TOOL_DEFINITIONS

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session storage for pending actions
_sessions: Dict[str, Dict[str, Any]] = {}

# Global database client
_db_client: Optional[SupabaseClientWrapper] = None


# ============ Request/Response Models ============

class UnifiedRequest(BaseModel):
    """Unified request model for all operations."""
    prompt: str = Field(..., description="The user's query or request")
    model: Optional[str] = Field(None, description="Model to use (optional)")
    max_tokens: int = Field(1024, description="Maximum tokens in response")
    temperature: float = Field(0.7, description="Sampling temperature")
    stream: bool = Field(False, description="Enable streaming response")
    
    # For confirmation flow
    session_id: Optional[str] = Field(None, description="Session ID for continuing a conversation")
    confirm: Optional[bool] = Field(None, description="Set to true to confirm pending actions")
    approvals: Optional[List[Dict[str, Any]]] = Field(None, description="Approval decisions for pending actions")


class UnifiedResponse(BaseModel):
    """Unified response model for all operations."""
    request_id: str
    output: str
    model: str
    
    # Action-related fields
    action_required: bool = Field(False, description="Whether user confirmation is needed")
    pending_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actions awaiting approval")
    session_id: Optional[str] = Field(None, description="Session ID for confirmation flow")
    
    # Execution results
    action_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results of executed actions")
    
    # Usage stats
    usage: Optional[Dict[str, Any]] = Field(None)


# ============ Helper Functions ============

def get_db_client(settings: Settings) -> Optional[SupabaseClientWrapper]:
    """Get or create the database client."""
    global _db_client
    if _db_client is None and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        _db_client = SupabaseClientWrapper(
            url=settings.SUPABASE_URL,
            key=settings.SUPABASE_KEY
        )
    return _db_client


def detect_intent(prompt: str) -> str:
    """
    Detect user intent from the prompt.
    Returns: 'simple', 'tool_use', or 'search'
    """
    prompt_lower = prompt.lower()
    
    # Tool use keywords
    tool_keywords = [
        'create file', 'make file', 'write file', 'save file',
        'delete file', 'remove file',
        'edit file', 'modify file', 'update file',
        'run command', 'execute', 'run script',
        'list files', 'show files', 'list directory',
        'read file', 'show file', 'open file'
    ]
    
    for keyword in tool_keywords:
        if keyword in prompt_lower:
            return 'tool_use'
    
    # Default to simple question
    return 'simple'


def stream_generator(
    client: AnthropicClientProtocol,
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float
) -> Generator[str, None, None]:
    """Generator for streaming responses."""
    for chunk in client.stream_generate(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    ):
        yield chunk


def generate_tool_proposals(prompt: str) -> List[Dict[str, Any]]:
    """Generate tool proposals based on the prompt."""
    proposals = []
    prompt_lower = prompt.lower()
    
    # Detect create file intent
    if 'create' in prompt_lower and 'file' in prompt_lower:
        # Extract filename if mentioned
        import re
        file_match = re.search(r'(?:called|named|file)\s+([a-zA-Z0-9_.-]+)', prompt_lower)
        filename = file_match.group(1) if file_match else 'new_file.py'
        
        proposals.append({
            "tool_id": str(uuid.uuid4()),
            "tool_type": "create_file",
            "description": f"Create file: {filename}",
            "parameters": {
                "path": filename,
                "content": f"# {filename}\n# Created by AI assistant\n\nprint('Hello, World!')"
            },
            "requires_confirmation": True,
            "risk_level": "medium"
        })
    
    # Detect run command intent
    if 'run' in prompt_lower or 'execute' in prompt_lower or 'command' in prompt_lower:
        import re
        cmd_match = re.search(r'(?:run|execute|command)[:\s]+(.+?)(?:$|\.)', prompt_lower)
        command = cmd_match.group(1).strip() if cmd_match else 'echo "Hello"'
        
        proposals.append({
            "tool_id": str(uuid.uuid4()),
            "tool_type": "run_command",
            "description": f"Run command: {command}",
            "parameters": {"command": command},
            "requires_confirmation": True,
            "risk_level": "high"
        })
    
    # Detect list directory intent
    if 'list' in prompt_lower and ('file' in prompt_lower or 'director' in prompt_lower):
        proposals.append({
            "tool_id": str(uuid.uuid4()),
            "tool_type": "list_directory",
            "description": "List directory: .",
            "parameters": {"path": "."},
            "requires_confirmation": True,
            "risk_level": "low"
        })
    
    # Detect read file intent
    if 'read' in prompt_lower and 'file' in prompt_lower:
        import re
        file_match = re.search(r'(?:read|show|open)\s+(?:file\s+)?([a-zA-Z0-9_.-]+)', prompt_lower)
        filename = file_match.group(1) if file_match else 'file.txt'
        
        proposals.append({
            "tool_id": str(uuid.uuid4()),
            "tool_type": "read_file",
            "description": f"Read file: {filename}",
            "parameters": {"path": filename},
            "requires_confirmation": True,
            "risk_level": "low"
        })
    
    # Detect delete file intent
    if 'delete' in prompt_lower or 'remove' in prompt_lower:
        import re
        file_match = re.search(r'(?:delete|remove)\s+(?:file\s+)?([a-zA-Z0-9_.-]+)', prompt_lower)
        filename = file_match.group(1) if file_match else 'file.txt'
        
        proposals.append({
            "tool_id": str(uuid.uuid4()),
            "tool_type": "delete_file",
            "description": f"Delete file: {filename}",
            "parameters": {"path": filename},
            "requires_confirmation": True,
            "risk_level": "high"
        })
    
    return proposals


def execute_approved_tools(
    approvals: List[Dict[str, Any]], 
    pending_actions: List[Dict[str, Any]],
    working_directory: str = "."
) -> List[Dict[str, Any]]:
    """Execute approved tools and return results."""
    approved_ids = {a["tool_id"] for a in approvals if a.get("approved", False)}
    executor = ToolExecutor(base_path=working_directory)
    results = []
    
    for action in pending_actions:
        tool_id = action.get("tool_id")
        
        if tool_id in approved_ids:
            tool_type = ToolType(action["tool_type"])
            result = executor.execute(tool_type, action.get("parameters", {}))
            results.append({
                "tool_id": tool_id,
                "description": action.get("description", ""),
                "success": result.success,
                "output": result.output,
                "error": result.error
            })
        else:
            results.append({
                "tool_id": tool_id,
                "description": action.get("description", ""),
                "success": False,
                "output": None,
                "error": "Rejected by user"
            })
    
    return results


# ============ Main Unified Endpoint ============

@router.post("/api/generate", response_model=None)
async def unified_generate(
    request: UnifiedRequest,
    settings: Settings = Depends(get_settings),
    client: AnthropicClientProtocol = Depends(get_anthropic_client)
):
    """
    Unified endpoint for all AI operations.
    
    This single endpoint handles:
    - Simple text generation
    - Streaming responses
    - Tool use with confirmation (create files, run commands, etc.)
    
    **Flow:**
    1. Send a prompt → Get response (may include pending_actions)
    2. If action_required=true → Confirm with approvals
    3. Get final result
    
    **Examples:**
    
    Simple question:
    ```json
    {"prompt": "What is Python?"}
    ```
    
    Create a file (will ask for confirmation):
    ```json
    {"prompt": "Create a file called hello.py"}
    ```
    
    Confirm the action:
    ```json
    {"session_id": "abc-123", "confirm": true, "approvals": [{"tool_id": "xyz", "approved": true}]}
    ```
    """
    model = request.model or settings.DEFAULT_MODEL
    request_id = str(uuid.uuid4())
    
    # Get database client for logging
    db = get_db_client(settings)
    
    # ===== CASE 1: User is confirming pending actions =====
    if request.confirm and request.session_id:
        session = _sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        pending_actions = session.get("pending_actions", [])
        approvals = request.approvals or []
        
        # Execute approved tools
        results = execute_approved_tools(approvals, pending_actions)
        
        # Clear session
        del _sessions[request.session_id]
        
        # Format output
        success_count = sum(1 for r in results if r.get("success"))
        total_count = len(results)
        
        output_parts = [f"Executed {success_count}/{total_count} actions:\n"]
        for r in results:
            status = "✓" if r.get("success") else "✗"
            output_parts.append(f"{status} {r.get('description', 'Unknown action')}")
            if r.get("output"):
                output_parts.append(f"   Output: {r['output'][:200]}")
            if r.get("error") and r["error"] != "Rejected by user":
                output_parts.append(f"   Error: {r['error']}")
        
        return UnifiedResponse(
            request_id=request_id,
            output="\n".join(output_parts),
            model=model,
            action_required=False,
            pending_actions=[],
            action_results=results
        )
    
    # ===== CASE 2: Streaming request =====
    if request.stream:
        return StreamingResponse(
            stream_generator(
                client=client,
                prompt=request.prompt,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ),
            media_type="text/plain"
        )
    
    # ===== CASE 3: Detect intent and route =====
    intent = detect_intent(request.prompt)
    
    # If tool use is needed, generate proposals and ask for confirmation
    if intent == 'tool_use':
        proposals = generate_tool_proposals(request.prompt)
        
        if proposals:
            session_id = str(uuid.uuid4())
            _sessions[session_id] = {
                "prompt": request.prompt,
                "pending_actions": proposals,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Build response text
            action_descriptions = [p.get("description", "") for p in proposals]
            output = f"I'll help you with that. Here are the actions I need to perform:\n\n"
            for i, desc in enumerate(action_descriptions, 1):
                risk = proposals[i-1].get("risk_level", "medium")
                output += f"{i}. {desc} [Risk: {risk}]\n"
            output += f"\nPlease confirm by sending:\n"
            output += f'{{"session_id": "{session_id}", "confirm": true, "approvals": ['
            output += ', '.join([f'{{"tool_id": "{p["tool_id"]}", "approved": true}}' for p in proposals])
            output += ']}'
            
            return UnifiedResponse(
                request_id=request_id,
                output=output,
                model=model,
                action_required=True,
                pending_actions=proposals,
                session_id=session_id
            )
    
    # ===== CASE 4: Simple text generation =====
    # Log to database
    request_record = None
    if db and db.client:
        try:
            request_record = db.create_request(
                prompt=request.prompt,
                model=model,
                stream=request.stream,
                user_id=None
            )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
    
    try:
        result = client.generate_text(
            prompt=request.prompt,
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Update database
        if db and db.client and request_record:
            try:
                db.update_request_status(
                    request_id=request_record.get("id", ""),
                    status="done",
                    partial_output=result.get("output", ""),
                    completed_at=datetime.utcnow().isoformat()
                )
            except Exception as e:
                logger.error(f"Failed to update request: {e}")
        
        return UnifiedResponse(
            request_id=result.get("request_id", request_id),
            output=result.get("output", ""),
            model=result.get("model", model),
            action_required=False,
            pending_actions=[],
            usage=result.get("usage")
        )
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
