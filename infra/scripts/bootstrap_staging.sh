#!/bin/sh
set -e

echo "===== Bootstrap Staging Environment ====="

# 1. Terraform Plan
echo "[1] Run Terraform Plan"
echo "    ./infra/scripts/terraform_run.sh"

# 2. Create Secrets
echo "[2] Create Secrets in AWS Secrets Manager"
echo "    aws secretsmanager put-secret-value --secret-id claude-proxy-secrets --secret-string '{...}'"

# 3. Push Image to ECR
echo "[3] Push Docker Image to ECR"
echo "    aws ecr get-login-password | docker login ..."
echo "    docker push REPLACE_ME_ACCOUNT.dkr.ecr.REPLACE_ME_REGION.amazonaws.com/claude-proxy:latest"

# 4. Register Task Definition
echo "[4] Register Task Definition"
echo "    aws ecs register-task-definition --cli-input-json file://infra/ecs/rendered_task_def.json"

# 5. Create/Update Service
echo "[5] Create/Update ECS Service"
echo "    aws ecs update-service --cluster claude-proxy --service api-service --force-new-deployment"

# 6. Run Smoke Tests
echo "[6] Run Smoke Tests"
echo "    ./infra/scripts/smoke_test.sh --url http://ALB_DNS"

echo "Staging bootstrap instructions complete."
