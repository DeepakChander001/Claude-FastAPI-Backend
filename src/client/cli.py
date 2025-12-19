
import os
import sys
import json
import requests
import time
import getpass
import shutil
from pathlib import Path

# Enable command history with up/down arrows
try:
    import readline
except ImportError:
    try:
        import pyreadline3 as readline
    except ImportError:
        pass  # No readline available, continue without history

# Default Configuration
DEFAULT_API_URL = "http://16.171.194.43:80/api/generate"
BASE_API_URL = "http://16.171.194.43:80"
CONFIG_DIR = Path.home() / ".nexus"
CONFIG_FILE = CONFIG_DIR / "config.json"



def print_markdown(text):
    """Simple markdown printer."""
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        console = Console()
        console.print(Markdown(text))
    except ImportError:
        print(text)


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_auth_headers(config):
    """Get authorization headers if logged in."""
    auth = config.get("auth")
    if auth and auth.get("access_token"):
        return {"Authorization": f"Bearer {auth['access_token']}"}
    return {}


def handle_login(api_url):
    """Effectuate Device Authorization Flow."""
    print("\033[1;33m[!] Initiating Login...\033[0m")
    try:
        # 1. Request Code
        resp = requests.post(f"{BASE_API_URL}/api/auth/device/code")
        resp.raise_for_status()
        data = resp.json()
        
        device_code = data["device_code"]
        user_code = data["user_code"]
        verification_uri = data["verification_uri"]
        interval = data["interval"]
        
        print("\n\033[1;36m=========================================")
        print(f" Please visit: \033[1;34m{verification_uri}\033[1;36m")
        print(f" Enter Code:   \033[1;32m{user_code}\033[1;36m")
        print("=========================================\033[0m\n")
        
        print("Waiting for authentication...", end="", flush=True)
        
        # 2. Poll
        while True:
            time.sleep(interval)
            print(".", end="", flush=True)
            
            try:
                poll_resp = requests.post(
                    f"{BASE_API_URL}/api/auth/device/poll",
                    json={"device_code": device_code}
                )
                
                if poll_resp.status_code == 200:
                    token_data = poll_resp.json()
                    
                    # Save Token
                    config = load_config()
                    config["auth"] = token_data
                    save_config(config)
                    
                    print(f"\n\n\033[1;32m✅ Login Successful! (User: {token_data['email']})\033[0m")
                    return True
                    
                if poll_resp.status_code == 403:
                    print("\n\033[1;31m❌ Access Denied.\033[0m")
                    return False
                    
            except Exception:
                pass
                
    except Exception as e:
        print(f"\n\033[1;31mError during login: {e}\033[0m")
        return False


def handle_init():
    """Initialize current directory as S3 workspace by uploading files in batches."""
    print("\033[1;36m[!] Initializing Project to S3 Cloud...\033[0m")
    
    config = load_config()
    headers = get_auth_headers(config)
    
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    
    print(f"\033[1;34mProject: {project_name}\033[0m")
    print(f"\033[1;34mPath: {current_dir}\033[0m")
    
    # Confirm upload
    confirm = input("\n\033[1;33mUpload this folder to S3 cloud? [y/N]: \033[0m").lower()
    if confirm != 'y':
        print("Cancelled.")
        return False
    
    print("\n\033[1;34mScanning files...\033[0m")
    
    # Collect files to upload (exclude common patterns)
    exclude_patterns = ['.git', '__pycache__', 'node_modules', '.env', 'venv', '.venv', '.nexus', 'temp_research']
    files_to_upload = []
    
    for root, dirs, files in os.walk(current_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_patterns]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, current_dir).replace('\\', '/')
            
            # Skip binary files and very large files
            try:
                # Check file size first
                file_size = os.path.getsize(file_path)
                if file_size > 512 * 1024:  # Skip files > 512KB
                    print(f"   Skipping (large): {relative_path}")
                    continue
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    files_to_upload.append({
                        "path": relative_path,
                        "content": content
                    })
            except Exception as e:
                continue  # Silently skip binary files
    
    total_files = len(files_to_upload)
    print(f"\033[1;34mUploading {total_files} files to S3 in batches...\033[0m")
    
    # Batch upload (50 files per batch)
    BATCH_SIZE = 50
    total_uploaded = 0
    total_failed = 0
    s3_prefix = ""
    
    try:
        for i in range(0, total_files, BATCH_SIZE):
            batch = files_to_upload[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_files + BATCH_SIZE - 1) // BATCH_SIZE
            
            sys.stdout.write(f"\r   Batch {batch_num}/{total_batches} ({len(batch)} files)...")
            sys.stdout.flush()
            
            resp = requests.post(
                f"{BASE_API_URL}/api/workspace/init",
                json={
                    "project_name": project_name,
                    "files": batch
                },
                headers=headers,
                timeout=60  # 1 minute per batch
            )
            resp.raise_for_status()
            data = resp.json()
            
            total_uploaded += data.get("uploaded_count", 0)
            total_failed += data.get("failed_count", 0)
            s3_prefix = data.get("s3_prefix", s3_prefix)
        
        print(f"\n\n\033[1;32m✅ Upload Complete!\033[0m")
        print(f"   Files uploaded: {total_uploaded}")
        if total_failed > 0:
            print(f"   Files failed: {total_failed}")
        print(f"   S3 Path: {s3_prefix}")
        
        # Save project info
        config["active_project"] = {
            "name": project_name,
            "s3_prefix": s3_prefix,
            "local_path": current_dir
        }
        save_config(config)
        return True
            
    except Exception as e:
        print(f"\n\033[1;31mError: {e}\033[0m")
        return False


