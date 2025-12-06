#!/bin/sh
# cost_snapshot.sh - Generate daily cost snapshot report
# ============================================================================
# Required IAM: ce:GetCostAndUsage
# Usage:
#   ./cost_snapshot.sh              # Dry run
#   ./cost_snapshot.sh --live       # Execute
# ============================================================================
set -euo pipefail

LIVE=false
BUCKET="${COST_BUCKET:-REPLACE_ME_BUCKET}"
REGION="${AWS_REGION:-us-east-1}"

while [ $# -gt 0 ]; do
    case "$1" in
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="reports/cost-${YESTERDAY}.json"

mkdir -p reports

echo "===== Cost Snapshot ====="
echo "Date: $YESTERDAY"
echo "Report: $REPORT_FILE"
echo "Live: $LIVE"

# Cost Explorer command
CMD="aws ce get-cost-and-usage \
    --time-period Start=$YESTERDAY,End=$TODAY \
    --granularity DAILY \
    --metrics BlendedCost UnblendedCost \
    --group-by Type=TAG,Key=project \
    --output json"

echo "[Command] $CMD"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    $CMD > "$REPORT_FILE"
    echo "Report saved to $REPORT_FILE"
    
    # Optional: Upload to S3
    echo "[Upload] aws s3 cp $REPORT_FILE s3://$BUCKET/costs/"
    aws s3 cp "$REPORT_FILE" "s3://$BUCKET/costs/"
else
    echo "(Dry run - not executing)"
fi

echo "===== Done ====="
