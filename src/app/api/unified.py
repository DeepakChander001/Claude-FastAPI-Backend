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
from src.app.services.slash_commands import SlashCommandService
from src.app.services.agent_prompts import get_agent_config
import json

# Global Active Agent State (In-memory for simplicity)
ACTIVE_AGENT = "claude"

# Native Tool Definitions (OpenAI Format)
NATIVE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file with the specified content. Use this to write code or save data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path (e.g. src/main.py)"},
                    "content": {"type": "string", "description": "Full file content"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command. Use this to list files, run scripts, or check system status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run (e.g. ls -la, python script.py)"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path (default: .)"}
                },
                "required": ["path"]
            }
        }
    }
]

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
    stream: bool = Field(True, description="Enable streaming response")
    
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


# Intent detection functions removed in favor of Native Tool Calling


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


    return results


def yield_text_chunks(text: str, chunk_size: int = 20):
    """Yield text in small chunks to simulate streaming."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

@router.post("/generate", response_model=None)
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
    
    # Declare global state usage at the top
    global ACTIVE_AGENT
    
    # Get database client for logging
    db = get_db_client(settings)
    
    # 1. Parse Input
    prompt_text = request.prompt
    
    # 2. Log Request to Supabase w/ User Context (if available)
    # Note: CLI currently doesn't pass header, but we are setting up the structure.
    # Future TODO: extract user_id from headers/token.
    user_id = None 
    
    log_entry = db.create_request(
        prompt=prompt_text[:2000], 
        model=ACTIVE_MODEL_ID,
        stream=request.stream,
        user_id=user_id
    )
    # We pass the active_agent state to the service
    slash_service = SlashCommandService(settings)
    slash_service.active_agent = ACTIVE_AGENT 
    
    if slash_service.is_command(request.prompt):
        cmd_result = slash_service.execute(request.prompt)
        
        # Check if agent was switched
        if "set_agent" in cmd_result:
            ACTIVE_AGENT = cmd_result["set_agent"]

        # Special Case: Command wants to trigger the LLM with a specific prompt (Ported Logic)
        if cmd_result.get("execute_llm_call"):
            # We update the prompt with the "Ported" system prompt and fall through
            # to the standard generation logic below.
            # We essentially "Rewrite" the user's request from "/review" to "You are a code reviewer..."
            request.prompt = cmd_result["output"]
            # Fall through (do not return)
        else:
            return UnifiedResponse(
                request_id=request_id,
                output=cmd_result.get("output", ""),
                model="system-slash-command",
                action_required=cmd_result.get("action_required", False),
                pending_actions=[],
                session_id=None
            )

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
    
    # ===== CASE 2 & 3: Smart Agent & Streaming =====
    # Strategy: We generate synchronously first to check for Tool Calls.
    
    # 0. Get Active Agent Configuration
    agent_config = get_agent_config(ACTIVE_AGENT)
    system_prompt = agent_config.get("system_prompt", "")
    target_model = agent_config.get("model", model)
    
    # Prepend System Prompt to User Prompt (Simple Injection)
    # Note: For full robustness, we should use 'system' role in messages, 
    # but 'prompt' injection works well for DeepSeek V2/V3 compatibility via this client.
    full_prompt = f"System: {system_prompt}\n\nUser: {request.prompt}"

    try:
        # Call the model WITH tools (Synchronous)
        result = client.generate_text(
            prompt=full_prompt,
            model=target_model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            tools=NATIVE_TOOLS
        )
        
        raw_tool_calls = result.get("tool_calls")
        
        # 3A. Tool Actions Required -> Return JSON
        if raw_tool_calls:
            proposals = []
            for tool_call in raw_tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except:
                    func_args = {}
                
                # Map to our ToolTypes
                risk = "low"
                desc = f"Call {func_name}"
                
                if func_name == "create_file":
                    risk = "medium"
                    desc = f"Create file: {func_args.get('path', 'unknown')}"
                elif func_name == "run_command":
                    risk = "high"
                    desc = f"Run command: {func_args.get('command')}"
                elif func_name == "list_directory":
                    desc = f"List directory: {func_args.get('path')}"

                proposals.append({
                    "tool_id": str(uuid.uuid4()),
                    "tool_type": func_name,
                    "description": desc,
                    "parameters": func_args,
                    "requires_confirmation": True,
                    "risk_level": risk,
                    "native_tool_call_id": tool_call.id
                })
            
            if proposals:
                session_id = str(uuid.uuid4())
                _sessions[session_id] = {
                    "prompt": request.prompt,
                    "pending_actions": proposals,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                output = f"I need to perform the following actions:\n\n"
                for i, p in enumerate(proposals, 1):
                    output += f"{i}. {p['description']} [Risk: {p['risk_level']}]\n"
                
                if result.get("output"):
                    output = f"{result['output']}\n\n{output}"

                return UnifiedResponse(
                    request_id=request_id,
                    output=output,
                    model=model,
                    action_required=True,
                    pending_actions=proposals,
                    session_id=session_id
                )

        # 3B. Text Only -> Stream or Return JSON
        text_output = result.get("output") or ""
        
        if request.stream:
            # User wants streaming. We simulate it with the text we already generated.
            return StreamingResponse(
                yield_text_chunks(text_output),
                media_type="text/plain"
            )
        
        # Default JSON return
        return UnifiedResponse(
            request_id=result.get("request_id", request_id),
            output=text_output,
            model=result.get("model", model),
            action_required=False,
            pending_actions=[],
            usage=result.get("usage")
        )

    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
