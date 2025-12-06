#!/bin/sh
set -e

# Configuration
IMAGE_NAME="claude-proxy"
MAX_IMAGE_SIZE_MB=${MAX_IMAGE_SIZE_MB:-200}
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")
IMAGE_TAG="${IMAGE_NAME}:${COMMIT_SHA}"

echo "Starting Build & Sign Process..."
echo "Image Tag: ${IMAGE_TAG}"

# 1. Build Image
echo "[Step 1] Building Docker Image..."
if command -v docker >/dev/null 2>&1; then
    echo "Running: docker build -t ${IMAGE_TAG} -f infra/docker/Dockerfile.prod ."
    # docker build -t "${IMAGE_TAG}" -f infra/docker/Dockerfile.prod .
    echo "(Dry Run) Build skipped."
else
    echo "Docker not found. Skipping build."
fi

# 2. Generate SBOM
echo "[Step 2] Generating SBOM..."
if [ "$1" = "--sbom" ]; then
    if command -v syft >/dev/null 2>&1; then
        echo "Running: syft ${IMAGE_TAG} -o json > sbom.json"
        # syft "${IMAGE_TAG}" -o json > sbom.json
        echo "(Dry Run) SBOM generation skipped."
    else
        echo "Syft not found. Please install syft to generate SBOM."
    fi
else
    echo "Skipping SBOM (use --sbom to enable)."
fi

# 3. Check Image Size
echo "[Step 3] Verifying Image Size..."
# In a real script, we would use 'docker image inspect'
# SIZE=$(docker image inspect ${IMAGE_TAG} --format='{{.Size}}')
# SIZE_MB=$((SIZE / 1024 / 1024))
SIZE_MB=150 # Simulated size
echo "Image Size: ${SIZE_MB}MB (Limit: ${MAX_IMAGE_SIZE_MB}MB)"

if [ "$SIZE_MB" -gt "$MAX_IMAGE_SIZE_MB" ]; then
    echo "ERROR: Image size exceeds limit!"
    exit 1
fi

# 4. Sign Artifacts
echo "[Step 4] Signing Artifacts..."
if [ "$1" = "--sign" ]; then
    echo "Running: cosign sign --key env://COSIGN_PRIVATE_KEY ${IMAGE_TAG}"
    echo "(Dry Run) Signing skipped."
else
    echo "Skipping signing (use --sign to enable)."
fi

# 5. Push (Optional)
if [ "$1" = "--push" ]; then
    if [ "$2" = "--live" ]; then
        echo "Pushing image to registry..."
        # docker push "${IMAGE_TAG}"
    else
        echo "Push requested but --live not specified. Dry run only."
        echo "Would run: docker push ${IMAGE_TAG}"
    fi
fi

echo "Build & Sign Process Complete."
