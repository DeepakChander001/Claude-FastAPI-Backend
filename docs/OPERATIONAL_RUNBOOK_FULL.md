# Operational Runbook

## Daily Checks

- [ ] Review CloudWatch dashboard for anomalies
- [ ] Check SQS queue depth < 100
- [ ] Verify all ECS tasks healthy
- [ ] Review error rate in logs

```bash
# Check service health
curl -s http://REPLACE_ME_ALB_DNS/health | jq
```

## Weekly Maintenance

- [ ] Review cost trends
- [ ] Check for dependency updates
- [ ] Review DLQ for failed messages
- [ ] Rotate logs if needed

## Incident Triage Flow

1. **Acknowledge** alert within 5 minutes
2. **Assess** scope: single task or full outage?
3. **Mitigate** using playbooks below
4. **Communicate** in #incidents
5. **Resolve** and document

## Escalation Matrix

| Severity | Response | Escalate After |
|----------|----------|----------------|
| P1 | 5 min | 15 min |
| P2 | 30 min | 2 hours |
| P3 | 4 hours | 24 hours |

## Scheduled Tasks

| Task | Frequency | Owner |
|------|-----------|-------|
| Secret rotation | 90 days | Security |
| RDS backup verify | Monthly | Ops |
| Dependency scan | Weekly | CI/CD |
| Cost review | Monthly | Engineering |

## Deployment Policy

1. All changes via PR with CI passing
2. Deploy to staging first
3. Run smoke tests before production
4. Use canary deployments for production
5. Rollback if error rate > 5%

## Common Commands

```bash
# View logs
aws logs tail /ecs/claude-proxy --follow

# Scale service
aws ecs update-service --cluster claude-proxy --service api-service --desired-count 4

# Rollback
./infra/scripts/rollback_release.sh --live

# Smoke test
./infra/scripts/smoke_test.sh --url http://REPLACE_ME_ALB_DNS
```

## Contact List

| Role | Contact |
|------|---------|
| On-Call | REPLACE_ME_PAGER |
| Slack | #claude-proxy-ops |
| Email | REPLACE_ME_EMAIL |
