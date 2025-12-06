# On-Call Guide

## Escalation Policy

| Severity | Response Time | Action |
|----------|---------------|--------|
| P1 (Critical) | 5 min | Page on-call, wake up if needed |
| P2 (High) | 30 min | Page during business hours |
| P3 (Medium) | 4 hours | Slack notification |

## Contact List

| Role | Name | Contact |
|------|------|---------|
| Primary On-Call | REPLACE_ME | REPLACE_ME_PHONE |
| Secondary On-Call | REPLACE_ME | REPLACE_ME_PHONE |
| Engineering Lead | REPLACE_ME | REPLACE_ME_PHONE |

## When to Page

**Page immediately for:**
- Service completely down
- 5xx error rate > 10%
- Security incident
- Data loss or corruption

**Do NOT page for:**
- Single task restart
- Brief latency spike (< 5 min)
- Scheduled maintenance

## Runbook Links

- [High CPU/Memory](incident_playbooks/HIGH_CPU_OR_MEMORY.md)
- [API Key Leak](incident_playbooks/CLAUDE_API_KEY_LEAK.md)
- [Queue Backlog](incident_playbooks/QUEUE_BACKLOG.md)
- [Rollback](../../runbooks/ROLLBACK_PLAYBOOK.md)

## Paging Etiquette

1. Acknowledge the page within 5 minutes.
2. If you can't respond, escalate immediately.
3. Communicate in #incidents Slack channel.
4. Update status page if customer-facing.

## Forgiveness Windows

During these times, alerts are suppressed:
- Scheduled maintenance windows
- First 15 min after deploy (some flapping expected)

## Post-Incident

1. Document timeline in incident ticket.
2. Schedule postmortem if SLO breached.
3. Hand off to next on-call if unresolved.
