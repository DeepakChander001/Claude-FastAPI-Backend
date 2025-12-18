
import os
import sys
import json
import requests
import time

# Default Configuration
DEFAULT_API_URL = "http://16.171.194.43:8000/api/generate"

def print_markdown(text):
    """
    Simple markdown printer.
    If 'rich' is installed, use it for pretty printing.
    Otherwise, just print text.
    """
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        console = Console()
        console.print(Markdown(text))
    except ImportError:
        print(text)

def main():
    print("\033[1;36mNexus CLI (Powered by Claude-FastAPI-Backend)\033[0m")
    print("Type /exit to quit.\n")

    session_id = None
    
    # Check for API URL override
    api_url = os.environ.get("CLAUDE_API_URL", DEFAULT_API_URL)

    while True:
        try:
            # 1. Get User Input
            prompt = input("\033[1;32m> \033[0m").strip()
            
            if not prompt:
                continue
                
            if prompt.lower() in ["/exit", "/quit"]:
                print("Goodbye!")
                break
            
            # 2. Send Request
            payload = {
                "prompt": prompt,
                "stream": False # CLI is easier with non-streaming for now
            }
            
            # Resume session if exists (for conversation context)
            if session_id:
                # In a real impl, we'd manage conversation history or pass IDs.
                # For this specific backend, session_id is mostly for ACTIONS.
                # But let's assume stateless for chat unless we add conversation_id.
                pass

            try:
                response = requests.post(api_url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"\033[1;31mError connecting to server: {e}\033[0m")
                continue

            # 3. Print Output
            if data.get("output"):
                print_markdown(data["output"])

            # 4. Handle Actions (Confirmation Flow)
            if data.get("action_required"):
                pending = data.get("pending_actions", [])
                sid = data.get("session_id")
                
                print(f"\n\033[1;33m[!] Action Required ({len(pending)} pending):\033[0m")
                for i, action in enumerate(pending, 1):
                    print(f" {i}. {action.get('description')} [Risk: {action.get('risk_level')}]")
                
                confirm = input("\n\033[1;33mDo you want to proceed? [y/N]: \033[0m").lower()
                
                if confirm == 'y':
                    # Send Confirmation
                    confirm_payload = {
                        "prompt": "", # Not used in confirmation
                        "confirm": True,
                        "session_id": sid,
                        "approvals": [{"tool_id": a["tool_id"], "approved": True} for a in pending]
                    }
                    
                    try:
                        print("\033[1;34mExecuting...\033[0m")
                        res2 = requests.post(api_url, json=confirm_payload, timeout=120)
                        data2 = res2.json()
                        print_markdown(data2.get("output", ""))
                    except Exception as e:
                         print(f"\033[1;31mExecution Error: {e}\033[0m")
                else:
                    print("Cancelled.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
