# Deployment Checklist

## Pre-Deploy
- [ ] Secrets are configured in AWS Secrets Manager.
- [ ] Infrastructure is healthy (`terraform plan` shows no drift).
- [ ] Local smoke tests pass.
- [ ] Changelog entry added for this release.
- [ ] Docker image builds successfully.

## Deploy Steps
1. [ ] Build and push image: `./infra/scripts/deploy_release.sh --build --live`
2. [ ] Register task definition: Verified via `aws ecs describe-task-definition`
3. [ ] Deploy to staging: `./infra/scripts/deploy_release.sh --env staging --strategy rolling --live`
4. [ ] Run smoke tests: `./infra/scripts/smoke_test.sh --url http://STAGING_ALB`
5. [ ] Promote to production: `./infra/scripts/deploy_release.sh --env prod --strategy canary --live`

## Post-Deploy
- [ ] ALB target group shows healthy targets.
- [ ] CloudWatch dashboards show normal metrics.
- [ ] No new errors in CloudWatch Logs.
- [ ] SQS queue depth is stable.

## Rollback
If issues occur:
```bash
./infra/scripts/rollback_release.sh --live
```
