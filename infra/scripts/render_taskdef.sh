#!/bin/sh
set -e

# Render Task Definition Template
# Usage: ./render_taskdef.sh

TEMPLATE="infra/terraform/modules/ecs_service/task_definition_template.json"
OUTPUT="infra/ecs/rendered_task_def.json"

IMAGE="${IMAGE:-REPLACE_ME_IMAGE}"
REGION="${REGION:-REPLACE_ME_REGION}"
SECRETS_ARN="${SECRETS_ARN:-REPLACE_ME_SECRETS_ARN}"
EXECUTION_ROLE_ARN="${EXECUTION_ROLE_ARN:-REPLACE_ME_EXECUTION_ROLE_ARN}"
TASK_ROLE_ARN="${TASK_ROLE_ARN:-REPLACE_ME_TASK_ROLE_ARN}"

echo "Rendering task definition..."
echo "  IMAGE: $IMAGE"
echo "  REGION: $REGION"
echo "  SECRETS_ARN: $SECRETS_ARN"

# Substitute placeholders
sed -e "s|REPLACE_ME_IMAGE|$IMAGE|g" \
    -e "s|REPLACE_ME_REGION|$REGION|g" \
    -e "s|REPLACE_ME_SECRETS_ARN|$SECRETS_ARN|g" \
    -e "s|REPLACE_ME_EXECUTION_ROLE_ARN|$EXECUTION_ROLE_ARN|g" \
    -e "s|REPLACE_ME_TASK_ROLE_ARN|$TASK_ROLE_ARN|g" \
    "$TEMPLATE" > "$OUTPUT"

# Validate JSON
if command -v jq >/dev/null 2>&1; then
    jq . "$OUTPUT" > /dev/null && echo "JSON is valid."
else
    echo "Warning: jq not installed, skipping validation."
fi

echo "Rendered to $OUTPUT"
