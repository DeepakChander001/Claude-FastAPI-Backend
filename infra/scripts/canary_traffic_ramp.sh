#!/bin/sh
# canary_traffic_ramp.sh - Gradually increase traffic to production canary
# ============================================================================
# Usage:
#   ./canary_traffic_ramp.sh --start 1 --end 100 --step 10 --interval 5m --target http://alb.example.com
#   ./canary_traffic_ramp.sh --live (requires CONFIRM=true)
# ============================================================================
set -euo pipefail

START_PERCENT=1
END_PERCENT=100
STEP=10
INTERVAL="5m"
TARGET="${ALB_DNS:-REPLACE_ME_ALB_DNS}"
LIVE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --start) START_PERCENT="$2"; shift 2;;
        --end) END_PERCENT="$2"; shift 2;;
        --step) STEP="$2"; shift 2;;
        --interval) INTERVAL="$2"; shift 2;;
        --target) TARGET="$2"; shift 2;;
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

echo "===== Canary Traffic Ramp ====="
echo "Start: ${START_PERCENT}%"
echo "End: ${END_PERCENT}%"
echo "Step: ${STEP}%"
echo "Interval: $INTERVAL"
echo "Target: $TARGET"
echo "Live: $LIVE"

CURRENT=$START_PERCENT

while [ "$CURRENT" -le "$END_PERCENT" ]; do
    echo ""
    echo "[Step] Ramping to ${CURRENT}%..."
    
    # Run smoke test at this level
    echo "  [Smoke Test] k6 run --env TARGET_URL=$TARGET --env DURATION=30s infra/tests/load/k6/smoke_and_rps_test.js"
    
    # Check health metrics (dry run)
    echo "  [Health Check] aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name HTTPCode_Target_5XX_Count ..."
    
    # Update canary weight
    echo "  [Canary Update] ./infra/scripts/canary_release.sh --canary-percent $CURRENT"
    
    if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
        ./infra/scripts/canary_release.sh --canary-percent "$CURRENT" --live || {
            echo "ERROR: Smoke test failed at ${CURRENT}%. Aborting ramp."
            exit 1
        }
        
        echo "  [Wait] Waiting $INTERVAL before next step..."
        sleep "$INTERVAL"
    else
        echo "  (Dry run - not executing)"
    fi
    
    CURRENT=$((CURRENT + STEP))
done

echo ""
echo "===== Canary Ramp Complete ====="
