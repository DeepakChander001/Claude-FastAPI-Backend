#!/bin/sh
# create_dns_record.sh - Create Route53 DNS record
# ============================================================================
# Usage:
#   ./create_dns_record.sh --zone-id Z123 --name api.example.com --value d123.cloudfront.net
#   ./create_dns_record.sh --zone-id Z123 --name api.example.com --value d123.cloudfront.net --live
# ============================================================================
set -euo pipefail

ZONE_ID="REPLACE_ME_ZONE_ID"
NAME=""
VALUE=""
TTL=300
LIVE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --zone-id) ZONE_ID="$2"; shift 2;;
        --name) NAME="$2"; shift 2;;
        --value) VALUE="$2"; shift 2;;
        --ttl) TTL="$2"; shift 2;;
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

if [ -z "$NAME" ]; then
    NAME="api.REPLACE_ME_DOMAIN.com"
fi

if [ -z "$VALUE" ]; then
    VALUE="REPLACE_ME_CLOUDFRONT_DOMAIN.cloudfront.net"
fi

echo "===== Create DNS Record ====="
echo "Zone ID: $ZONE_ID"
echo "Name: $NAME"
echo "Value: $VALUE"
echo "Live: $LIVE"

# Build change batch JSON
CHANGE_BATCH=$(cat <<EOF
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$NAME",
        "Type": "CNAME",
        "TTL": $TTL,
        "ResourceRecords": [
          {"Value": "$VALUE"}
        ]
      }
    }
  ]
}
EOF
)

echo "[Change Batch JSON]"
echo "$CHANGE_BATCH"

echo "[Command] aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch '...'"

if [ "$LIVE" = true ] && [ "${CONFIRM:-false}" = "true" ]; then
    aws route53 change-resource-record-sets \
        --hosted-zone-id "$ZONE_ID" \
        --change-batch "$CHANGE_BATCH"
    echo "DNS record created/updated."
else
    echo "(Dry run - not executing)"
fi
