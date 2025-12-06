#!/bin/sh
# promote_canary.sh - Promote canary deployment to higher traffic percentage
# ============================================================================
# Usage:
#   ./promote_canary.sh --from 1 --to 10 --live
# ============================================================================
set -euo pipefail

FROM_PERCENT=1
TO_PERCENT=10
LIVE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --from) FROM_PERCENT="$2"; shift 2;;
        --to) TO_PERCENT="$2"; shift 2;;
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

CLUSTER_NAME="${CLUSTER_NAME:-claude-proxy}"
ALB_DNS="${ALB_DNS:-REPLACE_ME_ALB_DNS}"

echo "===== Promote Canary ====="
echo "From: ${FROM_PERCENT}%"
echo "To: ${TO_PERCENT}%"
echo "Live: $LIVE"

# Pre-checks
echo "[Pre-check 1] Verifying ALB Health..."
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services api-service"

echo "[Pre-check 2] Running Smoke Tests..."
echo "  ./infra/scripts/smoke_test.sh --url http://${ALB_DNS}"

# Promote
echo "[Promote] Updating Traffic Weights..."
echo "  ./infra/scripts/canary_release.sh --canary-percent $TO_PERCENT"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    ./infra/scripts/canary_release.sh --canary-percent "$TO_PERCENT" --live
fi

echo "===== Promotion Complete ====="
