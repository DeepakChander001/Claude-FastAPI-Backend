import os
import re
import sys

def verify_pinned_base(dockerfile_path="infra/docker/Dockerfile.prod"):
    """
    Verifies that FROM instructions in Dockerfile use pinned digests.
    """
    print(f"Verifying {dockerfile_path}...")
    
    if not os.path.exists(dockerfile_path):
        print(f"Error: {dockerfile_path} not found.")
        sys.exit(1)

    with open(dockerfile_path, "r") as f:
        lines = f.readlines()

    errors = 0
    for line in lines:
        if line.strip().upper().startswith("FROM"):
            # Check for @sha256:
            if "@sha256:" not in line:
                # Check if allowed via env var
                if os.environ.get("ALLOW_UNPINNED") == "true":
                    print(f"WARNING: Unpinned base image found: {line.strip()}")
                else:
                    print(f"ERROR: Unpinned base image found: {line.strip()}")
                    print("       Use FROM image@sha256:digest format.")
                    errors += 1
            else:
                print(f"OK: Pinned image found: {line.strip()}")

    if errors > 0:
        print(f"Verification failed with {errors} errors.")
        sys.exit(1)
    
    print("Verification passed.")

if __name__ == "__main__":
    verify_pinned_base()
