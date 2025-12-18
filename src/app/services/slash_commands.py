import os
import shutil
import subprocess
import time
from typing import Dict, Any, List, Optional
from src.app.config import Settings

from src.app.services.agent_prompts import AGENTS, get_agent_config
from src.app.services.official_prompts import VISUAL_MOCKS, OFFICIAL_LOGIC_PROMPTS, get_command_output

class SlashCommandService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.active_agent = "claude" # Default agent
        self.commands = {
            "/doctor": self.handle_doctor,
            "/help": self.handle_help,
            "/config": self.handle_config,
            "/agents": self.handle_agents,
            "/agent": self.handle_agents,
            "/clear": self.handle_clear,
            "/context": self.handle_context,
            "/exit": self.handle_exit,
            "/logout": self.handle_exit,
            "/compact": self.handle_compact,
        }
        
        # 1. Register Type C (Visual Mocks)
        for cmd in VISUAL_MOCKS.keys():
            self.commands[f"/{cmd}"] = self.handle_visual_mock

        # 2. Register Type A (Ported Logic)
        for cmd in OFFICIAL_LOGIC_PROMPTS.keys():
            self.commands[f"/{cmd}"] = self.handle_ported_logic
        
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
        """
        Mimics the Claude Code /doctor output with "L" list style.
        """
        import sys
        
        # Gather info
        git_version = "NOT FOUND"
        try:
            res = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                git_version = res.stdout.strip().replace("git version ", "")
        except:
            pass

        py_version = sys.version.split()[0]
        
        # Build TUI output matching screenshot
        output = f"""Diagnostics
L Currently running: native (2.0.72)
L Path: native
L Invoked: {sys.executable} (simulated)
L Config install method: native
L Auto-updates: enabled
L Search: OK (bundled)
L Python: {py_version}
L Git: {git_version}
L Active Agent: {self.active_agent.title()}

Press Enter to continue..."""

        return {
            "output": output,
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
        # Case 1: Switching Agent
        if args:
            target = args[0].lower()
            # Loose matching
            selected_key = next((k for k, v in AGENTS.items() if k in target or v["name"].lower() in target), None)
            
            if selected_key:
                # Update State
                self.active_agent = selected_key
                config = AGENTS[selected_key]
                
                return {
                    "output": f"✅ Switched active persona to **{config['name']}** • {config['model']}",
                    "action_required": False,
                    "set_agent": selected_key # Signal to unified.py
                }
            else:
                 return {
                    "output": f"❌ Agent '{target}' not found.",
                    "action_required": False
                }

        # Case 2: Listing Agents (TUI Style Replica)
        output = """# Agents
No custom agents found

> **Create new agent**

No custom agents found. Create specialized subagents that the system can delegate to.
Each subagent has its own context window, custom system prompt, and specific tools.
Try creating: Code Reviewer, Code Simplifier, Security Reviewer, Tech Lead, or UX Reviewer.

---

**Built-in (always available):**"""
        
        for key, agent in AGENTS.items():
            # Marker for active agent
            marker = "*" if key == self.active_agent else " "
            output += f"\n- **{agent['name']}** • {agent['model']} {marker}"
            
        # Add footer simulation
        output += "\n\n_Press ↑↓ to navigate • Enter to select • Esc to go back_"
            
        return {"output": output, "action_required": False}

    def handle_visual_mock(self, args: List[str]) -> Dict[str, Any]:
        """Generic handler for Visual Mocks (Type C)."""
        # We need to find which command triggered this to get the right output
        # NOTE: In a cleaner refactor, we'd pass the command name, but for now we look up the output based on keys.
        # Ideally, we should change the signature of handlers or use partials, but let's stick to the current contract.
        
        # Hack: Since we don't know the command name here easily without changing execute(), 
        # we will assume the command is passed as arg or we update execute() later. 
        # actually, let's update simple execute() to pass command to handler? 
        # No, let's just use a trick or simply return a generic message if we can't find it?
        # WAIT: execute() calls `return handler(args)`.
        
        # Better approach: We explicitly define the method for each if we want specific text, 
        # OR we change execute to pass the command name.
        # Let's stick to specific handlers or use a closure.
        return {"output": "Mock command executed.", "action_required": False}

    def execute(self, prompt: str) -> Dict[str, Any]:
        parts = prompt.strip().split()
        command = parts[0].lower()
        args = parts[1:]
        
        handler = self.commands.get(command)
        if handler:
            # Special Handling to inject command name
            if handler == self.handle_visual_mock or handler == self.handle_ported_logic:
                return handler(args, command_name=command[1:])
            return handler(args)
        
        return {
            "output": f"Command '{command}' not recognized. Try `/help` to see available commands.",
            "action_required": False
        }

    def handle_visual_mock(self, args: List[str], command_name: str = "") -> Dict[str, Any]:
        output = get_command_output(command_name)
        return {"output": output, "action_required": False}

    def handle_ported_logic(self, args: List[str], command_name: str = "") -> Dict[str, Any]:
        """
        Generic handler for Type A (Ported Prompts).
        Matches the context variables expected by OFFICIAL_LOGIC_PROMPTS.
        """
        prompt_template = OFFICIAL_LOGIC_PROMPTS.get(command_name)
        if not prompt_template:
             return {"output": f"Logic for /{command_name} not found.", "action_required": False}

        # Gather Context
        git_status = self._get_git_status()
        git_diff = self._get_git_diff()
        branch = self._get_git_branch()
        # Fallback for keys check
        context_data = {
            "git_status": git_status,
            "git_diff": git_diff,
            "branch": branch,
            "context": f"Active Context:\nBranch: {branch}\nGit Status:\n{git_status}" 
        }
        
        # Safe formatting
        try:
            filled_prompt = prompt_template.format(**context_data)
        except KeyError as e:
            filled_prompt = prompt_template + f"\n\n[Context Warning: Missing key {e}]"
        except Exception as e:
             filled_prompt = prompt_template + f"\n\n[Context Error: {e}]"
            
        return {
            "output": filled_prompt, 
            "action_required": True, 
            "execute_llm_call": True 
        }

    # --- Git Context Helpers ---
    def _run_git(self, args: List[str]) -> str:
        try:
            res = subprocess.run(["git"] + args, capture_output=True, text=True, check=False)
            return res.stdout.strip()
        except Exception:
            return ""

    def _get_git_status(self) -> str:
        return self._run_git(["status", "--short"]) or "No changes."

    def _get_git_diff(self) -> str:
        return self._run_git(["diff", "HEAD"]) or "No diff."

    def _get_git_branch(self) -> str:
        return self._run_git(["branch", "--show-current"]) or "main"
        
    def handle_context(self, args: List[str]) -> Dict[str, Any]:
        return {
            "output": "## Context\n- **Active Files**: None\n- **Conversation**: In Memory\n- **Mode**: AgentProxy", 
            "action_required": False
        }
    
    def handle_exit(self, args: List[str]) -> Dict[str, Any]:
        return {
            "output": "Session cleared. (To close the client, press Ctrl+C)", 
            "action_required": False
        }

    def handle_compact(self, args: List[str]) -> Dict[str, Any]:
        return {
            "output": "Compacting conversation history... (Done)", 
            "action_required": False
        }

    def handle_clear(self, args: List[str]) -> Dict[str, Any]:
        return {"output": "Session context cleared.", "action_required": False}
