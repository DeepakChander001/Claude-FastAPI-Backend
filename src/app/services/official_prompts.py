"""
Official Prompts and TUI Outputs for Claude Code Parity.
This file acts as the registry for all "Ported" prompts and "Mocked" responses.
"""

from typing import Dict, Any

# Type C: Visual Mocks (Static Text)
VISUAL_MOCKS = {
    "vim": "Vim mode enabled (Server-side acknowledgement only).",
    "login": "Already logged in as User (Simulated Session).",
    "logout": "Logged out (Session cleared).",
    "terminal-setup": "Terminal setup instructions:\n1. Add binary to PATH\n2. Reload shell.",
    "output-style": "Output style preference saved.",
    "theme": "Theme preference saved.",
    "permissions": "Permission rules updated.",
    "stats": "Usage Statistics:\n- Sessions: 12\n- Tokens: 1.5M\n- Cost: $4.20 (Simulated)",
    "usage": "## Usage Stats\n- **Provider**: OpenRouter\n- **Token Tracking**: Enabled (See Dashboard)",
    "tasks": "No background tasks running.",
    "todos": "No TODOs found in active context.",
    "install-github-app": "Please install the GitHub App manually via the Anthropic Console.",
    "install-slack-app": "Please install the Slack App manually via the Anthropic Console.",
    "mobile": "Scan QR Code for Mobile App (Not implemented in headless mode).",
    "release-notes": "Release Notes (Native Backend v2.1):\n- Added full slash command parity.\n- Activated DeepSeek Agents.",
    "pr-comments": "No active Pull Request found to fetch comments from.",
    "review": "Code Review initiated. (Logic placeholder - waiting for DeepSeek connection).",
    "commit": "Commit message generation initiated. (Logic placeholder).",
}

# Type A/B: Dynamic Logic Helpers
# (Future: Add actual System Prompts here)

def get_command_output(command: str) -> str:
    """Retrieve the mock output for a given command."""
    return VISUAL_MOCKS.get(command, f"Command '/{command}' acknowledged.")
