#!/bin/sh
# monthly_ops_report.sh - Generate monthly operations report
# ============================================================================
# Dry-run by default. Use --live with CONFIRM=true to execute.
# ============================================================================
set -euo pipefail

LIVE=false
MONTH=$(date +%Y%m)
REPORT_DIR="reports/monthly-${MONTH}"

while [ $# -gt 0 ]; do
    case "$1" in
        --live) LIVE=true; shift;;
        --month) MONTH="$2"; REPORT_DIR="reports/monthly-${MONTH}"; shift 2;;
        *) shift;;
    esac
done

mkdir -p "$REPORT_DIR"

echo "===== Monthly Ops Report ====="
echo "Month: $MONTH"
echo "Report: $REPORT_DIR"
echo "Live: $LIVE"

# Gather artifacts
echo "[1] Gathering SBOM..."
SBOM_PATH="reports/sbom.json"
echo "  Source: $SBOM_PATH"

echo "[2] Gathering vulnerability report..."
VULN_PATH="reports/trivy.json"
echo "  Source: $VULN_PATH"

echo "[3] Gathering cost snapshot..."
COST_PATH="reports/cost-*.json"
echo "  Source: $COST_PATH"

# Generate summary
cat > "${REPORT_DIR}/summary.md" << EOF
# Monthly Operations Report - ${MONTH}

## Top Incidents
- REPLACE_ME_INCIDENT_1
- REPLACE_ME_INCIDENT_2

## Cost Summary
- Previous Month: \$REPLACE_ME
- This Month: \$REPLACE_ME
- Delta: REPLACE_ME%

## Availability
- Uptime: REPLACE_ME%
- SLO Target: 99.9%

## Action Items
- [ ] REPLACE_ME_ACTION_1
- [ ] REPLACE_ME_ACTION_2

## Attachments
- SBOM: sbom.json
- Vulnerabilities: trivy.json
- Cost: cost-${MONTH}.json
EOF

echo "[4] Summary created: ${REPORT_DIR}/summary.md"

# Zip artifacts
echo "[5] Creating archive..."
if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    cp "$SBOM_PATH" "$REPORT_DIR/" 2>/dev/null || echo "  (SBOM not found)"
    cp "$VULN_PATH" "$REPORT_DIR/" 2>/dev/null || echo "  (Vuln report not found)"
    tar -czf "${REPORT_DIR}.tar.gz" -C reports "monthly-${MONTH}"
    echo "  Archive: ${REPORT_DIR}.tar.gz"
    
    echo "[6] Upload to S3..."
    echo "  aws s3 cp ${REPORT_DIR}.tar.gz s3://REPLACE_ME_BUCKET/reports/"
else
    echo "  (Dry run - not archiving)"
    echo "[6] Would upload: aws s3 cp ${REPORT_DIR}.tar.gz s3://REPLACE_ME_BUCKET/reports/"
fi

echo "===== Report Complete ====="
