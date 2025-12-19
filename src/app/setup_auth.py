
import os
import requests
import sys
import subprocess

ENV_PATH = "/home/ubuntu/EC2-Backend/.env"

def setup():
    print("=========================================")
    print("   NEXUS SERVER AUTH SETUP")
    print("=========================================")
    print("This script will configure your Google OAuth Keys.")
    print("Please ensure you have 'Desktop App' credentials from Google Cloud Console.")
    print("")

    client_id = input("Enter GOOGLE_CLIENT_ID: ").strip()
    client_secret = input("Enter GOOGLE_CLIENT_SECRET: ").strip()

    if not client_id or not client_secret:
        print("Error: Empty values not allowed.")
        return

    # Validate Keys with Google (Pre-Flight)
    print("\n[.] Validating keys with Google...")
    try:
        # We try to initiate a device flow to check if keys are accepted
        test_url = "https://oauth2.googleapis.com/device/code"
        test_payload = {"client_id": client_id, "scope": "email profile openid"}
        resp = requests.post(test_url, data=test_payload)
        
        if resp.status_code == 200:
            print("[+] Keys are VALID! Google accepted them.")
        elif resp.status_code == 400:
            # 400 often means "invalid_client"
            print(f"[-] Google Rejected Keys (400): {resp.json().get('error', 'Unknown Error')}")
            print("    Reason: Likely Invalid Client ID or Wrong Type (Web vs Desktop).")
            confirm = input("    Do you want to save them anyway? (y/n): ")
            if confirm.lower() != 'y':
                return
        elif resp.status_code == 401:
             print(f"[-] Google Rejected Keys (401): Valid Format but Unauthorized.")
             confirm = input("    Do you want to save them anyway? (y/n): ")
             if confirm.lower() != 'y':
                return
        else:
            print(f"[-] Unexpected Google Response: {resp.status_code} - {resp.text}")
            confirm = input("    Do you want to save them anyway? (y/n): ")
            if confirm.lower() != 'y':
                return

    except Exception as e:
        print(f"[-] Validation Network Error: {e}")
        print("    (Checking connectivity... Skipped)")

    # Write .env
    print(f"\n[.] Writing clean .env to {ENV_PATH}...")
    content = f"""# CORE CONFIGURATION
GOOGLE_CLIENT_ID="{client_id}"
GOOGLE_CLIENT_SECRET="{client_secret}"
GOOGLE_DISCOVERY_URL="https://accounts.google.com/.well-known/openid-configuration"
"""
    try:
        with open(ENV_PATH, "w") as f:
            f.write(content)
        print("[+] .env file written successfully.")
    except Exception as e:
        print(f"[-] Failed to write file: {e}")
        return

    # Restart Service
    print("\n[.] Restarting Service...")
    try:
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "claude-proxy"], check=True)
        print("[+] Service Restarted!")
    except Exception as e:
        print(f"[-] Failed to restart service: {e}")
        return

    print("\n=========================================")
    print("   SETUP COMPLETE - TRY LOGIN NOW")
    print("=========================================")

if __name__ == "__main__":
    setup()
