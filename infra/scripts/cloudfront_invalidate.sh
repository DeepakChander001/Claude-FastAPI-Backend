#!/bin/sh
# cloudfront_invalidate.sh - Invalidate CloudFront cache
# ============================================================================
# Usage:
#   ./cloudfront_invalidate.sh --dist-id EDFDVBD632BHDS5 --paths "/static/*,/index.html"
#   ./cloudfront_invalidate.sh --dist-id EDFDVBD632BHDS5 --paths "/*" --live
# ============================================================================
set -euo pipefail

DIST_ID=""
PATHS="/*"
LIVE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --dist-id) DIST_ID="$2"; shift 2;;
        --paths) PATHS="$2"; shift 2;;
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

if [ -z "$DIST_ID" ]; then
    DIST_ID="REPLACE_ME_DISTRIBUTION_ID"
fi

CALLER_REF=$(date +%s)

echo "===== CloudFront Invalidation ====="
echo "Distribution: $DIST_ID"
echo "Paths: $PATHS"
echo "Live: $LIVE"

# Build paths array
IFS=',' read -ra PATH_ARRAY <<< "$PATHS"
ITEMS=$(printf '"%s",' "${PATH_ARRAY[@]}" | sed 's/,$//')

echo "[Command] aws cloudfront create-invalidation \\"
echo "  --distribution-id $DIST_ID \\"
echo "  --invalidation-batch '{\"Paths\":{\"Quantity\":${#PATH_ARRAY[@]},\"Items\":[$ITEMS]},\"CallerReference\":\"$CALLER_REF\"}'"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    aws cloudfront create-invalidation \
        --distribution-id "$DIST_ID" \
        --invalidation-batch "{\"Paths\":{\"Quantity\":${#PATH_ARRAY[@]},\"Items\":[$ITEMS]},\"CallerReference\":\"$CALLER_REF\"}"
    
    echo "Invalidation created. Polling status..."
    echo "aws cloudfront get-invalidation --distribution-id $DIST_ID --id <INVALIDATION_ID>"
else
    echo "(Dry run - not executing)"
fi
