"""
Tool Executor - Executes approved tool actions.
"""

import os
import subprocess
import uuid
from typing import Dict, Any, Optional
from .definitions import ToolType, ToolResult


class ToolExecutor:
    """
    Executes tool actions after user approval.
    This is a sandboxed executor - in production, add more security checks.
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
    
    def execute(self, tool_type: ToolType, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with the given parameters."""
        tool_id = str(uuid.uuid4())
        
        try:
            if tool_type == ToolType.CREATE_FILE:
                return self._create_file(tool_id, parameters)
            elif tool_type == ToolType.EDIT_FILE:
                return self._edit_file(tool_id, parameters)
            elif tool_type == ToolType.DELETE_FILE:
                return self._delete_file(tool_id, parameters)
            elif tool_type == ToolType.RUN_COMMAND:
                return self._run_command(tool_id, parameters)
            elif tool_type == ToolType.READ_FILE:
                return self._read_file(tool_id, parameters)
            elif tool_type == ToolType.LIST_DIRECTORY:
                return self._list_directory(tool_id, parameters)
            else:
                return ToolResult(
                    tool_id=tool_id,
                    success=False,
                    error=f"Unknown tool type: {tool_type}"
                )
        except Exception as e:
            return ToolResult(
                tool_id=tool_id,
                success=False,
                error=str(e)
            )
    
    def _create_file(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        path = params.get("path", "")
        content = params.get("content", "")
        
        # Security check - prevent path traversal
        if ".." in path:
            return ToolResult(tool_id=tool_id, success=False, error="Path traversal not allowed")
        
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w") as f:
            f.write(content)
        
        return ToolResult(
            tool_id=tool_id,
            success=True,
            output=f"Created file: {path}"
        )
    
    def _edit_file(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        path = params.get("path", "")
        old_content = params.get("old_content", "")
        new_content = params.get("new_content", "")
        
        full_path = os.path.join(self.base_path, path)
        
        if not os.path.exists(full_path):
            return ToolResult(tool_id=tool_id, success=False, error=f"File not found: {path}")
        
        with open(full_path, "r") as f:
            content = f.read()
        
        if old_content not in content:
            return ToolResult(tool_id=tool_id, success=False, error="Content to replace not found")
        
        new_file_content = content.replace(old_content, new_content, 1)
        
        with open(full_path, "w") as f:
            f.write(new_file_content)
        
        return ToolResult(
            tool_id=tool_id,
            success=True,
            output=f"Edited file: {path}"
        )
    
    def _delete_file(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        path = params.get("path", "")
        full_path = os.path.join(self.base_path, path)
        
        if not os.path.exists(full_path):
            return ToolResult(tool_id=tool_id, success=False, error=f"File not found: {path}")
        
        os.remove(full_path)
        
        return ToolResult(
            tool_id=tool_id,
            success=True,
            output=f"Deleted file: {path}"
        )
    
    def _run_command(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        command = params.get("command", "")
        working_dir = params.get("working_directory", self.base_path)
        
        # Security: Only allow safe commands (customize this list)
        dangerous_patterns = ["rm -rf /", "sudo rm", "> /dev", "mkfs", "dd if="]
        for pattern in dangerous_patterns:
            if pattern in command:
                return ToolResult(
                    tool_id=tool_id,
                    success=False,
                    error=f"Dangerous command blocked: {pattern}"
                )
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            return ToolResult(
                tool_id=tool_id,
                success=result.returncode == 0,
                output=output,
                error=result.stderr if result.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_id=tool_id,
                success=False,
                error="Command timed out after 30 seconds"
            )
    
    def _read_file(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        path = params.get("path", "")
        full_path = os.path.join(self.base_path, path)
        
        if not os.path.exists(full_path):
            return ToolResult(tool_id=tool_id, success=False, error=f"File not found: {path}")
        
        with open(full_path, "r") as f:
            content = f.read()
        
        return ToolResult(
            tool_id=tool_id,
            success=True,
            output=content
        )
    
    def _list_directory(self, tool_id: str, params: Dict[str, Any]) -> ToolResult:
        path = params.get("path", ".")
        full_path = os.path.join(self.base_path, path)
        
        if not os.path.exists(full_path):
            return ToolResult(tool_id=tool_id, success=False, error=f"Directory not found: {path}")
        
        items = os.listdir(full_path)
        output = "\n".join(items)
        
        return ToolResult(
            tool_id=tool_id,
            success=True,
            output=output
        )
