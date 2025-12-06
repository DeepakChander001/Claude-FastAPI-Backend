#!/bin/sh
# notify_release.sh - Send release notification
# ============================================================================
# Usage:
#   ./notify_release.sh --env staging --image myimage:abc123 --status success
# ============================================================================
set -e

ENV="staging"
IMAGE=""
STATUS="success"
DEPLOYER="${USER:-unknown}"
LIVE=false
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

while [ $# -gt 0 ]; do
    case "$1" in
        --env) ENV="$2"; shift 2;;
        --image) IMAGE="$2"; shift 2;;
        --status) STATUS="$2"; shift 2;;
        --live) LIVE=true; shift;;
        *) shift;;
    esac
done

COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build payload
PAYLOAD=$(cat <<EOF
{
  "text": "Deployment Notification",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Deployment Complete*"
      }
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Environment:* $ENV"},
        {"type": "mrkdwn", "text": "*Status:* $STATUS"},
        {"type": "mrkdwn", "text": "*Commit:* $COMMIT_SHA"},
        {"type": "mrkdwn", "text": "*Image:* $IMAGE"},
        {"type": "mrkdwn", "text": "*Deployer:* $DEPLOYER"},
        {"type": "mrkdwn", "text": "*Time:* $TIMESTAMP"}
      ]
    }
  ]
}
EOF
)

echo "===== Release Notification ====="
echo "$PAYLOAD" | python -m json.tool 2>/dev/null || echo "$PAYLOAD"

if [ "$LIVE" = true ] && [ -n "$SLACK_WEBHOOK" ]; then
    echo "Sending to Slack..."
    curl -s -X POST -H 'Content-type: application/json' \
        --data "$PAYLOAD" \
        "$SLACK_WEBHOOK"
else
    echo "(Dry run - not sending to Slack)"
fi
