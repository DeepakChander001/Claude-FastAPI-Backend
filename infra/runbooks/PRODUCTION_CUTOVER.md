# Production Cutover Runbook

## Overview
This runbook covers the complete production cutover process for the Claude Proxy backend.

---

## Pre-Cutover Checklist

### Infrastructure
- [ ] Terraform plan shows no pending changes.
- [ ] ECS cluster is healthy with desired task count.
- [ ] ALB target groups show healthy targets.
- [ ] CloudFront distribution is deployed (if applicable).
- [ ] WAF is in COUNT mode with no false positives.

### Application
- [ ] Docker image pushed to ECR with verified tag.
- [ ] Secrets configured in AWS Secrets Manager.
- [ ] Environment variables validated.
- [ ] Smoke tests passing against staging.

### Monitoring
- [ ] CloudWatch alarms configured.
- [ ] Dashboards accessible.
- [ ] Log ingestion working.
- [ ] On-call rotation confirmed.

### Communication
- [ ] Team notified of cutover window.
- [ ] Support team on standby.
- [ ] Customer communication prepared (if needed).

---

## Cutover Steps

### Step 1: Final Staging Validation (T-30 min)
```bash
./infra/scripts/smoke_test.sh --url http://STAGING_ALB_DNS
./infra/scripts/run_load_test.sh --engine k6 --target http://STAGING_ALB_DNS --duration 5m --live
```

### Step 2: Deploy to Production (T-0)
```bash
# Register new task definition
aws ecs register-task-definition --cli-input-json file://infra/ecs/rendered_task_def.json

# Update service (1% canary)
./infra/scripts/canary_release.sh --canary-percent 1 --live
```

### Step 3: Initial Smoke Test (T+5 min)
```bash
./infra/scripts/smoke_test.sh --url http://PRODUCTION_ALB_DNS
```

### Step 4: Ramp Traffic (T+10 min)
```bash
./infra/scripts/canary_traffic_ramp.sh --start 1 --end 100 --step 25 --interval 5m --live
```

### Step 5: Monitor (T+30 min)
- Watch CloudWatch dashboards for 30 minutes.
- Verify error rates are within SLO.
- Check SQS queue depth is stable.

---

## Rollback Triggers

**Immediately rollback if:**
- 5xx error rate > 5% for 2 minutes.
- P95 latency > 2000ms for 5 minutes.
- SQS queue depth increasing continuously.
- Health check failures > 50%.

### Rollback Command
```bash
./infra/scripts/rollback_release.sh --live
```

---

## Post-Cutover Verification

- [ ] Error rate < 1% for 1 hour.
- [ ] P95 latency < 500ms.
- [ ] No customer complaints.
- [ ] Logs show normal traffic patterns.

---

## Communication Checklist

- [ ] Update #releases Slack channel.
- [ ] Close deployment ticket.
- [ ] Update runbook if any issues.
