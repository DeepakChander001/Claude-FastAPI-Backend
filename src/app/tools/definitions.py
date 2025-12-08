"""
Tool Use / Function Calling System

This module implements agentic tool use where Claude can:
1. Propose actions (create file, run command, delete file, etc.)
2. Ask for user confirmation
3. Execute the action after approval

This is the core of what makes Claude Code "agentic".
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class ToolType(str, Enum):
    """Types of tools the AI can propose to use."""
    CREATE_FILE = "create_file"
    EDIT_FILE = "edit_file"
    DELETE_FILE = "delete_file"
    RUN_COMMAND = "run_command"
    READ_FILE = "read_file"
    LIST_DIRECTORY = "list_directory"
    SEARCH_FILES = "search_files"


class ToolProposal(BaseModel):
    """A proposed tool action that requires user confirmation."""
    tool_id: str = Field(..., description="Unique identifier for this tool proposal")
    tool_type: ToolType = Field(..., description="Type of tool being proposed")
    description: str = Field(..., description="Human-readable description of what this action will do")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    requires_confirmation: bool = Field(True, description="Whether this action requires user approval")
    risk_level: Literal["low", "medium", "high"] = Field("medium", description="Risk level of the action")


class ToolResult(BaseModel):
    """Result of executing a tool."""
    tool_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


class ToolConfirmation(BaseModel):
    """User's response to a tool proposal."""
    tool_id: str
    approved: bool
    modified_parameters: Optional[Dict[str, Any]] = None


# Example tool definitions for Claude to use
TOOL_DEFINITIONS = [
    {
        "name": "create_file",
        "description": "Create a new file with the specified content. Use this when you need to write code or create configuration files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to create"
                },
                "content": {
                    "type": "string", 
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "run_command",
        "description": "Execute a shell command. Use this to run scripts, install packages, or perform system operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Directory to run the command in"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "edit_file",
        "description": "Edit an existing file by replacing specific content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to edit"
                },
                "old_content": {
                    "type": "string",
                    "description": "The content to find and replace"
                },
                "new_content": {
                    "type": "string",
                    "description": "The new content to insert"
                }
            },
            "required": ["path", "old_content", "new_content"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file. Use with caution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to delete"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files and directories in a path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list"
                }
            },
            "required": ["path"]
        }
    }
]
