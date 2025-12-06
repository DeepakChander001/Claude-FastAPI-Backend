#!/bin/bash
set -e

# ------------------------------------------------------------------------
# Prepare ECS Task Definition
# Substitutes placeholders in task_definition.json
# ------------------------------------------------------------------------

TASK_DEF_TEMPLATE="infra/ecs/task_definition.json"
OUTPUT_FILE="task_definition_rendered.json"

# Placeholders (In CI, these would be env vars)
IMAGE_URI="${IMAGE_URI:-REPLACE_ME_IMAGE_URI}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-123456789012}"
SECRET_NAME="${SECRET_NAME:-my-app-secrets-prod}"

echo "Preparing task definition..."
echo "Image: $IMAGE_URI"
echo "Region: $AWS_REGION"
echo "Secret: $SECRET_NAME"

# Use sed to replace placeholders
# NOTE: In a real pipeline, use envsubst or jq for robust JSON handling.
sed -e "s|REPLACE_ME_IMAGE_URI|$IMAGE_URI|g" \
    -e "s|REPLACE_ME_REGION|$AWS_REGION|g" \
    -e "s|REPLACE_ME_ACCOUNT_ID|$AWS_ACCOUNT_ID|g" \
    -e "s|REPLACE_ME_SECRET_NAME|$SECRET_NAME|g" \
    "$TASK_DEF_TEMPLATE" > "$OUTPUT_FILE"

echo "Task definition rendered to $OUTPUT_FILE"

# Validate JSON syntax
if command -v jq &> /dev/null; then
    echo "Validating JSON..."
    jq . "$OUTPUT_FILE" > /dev/null
    echo "JSON is valid."
    
    echo "Container Environment:"
    jq '.containerDefinitions[0].environment' "$OUTPUT_FILE"
else
    echo "jq not found, skipping validation."
fi
