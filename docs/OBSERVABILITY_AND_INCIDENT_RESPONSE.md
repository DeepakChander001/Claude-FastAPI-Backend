# Observability and Incident Response

## Monitoring Stack

### Metrics
- **OpenTelemetry Collector**: Receives OTLP from app, exports to CloudWatch/Prometheus.
- **Prometheus**: Scrapes ECS tasks, ALB, node exporters.
- **CloudWatch**: Native AWS metrics for ECS, ALB, SQS.

### Logs
- **CloudWatch Logs**: ECS task logs with 90-day retention.
- **Structured JSON**: All logs in JSON format for querying.

### Traces
- **OpenTelemetry**: Distributed tracing with sampling.

---

## SLO Enforcement

| SLO | Target | Window |
|-----|--------|--------|
| Availability | 99.9% | 30 days |
| P95 Latency | < 500ms | Rolling |

Error budget = 0.1% of requests per month.

---

## Alert Routing

| Severity | Route | Response |
|----------|-------|----------|
| Critical | PagerDuty | 5 min |
| Warning | Slack | 30 min |
| Info | Slack | Best effort |

---

## Incident Handling

1. **Acknowledge** page within 5 minutes.
2. **Assess** scope and impact.
3. **Mitigate** using runbooks.
4. **Communicate** in #incidents.
5. **Resolve** and verify.
6. **Postmortem** within 48 hours.

---

## Cost Control

- Monthly budget alerts at 50%, 80%, 100%.
- Daily cost snapshots to S3.
- Tag enforcement for cost allocation.

---

## Runbook Links

- [High CPU/Memory](../infra/monitoring/incident/incident_playbooks/HIGH_CPU_OR_MEMORY.md)
- [API Key Leak](../infra/monitoring/incident/incident_playbooks/CLAUDE_API_KEY_LEAK.md)
- [Queue Backlog](../infra/monitoring/incident/incident_playbooks/QUEUE_BACKLOG.md)
- [Rollback](DEPLOYMENT_RUNBOOK.md)
