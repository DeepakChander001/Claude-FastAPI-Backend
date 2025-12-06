# On-Call and Escalation Guide

## On-Call Rotation

| Week | Primary | Secondary |
|------|---------|-----------|
| Week 1 | REPLACE_ME | REPLACE_ME |
| Week 2 | REPLACE_ME | REPLACE_ME |
| Week 3 | REPLACE_ME | REPLACE_ME |
| Week 4 | REPLACE_ME | REPLACE_ME |

## Response Times

| Severity | Response | Resolution |
|----------|----------|------------|
| P1 Critical | 5 min | 1 hour |
| P2 High | 30 min | 4 hours |
| P3 Medium | 4 hours | 24 hours |

## P1 Response Actions

1. Acknowledge page immediately
2. Join #incidents Slack channel
3. Assess impact using dashboards
4. Apply mitigation (scale/rollback)
5. Page secondary if stuck > 15 min

## P2 Response Actions

1. Acknowledge within 30 minutes
2. Investigate root cause
3. Apply fix or schedule for next business day
4. Update ticket with findings

## Message Templates

### Slack Incident Start
```
🚨 *INCIDENT STARTED*
Service: Claude Proxy
Severity: P1/P2/P3
Impact: DESCRIBE_IMPACT
Owner: YOUR_NAME
Status: Investigating
```

### Slack Incident Resolved
```
✅ *INCIDENT RESOLVED*
Service: Claude Proxy
Duration: XX minutes
Root Cause: BRIEF_DESCRIPTION
Action Items: TICKET_LINK
```

## PagerDuty Webhook (Placeholder)

```
REPLACE_ME_PAGERDUTY_WEBHOOK
```

## Handoff Procedure

1. Review open incidents
2. Check monitoring dashboards
3. Update on-call schedule
4. Brief incoming on-call
