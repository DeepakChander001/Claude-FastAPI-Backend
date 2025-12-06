# AWS Infrastructure Runbook

## Prerequisites
1.  **VPC**: Use an existing VPC or create one.
2.  **Subnets**: At least 2 public subnets (ALB) and 2 private subnets (ECS).
3.  **IAM Permissions**: User needs permission to create ECS, ALB, SQS, Secrets Manager, IAM roles.
4.  **AWS CLI**: Installed and configured.
5.  **Terraform**: v1.0+.

## Deployment Sequence

### 1. Configure Variables
Edit `infra/terraform/variables.tf` and replace all `REPLACE_ME` placeholders.

### 2. Initialize Terraform
```bash
cd infra/terraform
terraform init
```

### 3. Plan Infrastructure
```bash
terraform plan -out=plans/plan.tfplan
```
Review the plan carefully.

### 4. Apply Infrastructure
```bash
CONFIRM=true ./infra/scripts/terraform_run.sh --apply
```

### 5. Create Secrets
```bash
aws secretsmanager put-secret-value \
  --secret-id claude-proxy-secrets \
  --secret-string '{"ANTHROPIC_API_KEY":"real-key",...}'
```

### 6. Push Docker Image
```bash
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/claude-proxy:latest
```

### 7. Render and Register Task Definition
```bash
./infra/scripts/render_taskdef.sh
aws ecs register-task-definition --cli-input-json file://infra/ecs/rendered_task_def.json
```

### 8. Deploy Services
```bash
aws ecs update-service --cluster claude-proxy --service api-service --force-new-deployment
```

### 9. Run Smoke Tests
```bash
./infra/scripts/smoke_test.sh --url http://ALB_DNS
```

## Rollback
If deployment fails:
1.  Identify the last stable task revision.
2.  `aws ecs update-service --task-definition family:OLD_REVISION --force-new-deployment`

## Cost Control
See `docs/AWS_COST_CONTROL.md`.
