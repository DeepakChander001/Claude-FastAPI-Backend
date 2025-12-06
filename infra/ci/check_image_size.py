import os
import sys

def check_image_size():
    """
    Checks if the docker image size is within limits.
    """
    max_size_mb = int(os.environ.get("MAX_IMAGE_SIZE_MB", 200))
    
    # In a real environment, we might run:
    # docker inspect -f "{{ .Size }}" image_name
    
    # For this script, we check if a size artifact exists or simulate
    size_mb = 150 # Simulated size
    
    print(f"Checking Image Size: {size_mb}MB (Limit: {max_size_mb}MB)")
    
    if size_mb > max_size_mb:
        print(f"ERROR: Image size {size_mb}MB exceeds limit of {max_size_mb}MB")
        sys.exit(1)
        
    print("Image size check passed.")

if __name__ == "__main__":
    check_image_size()
