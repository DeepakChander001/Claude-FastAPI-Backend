import sys
import os
sys.path.insert(0, os.getcwd())

print("=== Diagnostic Script ===")
print(f"CWD: {os.getcwd()}")
print(f"Python: {sys.executable}")

try:
    print("\n[1] Importing src.app.api.auth...")
    from src.app.api import auth
    print("    SUCCESS: auth module loaded")
except Exception as e:
    import traceback
    print("    FAILED:")
    traceback.print_exc()

try:
    print("\n[2] Importing src.app.main...")
    from src.app import main
    print("    SUCCESS: main module loaded")
except Exception as e:
    import traceback
    print("    FAILED:")
    traceback.print_exc()

print("\n=== Diagnostic Complete ===")
