# SLO and Alerting Definitions

## Service Level Objectives (SLOs)

### Availability SLO
| Metric | Target | Window |
|--------|--------|--------|
| Successful `POST /api/enqueue` | 99.9% | 30 days |
| Successful `GET /health` | 99.99% | 30 days |

### Latency SLO
| Metric | Target | Percentile |
|--------|--------|------------|
| `POST /api/enqueue` response time | < 500ms | p95 |
| `POST /api/enqueue` response time | < 1000ms | p99 |
| `GET /health` response time | < 100ms | p99 |

---

## Error Budget

Monthly error budget = `(1 - SLO) × total requests`

For 99.9% availability:
- Allowed failures per 1M requests: **1,000**
- Allowed downtime per month: **~43 minutes**

### Burn Rate Alerts

| Burn Rate | Alert Severity | Action |
|-----------|----------------|--------|
| 14.4x (budget exhausted in 1h) | Critical | Page on-call immediately |
| 6x (budget exhausted in 4h) | High | Page during business hours |
| 1x (budget exhausted in 30d) | Warning | Investigate this week |

---

## CloudWatch Alarms

### Critical Alarms (Page Immediately)
```
Metric: HTTPCode_Target_5XX_Count
Threshold: > 10 in 5 minutes
Action: SNS → PagerDuty → REPLACE_ME_ONCALL_TEAM
```

### Warning Alarms (Investigate)
```
Metric: TargetResponseTime (p95)
Threshold: > 500ms for 10 minutes
Action: SNS → Slack #alerts
```

### SQS Queue Depth
```
Metric: ApproximateNumberOfMessagesVisible
Threshold: > 1000 for 5 minutes
Action: Trigger autoscaling or alert
```

---

## Escalation Matrix

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| P1 (Critical) | 5 minutes | On-call → Engineering Lead → VP |
| P2 (High) | 30 minutes | On-call → Team Lead |
| P3 (Medium) | 4 hours | Assigned engineer |

---

## Mitigation Tactics

When SLO is breached:
1. **Throttle**: Reduce rate limits temporarily.
2. **Scale Up**: Increase ECS task count.
3. **Disable Non-Essential**: Turn off optional features.
4. **Rollback**: Revert to previous stable version.
