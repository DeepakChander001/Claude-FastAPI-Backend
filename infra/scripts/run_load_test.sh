#!/bin/sh
# run_load_test.sh - Run load tests against staging/production
# ============================================================================
# Usage:
#   ./run_load_test.sh --engine k6 --target http://localhost:8000
#   ./run_load_test.sh --engine locust --target http://staging.example.com --live
#
# Environment Variables:
#   TARGET_URL  - Target API URL
#   API_KEY     - API key for authentication
#   LOAD_ENGINE - k6 or locust (default: k6)
#   DEFAULT_RPS - Requests per second (default: 50)
# ============================================================================
set -euo pipefail

ENGINE="${LOAD_ENGINE:-k6}"
TARGET="${TARGET_URL:-REPLACE_ME_TARGET_URL}"
API_KEY="${API_KEY:-REPLACE_ME_API_KEY}"
DURATION="${DURATION:-1m}"
RPS="${DEFAULT_RPS:-50}"
LIVE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --engine) ENGINE="$2"; shift 2;;
        --target) TARGET="$2"; shift 2;;
        --duration) DURATION="$2"; shift 2;;
        --rps) RPS="$2"; shift 2;;
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="logs/load_tests/${TIMESTAMP}"
mkdir -p "$REPORT_DIR"

echo "===== Load Test Runner ====="
echo "Engine: $ENGINE"
echo "Target: $TARGET"
echo "Duration: $DURATION"
echo "RPS: $RPS"
echo "Live: $LIVE"
echo "Reports: $REPORT_DIR"

# Validate engine
if [ "$ENGINE" = "k6" ]; then
    if ! command -v k6 >/dev/null 2>&1; then
        echo "Warning: k6 not installed. Install from https://k6.io/"
    fi
    
    CMD="k6 run --env TARGET_URL=$TARGET --env API_KEY=$API_KEY --env DURATION=$DURATION --env RPS=$RPS --summary-export=${REPORT_DIR}/summary.json infra/tests/load/k6/smoke_and_rps_test.js"
    
elif [ "$ENGINE" = "locust" ]; then
    if ! command -v locust >/dev/null 2>&1; then
        echo "Warning: locust not installed. Install with: pip install locust"
    fi
    
    CMD="locust -f infra/tests/load/locust/locustfile.py --headless -u 10 -r 2 --run-time $DURATION --host $TARGET --csv=${REPORT_DIR}/locust"
else
    echo "Unknown engine: $ENGINE"
    exit 1
fi

echo "[Command] $CMD"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    echo "Executing load test..."
    eval "$CMD"
    
    # Compress results
    tar -czf "${REPORT_DIR}.tar.gz" -C "logs/load_tests" "$TIMESTAMP"
    echo "Results compressed to ${REPORT_DIR}.tar.gz"
else
    echo "(Dry run - not executing)"
fi

echo "===== Load Test Complete ====="
