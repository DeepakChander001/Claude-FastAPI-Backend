#!/bin/sh
# auto_remediation_example.sh - Safe auto-remediation patterns
# ============================================================================
# ONLY PRINTS by default. Required IAM: ecs:UpdateService, ecs:StopTask
# ============================================================================
set -euo pipefail

LIVE=false
CLUSTER="${CLUSTER_NAME:-claude-proxy}"

while [ $# -gt 0 ]; do
    case "$1" in
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

echo "===== Auto-Remediation ====="
echo "Cluster: $CLUSTER"
echo "Live: $LIVE"

echo "[Action] Restart unhealthy tasks:"
echo "  aws ecs stop-task --cluster $CLUSTER --task TASK_ARN"

echo "[Action] Scale up on high CPU:"
echo "  aws ecs update-service --cluster $CLUSTER --service api-service --desired-count +2"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    echo "(Would execute)"
else
    echo "(Dry run - not executing)"
fi
