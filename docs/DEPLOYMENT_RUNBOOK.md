# Deployment Runbook

## Overview
This runbook covers deploying the Claude Proxy backend to AWS ECS.

## Pre-Deploy Checklist
1.  **Secrets**: Verify secrets exist in AWS Secrets Manager.
2.  **Infrastructure**: Run `terraform plan` to ensure no drift.
3.  **Local Tests**: Run `pytest tests/` and verify all pass.
4.  **Build**: Verify Docker image builds locally.

## Environment Variables
Set these before running deploy scripts:
```bash
export AWS_REGION=us-east-1
export ECR_REPO=123456789.dkr.ecr.us-east-1.amazonaws.com/claude-proxy
export CLUSTER_NAME=claude-proxy
export SERVICE_NAME_API=api-service
export ALB_DNS=my-alb-123.us-east-1.elb.amazonaws.com
export CONFIRM=true  # Required for live deployment
```

## Deployment Flow

### 1. Build and Push Image
```bash
./infra/scripts/deploy_release.sh --build --image myimage:latest --live
```

### 2. Deploy to Staging (Rolling)
```bash
./infra/scripts/deploy_release.sh --env staging --strategy rolling --live
```

### 3. Run Smoke Tests
```bash
./infra/scripts/smoke_test.sh --url http://$ALB_DNS
```

### 4. Deploy to Production (Canary)
```bash
./infra/scripts/deploy_release.sh --env prod --strategy canary --live
```

### 5. Promote Canary
```bash
./infra/scripts/promote_canary.sh --from 1 --to 10 --live
./infra/scripts/promote_canary.sh --from 10 --to 100 --live
```

## Rollback
If issues occur:
```bash
./infra/scripts/rollback_release.sh --live
```

## Post-Deploy Validation
1.  Check ALB Target Health: `aws elbv2 describe-target-health --target-group-arn $TG_ARN`
2.  Check CloudWatch Logs for errors.
3.  Monitor SQS queue depth.

## Cost Safety
-   If CloudWatch alarms fire, pause promotion.
-   Use `--strategy canary` to limit blast radius.
