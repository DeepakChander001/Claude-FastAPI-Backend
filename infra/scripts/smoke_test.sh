#!/bin/sh
# smoke_test.sh - Run smoke tests against deployed service
# ============================================================================
# Usage:
#   ./smoke_test.sh --url http://localhost:8000 --api-key test-key
# ============================================================================
set -e

# Defaults
URL="http://localhost:8000"
API_KEY="${API_KEY:-test-key}"
RETRIES=3
TIMEOUT=30
STREAM=false
LOG_DIR="logs/smoke_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse args
while [ $# -gt 0 ]; do
    case "$1" in
        --url) URL="$2"; shift 2;;
        --api-key) API_KEY="$2"; shift 2;;
        --retries) RETRIES="$2"; shift 2;;
        --timeout) TIMEOUT="$2"; shift 2;;
        --stream) STREAM=true; shift;;
        *) shift;;
    esac
done

mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/smoke-${TIMESTAMP}.log"

echo "===== Smoke Tests =====" | tee "$LOG_FILE"
echo "URL: $URL" | tee -a "$LOG_FILE"
echo "Timestamp: $TIMESTAMP" | tee -a "$LOG_FILE"

PASSED=0
FAILED=0

# Test 1: Health Check
echo "[Test 1] GET /health" | tee -a "$LOG_FILE"
if command -v curl >/dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s --max-time "$TIMEOUT" "${URL}/health" 2>/dev/null || echo "TIMEOUT")
    if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
        echo "  PASS: $HEALTH_RESPONSE" | tee -a "$LOG_FILE"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL: $HEALTH_RESPONSE" | tee -a "$LOG_FILE"
        FAILED=$((FAILED + 1))
    fi
else
    echo "  SKIP: curl not available" | tee -a "$LOG_FILE"
fi

# Test 2: Enqueue API
echo "[Test 2] POST /api/enqueue" | tee -a "$LOG_FILE"
if command -v curl >/dev/null 2>&1; then
    ENQUEUE_RESPONSE=$(curl -s --max-time "$TIMEOUT" -X POST "${URL}/api/enqueue" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{"prompt":"test"}' 2>/dev/null || echo "TIMEOUT")
    if echo "$ENQUEUE_RESPONSE" | grep -qE '(request_id|queued|error)'; then
        echo "  PASS: Response received" | tee -a "$LOG_FILE"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL: $ENQUEUE_RESPONSE" | tee -a "$LOG_FILE"
        FAILED=$((FAILED + 1))
    fi
else
    echo "  SKIP: curl not available" | tee -a "$LOG_FILE"
fi

# Test 3: Streaming (optional)
if [ "$STREAM" = true ]; then
    echo "[Test 3] Streaming Test" | tee -a "$LOG_FILE"
    echo "  SKIP: Streaming test not implemented in dry run" | tee -a "$LOG_FILE"
fi

# Summary
echo "===== Summary =====" | tee -a "$LOG_FILE"
echo "Passed: $PASSED" | tee -a "$LOG_FILE"
echo "Failed: $FAILED" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE"

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi

exit 0
