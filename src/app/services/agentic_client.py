"""
Agentic Anthropic Client - Uses Claude's tool use feature for human-in-the-loop actions.
"""

import uuid
import anthropic
from typing import Dict, Any, List, Optional, Generator
from src.app.tools.definitions import TOOL_DEFINITIONS, ToolProposal, ToolType


class AgenticAnthropicClient:
    """
    Client that uses Claude with tool use for agentic interactions.
    Claude can propose actions that require user confirmation.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_with_tools(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response that may include tool use proposals.
        
        Returns:
            Dict with:
                - response_text: The AI's text response
                - tool_proposals: List of tools the AI wants to use
                - requires_confirmation: Whether user confirmation is needed
        """
        messages = [{"role": "user", "content": prompt}]
        
        default_system = """You are a helpful coding assistant. You have access to tools that can:
- Create files
- Edit files
- Delete files
- Run terminal commands
- Read files
- List directories

When you need to perform an action, use the appropriate tool. Be clear about what you're doing and why.
Always explain your actions before using tools."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or default_system,
                tools=TOOL_DEFINITIONS,
                messages=messages
            )
            
            # Parse the response
            response_text = ""
            tool_proposals = []
            
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                elif block.type == "tool_use":
                    # Claude wants to use a tool - create a proposal
                    tool_type = self._map_tool_name_to_type(block.name)
                    proposal = ToolProposal(
                        tool_id=block.id,
                        tool_type=tool_type,
                        description=self._generate_tool_description(block.name, block.input),
                        parameters=block.input,
                        requires_confirmation=True,
                        risk_level=self._assess_risk(block.name, block.input)
                    )
                    tool_proposals.append(proposal)
            
            return {
                "request_id": response.id,
                "response_text": response_text,
                "tool_proposals": [p.model_dump() for p in tool_proposals],
                "requires_confirmation": len(tool_proposals) > 0,
                "stop_reason": response.stop_reason,
                "model": response.model,
                "usage": response.usage.model_dump()
            }
            
        except anthropic.APIError as e:
            return {
                "request_id": str(uuid.uuid4()),
                "response_text": f"Error: {str(e)}",
                "tool_proposals": [],
                "requires_confirmation": False,
                "error": str(e)
            }
    
    def continue_with_tool_results(
        self,
        original_messages: List[Dict],
        tool_results: List[Dict[str, Any]],
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Continue the conversation after tool execution.
        This is called after the user approves tools and we execute them.
        """
        # Add tool results to messages
        messages = original_messages.copy()
        
        # Format tool results for Claude
        tool_result_content = []
        for result in tool_results:
            tool_result_content.append({
                "type": "tool_result",
                "tool_use_id": result["tool_id"],
                "content": result["output"] if result["success"] else f"Error: {result['error']}"
            })
        
        messages.append({"role": "user", "content": tool_result_content})
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                tools=TOOL_DEFINITIONS,
                messages=messages
            )
            
            # Parse response (could have more tool calls)
            response_text = ""
            tool_proposals = []
            
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                elif block.type == "tool_use":
                    tool_type = self._map_tool_name_to_type(block.name)
                    proposal = ToolProposal(
                        tool_id=block.id,
                        tool_type=tool_type,
                        description=self._generate_tool_description(block.name, block.input),
                        parameters=block.input,
                        requires_confirmation=True,
                        risk_level=self._assess_risk(block.name, block.input)
                    )
                    tool_proposals.append(proposal)
            
            return {
                "response_text": response_text,
                "tool_proposals": [p.model_dump() for p in tool_proposals],
                "requires_confirmation": len(tool_proposals) > 0,
                "stop_reason": response.stop_reason
            }
            
        except anthropic.APIError as e:
            return {
                "response_text": f"Error: {str(e)}",
                "tool_proposals": [],
                "requires_confirmation": False,
                "error": str(e)
            }
    
    def _map_tool_name_to_type(self, name: str) -> ToolType:
        """Map tool name to ToolType enum."""
        mapping = {
            "create_file": ToolType.CREATE_FILE,
            "edit_file": ToolType.EDIT_FILE,
            "delete_file": ToolType.DELETE_FILE,
            "run_command": ToolType.RUN_COMMAND,
            "read_file": ToolType.READ_FILE,
            "list_directory": ToolType.LIST_DIRECTORY,
        }
        return mapping.get(name, ToolType.RUN_COMMAND)
    
    def _generate_tool_description(self, tool_name: str, params: Dict) -> str:
        """Generate human-readable description of what the tool will do."""
        if tool_name == "create_file":
            return f"Create file: {params.get('path', 'unknown')}"
        elif tool_name == "edit_file":
            return f"Edit file: {params.get('path', 'unknown')}"
        elif tool_name == "delete_file":
            return f"Delete file: {params.get('path', 'unknown')}"
        elif tool_name == "run_command":
            cmd = params.get('command', 'unknown')
            return f"Run command: {cmd[:50]}..." if len(cmd) > 50 else f"Run command: {cmd}"
        elif tool_name == "read_file":
            return f"Read file: {params.get('path', 'unknown')}"
        elif tool_name == "list_directory":
            return f"List directory: {params.get('path', '.')}"
        return f"Execute: {tool_name}"
    
    def _assess_risk(self, tool_name: str, params: Dict) -> str:
        """Assess risk level of a tool action."""
        high_risk = ["delete_file", "run_command"]
        medium_risk = ["edit_file", "create_file"]
        
        if tool_name in high_risk:
            return "high"
        elif tool_name in medium_risk:
            return "medium"
        return "low"
