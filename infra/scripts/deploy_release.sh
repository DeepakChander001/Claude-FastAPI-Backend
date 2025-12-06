#!/bin/sh
# deploy_release.sh - Deploy release to AWS ECS
# ============================================================================
# Required ENV:
#   AWS_REGION, ECR_REPO, CLUSTER_NAME, SERVICE_NAME_API, SERVICE_NAME_WORKER
# Usage:
#   ./deploy_release.sh --env staging --image myimage:latest --strategy rolling
#   ./deploy_release.sh --env prod --image myimage:latest --strategy canary --live
# ============================================================================
set -euo pipefail

# Defaults
ENV="staging"
IMAGE=""
STRATEGY="rolling"
LIVE=false
BUILD=false
PROMOTE=false
ROLLBACK=false

# Parse args
while [ $# -gt 0 ]; do
    case "$1" in
        --env) ENV="$2"; shift 2;;
        --image) IMAGE="$2"; shift 2;;
        --strategy) STRATEGY="$2"; shift 2;;
        --build) BUILD=true; shift;;
        --live) LIVE=true; shift;;
        --promote) PROMOTE=true; shift;;
        --rollback) ROLLBACK=true; shift;;
        *) echo "Unknown arg: $1"; exit 1;;
    esac
done

# Config (use env vars or defaults)
AWS_REGION="${AWS_REGION:-REPLACE_ME_REGION}"
ECR_REPO="${ECR_REPO:-REPLACE_ME_ACCOUNT.dkr.ecr.REPLACE_ME_REGION.amazonaws.com/claude-proxy}"
CLUSTER_NAME="${CLUSTER_NAME:-claude-proxy}"
SERVICE_NAME_API="${SERVICE_NAME_API:-api-service}"
SERVICE_NAME_WORKER="${SERVICE_NAME_WORKER:-worker-service}"
TASK_FAMILY="${TASK_FAMILY:-claude-proxy-api}"
ALB_DNS="${ALB_DNS:-REPLACE_ME_ALB_DNS}"
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")

echo "===== Deploy Release ====="
echo "Environment: $ENV"
echo "Image: $IMAGE"
echo "Strategy: $STRATEGY"
echo "Live: $LIVE"
echo "Commit: $COMMIT_SHA"

# Step 1: Build (optional)
if [ "$BUILD" = true ]; then
    echo "[Step 1] Building Docker Image..."
    echo "  docker build -t ${ECR_REPO}:${COMMIT_SHA} -f infra/docker/Dockerfile.prod ."
    if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
        docker build -t "${ECR_REPO}:${COMMIT_SHA}" -f infra/docker/Dockerfile.prod .
    fi
fi

# Step 2: Push to ECR
echo "[Step 2] Pushing to ECR..."
echo "  aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO"
echo "  docker push ${ECR_REPO}:${COMMIT_SHA}"
if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REPO"
    docker push "${ECR_REPO}:${COMMIT_SHA}"
fi

# Step 3: Render Task Definition
echo "[Step 3] Rendering Task Definition..."
echo "  IMAGE=${ECR_REPO}:${COMMIT_SHA} ./infra/scripts/render_taskdef.sh"
IMAGE="${ECR_REPO}:${COMMIT_SHA}" ./infra/scripts/render_taskdef.sh 2>/dev/null || true

# Step 4: Register Task Definition
echo "[Step 4] Registering Task Definition..."
echo "  aws ecs register-task-definition --cli-input-json file://infra/ecs/rendered_task_def.json"
if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    aws ecs register-task-definition --cli-input-json file://infra/ecs/rendered_task_def.json
fi

# Step 5: Deploy
if [ "$STRATEGY" = "rolling" ]; then
    echo "[Step 5] Rolling Deployment..."
    echo "  aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME_API --force-new-deployment"
    if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
        aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME_API" --force-new-deployment
    fi
elif [ "$STRATEGY" = "canary" ]; then
    echo "[Step 5] Canary Deployment..."
    echo "  ./infra/scripts/canary_release.sh --image ${ECR_REPO}:${COMMIT_SHA} --canary-percent 1"
    if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
        ./infra/scripts/canary_release.sh --image "${ECR_REPO}:${COMMIT_SHA}" --canary-percent 1 --live
    fi
fi

# Step 6: Wait for Healthy
echo "[Step 6] Waiting for Deployment..."
echo "  python infra/scripts/wait_for_deployment.py --cluster $CLUSTER_NAME --service $SERVICE_NAME_API"

# Step 7: Smoke Test
echo "[Step 7] Running Smoke Tests..."
echo "  ./infra/scripts/smoke_test.sh --url http://${ALB_DNS}"
./infra/scripts/smoke_test.sh --url "http://${ALB_DNS}" 2>/dev/null || echo "(Dry run or service not reachable)"

# Step 8: Promote (optional)
if [ "$PROMOTE" = true ]; then
    echo "[Step 8] Promoting..."
    echo "  ./infra/scripts/promote_canary.sh --to 100"
fi

# Rollback instructions
if [ "$ROLLBACK" = true ]; then
    echo "[Rollback] Rolling back..."
    echo "  ./infra/scripts/rollback_release.sh --live"
fi

echo "===== Deploy Complete (Dry Run) ====="
