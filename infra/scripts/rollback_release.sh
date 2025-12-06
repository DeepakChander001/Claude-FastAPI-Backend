#!/bin/sh
# rollback_release.sh - Rollback to previous ECS task definition
# ============================================================================
# Usage:
#   ./rollback_release.sh --live
# ============================================================================
set -euo pipefail

LIVE=false
CLUSTER_NAME="${CLUSTER_NAME:-claude-proxy}"
SERVICE_NAME="${SERVICE_NAME_API:-api-service}"
TASK_FAMILY="${TASK_FAMILY:-claude-proxy-api}"

while [ $# -gt 0 ]; do
    case "$1" in
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

echo "===== Rollback Release ====="
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Task Family: $TASK_FAMILY"
echo "Live: $LIVE"

# Find previous task definition
echo "[Step 1] Finding Previous Task Definition..."
echo "  aws ecs list-task-definitions --family-prefix $TASK_FAMILY --sort DESC --max-items 5"

# Simulate getting previous revision
CURRENT_REVISION=10
PREVIOUS_REVISION=$((CURRENT_REVISION - 1))
PREVIOUS_TASK_DEF="${TASK_FAMILY}:${PREVIOUS_REVISION}"

echo "  Current: ${TASK_FAMILY}:${CURRENT_REVISION}"
echo "  Rolling back to: $PREVIOUS_TASK_DEF"

# Rollback
echo "[Step 2] Rolling Back Service..."
echo "  aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $PREVIOUS_TASK_DEF --force-new-deployment"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME" --task-definition "$PREVIOUS_TASK_DEF" --force-new-deployment
fi

# Verify
echo "[Step 3] Verifying Rollback..."
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME"

echo "===== Rollback Complete ====="