def handle_projects():
    """List user's S3 projects."""
    print("\033[1;36m[!] Loading Projects from S3...\033[0m")
    
    config = load_config()
    headers = get_auth_headers(config)
    
    try:
        resp = requests.get(
            f"{BASE_API_URL}/api/workspace/projects",
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("success"):
            projects = data.get("projects", [])
            if not projects:
                print("\n\033[1;33mNo projects found. Use /init to upload a project.\033[0m")
                return
            
            print(f"\n\033[1;32m📁 Your Projects ({len(projects)}):\033[0m")
            for i, proj in enumerate(projects, 1):
                active = ""
                if config.get("active_project", {}).get("name") == proj:
                    active = " \033[1;32m← active\033[0m"
                print(f"   {i}. {proj}{active}")
            
            print("\n\033[1;33mTo switch: /switch <project_name>\033[0m")
        else:
            print(f"\n\033[1;31mError: {data.get('error')}\033[0m")
            
    except Exception as e:
        print(f"\n\033[1;31mError: {e}\033[0m")


def handle_status():
    """Get current project workspace status."""
    config = load_config()
    active_project = config.get("active_project")
    
    if not active_project:
        print("\033[1;33mNo active project. Use /init to upload a project.\033[0m")
        return
    
    headers = get_auth_headers(config)
    project_name = active_project["name"]
    
    print(f"\033[1;36m[!] Workspace Status for: {project_name}\033[0m")
    
    try:
        resp = requests.get(
            f"{BASE_API_URL}/api/workspace/status?project_name={project_name}",
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("success"):
            print(f"\n\033[1;32m📊 Project Status:\033[0m")
            print(f"   Name: {data['project_name']}")
            print(f"   Total Files: {data['total_files']}")
            print(f"   Last Modified: {data.get('last_modified', 'N/A')}")
            print(f"   S3 Bucket: {data['s3_bucket']}")
            print(f"   S3 Path: {data['s3_prefix']}")
        else:
            print(f"\n\033[1;31mError: {data.get('error')}\033[0m")
            
    except Exception as e:
        print(f"\n\033[1;31mError: {e}\033[0m")


def handle_ls(path=""):
    """List files in S3 project directory."""
    config = load_config()
    active_project = config.get("active_project")
    
    if not active_project:
        print("\033[1;33mNo active project. Use /init first.\033[0m")
        return
    
    headers = get_auth_headers(config)
    project_name = active_project["name"]
    
    try:
        resp = requests.get(
            f"{BASE_API_URL}/api/workspace/ls?project_name={project_name}&path={path}",
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("success"):
            objects = data.get("objects", [])
            print(f"\n\033[1;32m📁 S3 Files ({len(objects)}):\033[0m")
            for obj in objects[:20]:  # Limit display
                size_kb = obj['size'] / 1024
                print(f"   {obj['path']} ({size_kb:.1f} KB)")
            if len(objects) > 20:
                print(f"   ... and {len(objects) - 20} more files")
        else:
            print(f"\n\033[1;31mError: {data.get('error')}\033[0m")
            
    except Exception as e:
        print(f"\n\033[1;31mError: {e}\033[0m")


def main():
    print("\033[1;36mNexus CLI (Powered by Claude-FastAPI-Backend)\033[0m")
    
    # 1. Init Sequence
    config = load_config()
    auth_config = config.get("auth")
    active_project = config.get("active_project")
    
    api_url = os.environ.get("CLAUDE_API_URL", DEFAULT_API_URL)
    
    # Explicit Login Check
    if not auth_config:
        print("\033[1;33m[!] You are not logged in.\033[0m")
        print("Type '/login' to authenticate via Gmail.\n")
    
    # Show Active Project
    if active_project:
        print(f"\033[1;34m☁ Cloud Project: {active_project['name']}\033[0m")
    
    print(f"\nCurrent Directory: {os.getcwd()}")
    
    while True:
        try:
            # 2. Loop
            prompt_text = "\033[1;32mNexus> \033[0m"
            if auth_config: 
                email_short = auth_config['email'][:5] if auth_config.get('email') else "user"
                prompt_text = f"\033[1;32mNexus({email_short}..)\033[0m"
                if active_project:
                    prompt_text = f"\033[1;32mNexus({email_short}..☁)\033[0m"
                prompt_text += "> "
            
            prompt = input(prompt_text).strip()
            
            if not prompt:
                continue
            if prompt.lower() in ["/exit", "/quit", "/q"]:
                print("Goodbye!")
                break
                
            # Command Handlers
            if prompt.lower() == "/login":
                if handle_login(api_url):
                    auth_config = load_config().get("auth")
                continue
            
            if prompt.lower() == "/init":
                handle_init()
                active_project = load_config().get("active_project")
                continue
            
            if prompt.lower() == "/projects":
                handle_projects()
                continue
            
            if prompt.lower() == "/status":
                handle_status()
                continue
            
            if prompt.lower().startswith("/ls"):
                parts = prompt.split(maxsplit=1)
                path = parts[1] if len(parts) > 1 else ""
                handle_ls(path)
                continue
            
            if prompt.lower() == "/help":
                print("\n\033[1;32mAvailable Commands:\033[0m")
                print("  /login    - Login with Google")
                print("  /init     - Upload current folder to S3 cloud")
                print("  /projects - List your cloud projects")
                print("  /status   - Show active project status")
                print("  /ls       - List files in cloud project")
                print("  /exit     - Exit CLI")
                print("\nOr just type a question to chat with AI.\n")
                continue
            
            # Regular AI Prompt - include S3 project context if active
            payload = {
                "prompt": prompt,
                "stream": False,
            }
            
            # Add S3 project context if user has an active project
            if active_project:
                payload["project_name"] = active_project.get("name")
                payload["user_id"] = auth_config.get("user_id", "default-user") if auth_config else "default-user"
            
            try:
                headers = get_auth_headers(config)
                response = requests.post(api_url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"\033[1;31mError connecting to server: {e}\033[0m")
                continue

            # Print Output
            if data.get("output"):
                print_markdown(data["output"])

            # Handle Actions
            if data.get("action_required"):
                pending = data.get("pending_actions", [])
                sid = data.get("session_id")
                
                print(f"\n\033[1;33m[!] Action Required ({len(pending)} pending):\033[0m")
                for i, action in enumerate(pending, 1):
                    print(f" {i}. {action.get('description')} [Risk: {action.get('risk_level')}]")
                
                confirm = input("\n\033[1;33mDo you want to proceed? [y/N]: \033[0m").lower()
                
                if confirm == 'y':
                    confirm_payload = {
                        "prompt": "",
                        "confirm": True,
                        "session_id": sid,
                        "approvals": [{"tool_id": a["tool_id"], "approved": True} for a in pending]
                    }
                    try:
                        print("\033[1;34mExecuting...\033[0m")
                        res2 = requests.post(api_url, json=confirm_payload, headers=headers, timeout=120)
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
