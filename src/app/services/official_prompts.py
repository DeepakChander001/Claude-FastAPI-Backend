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
    "chrome": """Claude in Chrome (Beta)

Claude in Chrome works with the Chrome extension to let you control your browser directly from Claude Code. Navigate websites, fill forms, capture screenshots, record GIFs, and debug with console logs and network requests.

Status: Disabled
Extension: Not detected

> Install Chrome extension
  Enabled by default: No

Usage: claude --chrome or claude --no-chrome

Enter to confirm • Esc to cancel""",
    "hooks": """Hook Configuration

Hooks are shell commands you can register to run during Claude Code processing. Docs

• Each hook event has its own input and output behavior
• Multiple hooks can be registered per event, executed in parallel
• Any changes to hooks outside of /hooks require a restart
• Timeout: 60 seconds

⚠ Hooks execute shell commands with your full user permissions. This can pose security risks, so only use hooks from trusted sources.
Learn more: https://code.claude.com/docs/en/hooks

Select hook event:
> 1.  PreToolUse - Before tool execution
  2.  PostToolUse - After tool execution
  3.  PostToolUseFailure - After tool execution fails
  4.  Notification - When notifications are sent
  5.  UserPromptSubmit - When the user submits a prompt
  6.  SessionStart - When a new session is started
  7.  Stop - Right before Claude concludes its response
  8.  SubagentStart - When a subagent (Task tool call) is started
  9.  SubagentStop - Right before a subagent (Task tool call) concludes its response
  10. PreCompact - Before conversation compaction
  11. SessionEnd - When a session is ending
  12. PermissionRequest - When a permission dialog is displayed
  13. Disable all hooks

Enter to select • Esc to exit""",
}

# Type A: Official Logic Prompts (Ported from Markdown)
OFFICIAL_LOGIC_PROMPTS = {
    "review": """
You are a Code Review Agent.
Goal: Provide a code review for the given files, following the official Claude Code logic.

STEPS:
1. Check if PR is closed/draft (Simulated).
2. Scan for CLAUDE.md compliance.
3. Launch agents to review changes.

You must Simulate 4 Agents in your reasoning:
- Agents 1+2: CLAUDE.md compliance
- Agent 3: Opus bug agent (High Signal Bugs only)
- Agent 4: Opus bug agent (Logic/Security)

CRITICAL:
- Only flag HIGH SIGNAL issues (Runtime bugs, clear CLAUDE.md violations).
- Ignore nitpicks, style suggestions (unless in CLAUDE.md).
- Verify every issue: If "variable not defined", ensure it is true.

Active Files Context:
{context}

Format your response exactly like the official tool:
---
## Code review
Found N issues:
1. <brief description> (CLAUDE.md says: "...")
<file path>:L<line>
---
If no issues:
---
## Auto code review
No issues found. Checked for bugs and CLAUDE.md compliance.
---
""",

    "commit": """
You are a git commit agent.
Context:
- Git Status: {git_status}
- Git Diff: {git_diff}

Task: Create a single git commit based on these changes.
Capabilities: Call the bash tool to `git commit -m "message"`.
Do NOT do anything else.
""",

    "pr-comments": """
You are a PR management agent.
Context:
- Git Status: {git_status}
- Branch: {branch}

Task:
1. Commit changes (if any).
2. Push branch.
3. Create PR using `gh pr create`.

Output: Sequence of tool calls.
"""
}

def get_command_output(command: str) -> str:
    """Retrieve the mock output for a given command."""
    return VISUAL_MOCKS.get(command, f"Command '/{command}' acknowledged.")
