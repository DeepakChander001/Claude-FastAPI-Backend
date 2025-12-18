import os
import shutil
import subprocess
import time
from typing import Dict, Any, List, Optional
from src.app.config import Settings

class SlashCommandService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.commands = {
            "/doctor": self.handle_doctor,
            "/help": self.handle_help,
            "/config": self.handle_config,
            "/agents": self.handle_agents,
            "/clear": self.handle_clear,
            "/status": self.handle_status,
            "/cost": self.handle_cost,
        }
        
    def is_command(self, prompt: str) -> bool:
        return prompt.strip().startswith("/")

    def execute(self, prompt: str) -> Dict[str, Any]:
        parts = prompt.strip().split()
        command = parts[0].lower()
        args = parts[1:]
        
        handler = self.commands.get(command)
        if handler:
            return handler(args)
        
        # Fallback for unknown commands
        return {
            "output": f"Command '{command}' not recognized. Try `/help` to see available commands.",
            "action_required": False
        }

    def handle_help(self, args: List[str]) -> Dict[str, Any]:
        help_text = "## Available Commands\n\n"
        for cmd in self.commands.keys():
            help_text += f"- `{cmd}`\n"
        
        help_text += "\n\n**Common Actions:**\n"
        help_text += "- `/doctor`: Check system health\n"
        help_text += "- `/config`: View settings\n"
        help_text += "- `/agents`: List active agents\n"
        
        return {"output": help_text, "action_required": False}

    def handle_doctor(self, args: List[str]) -> Dict[str, Any]:
        checks = []
        
        # 1. API Check
        checks.append("🔎 **Checking Connections...**")
        if self.settings.OPENROUTER_API_KEY:
            checks.append("✓ OpenRouter API Key: Found")
        elif self.settings.ZAI_API_KEY:
             checks.append("✓ Z.AI API Key: Found")
        else:
             checks.append("✗ API Key: MISSING")
             
        # 2. File System
        checks.append("\n💾 **File System...**")
        try:
            with open("test_write_perm.tmp", "w") as f:
                f.write("test")
            os.remove("test_write_perm.tmp")
            checks.append("✓ Write Permissions: OK")
        except Exception as e:
            checks.append(f"✗ Write Permissions: FAILED ({str(e)})")
            
        # 3. Git
        checks.append("\n🔧 **Tools...**")
        git_path = shutil.which("git")
        if git_path:
            checks.append(f"✓ Git: Installed ({git_path})")
        else:
            checks.append("✗ Git: NOT FOUND")
            
        return {
            "output": "\n".join(checks),
            "action_required": False
        }

    def handle_config(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            # Show Config
            config_str = "## Current Configuration\n"
            config_str += f"- **Model**: `{self.settings.DEFAULT_MODEL}`\n"
            config_str += f"- **Environment**: `{self.settings.ENVIRONMENT}`\n"
            config_str += f"- **Mock Client**: `{self.settings.USE_MOCK_CLIENT}`\n"
            return {"output": config_str, "action_required": False}
        
        return {"output": "Config editing not yet implemented via slash command (security restriction).", "action_required": False}

    def handle_agents(self, args: List[str]) -> Dict[str, Any]:
        agents = [
            {"name": "claude", "role": "General Assistant", "model": self.settings.DEFAULT_MODEL},
            {"name": "coder", "role": "Specialist Coder", "model": "deepseek/deepseek-coder"},
            {"name": "doctor", "role": "System Diagnostician", "model": self.settings.DEFAULT_MODEL},
        ]
        
        output = "## Available Agents\n"
        for agent in agents:
            output += f"- **{agent['name']}**: {agent['role']} ({agent['model']})\n"
            
        return {"output": output, "action_required": False}

    def handle_clear(self, args: List[str]) -> Dict[str, Any]:
        return {"output": "Session context cleared.", "action_required": False}

    def handle_status(self, args: List[str]) -> Dict[str, Any]:
        return {"output": "System Status: ONLINE\nMode: Agentic Proxy", "action_required": False}

    def handle_cost(self, args: List[str]) -> Dict[str, Any]:
        return {"output": "Cost tracking is not yet linked to the billing API.", "action_required": False}
