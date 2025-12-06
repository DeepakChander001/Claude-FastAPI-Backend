# Maintenance Schedule (12 Months)

## Monthly Ops Checklist

- [ ] Review cost report
- [ ] Check vulnerability scan results
- [ ] Verify backup restore capability
- [ ] Review SLO compliance
- [ ] Update dependencies (minor versions)

## Maintenance Windows

**Standard Window**: Sunday 02:00-06:00 UTC  
**Emergency Window**: As needed with 1-hour notice

## Annual Calendar

| Month | Task | Owner |
|-------|------|-------|
| Jan | Q1 planning, dependency audit | Engineering |
| Feb | Regular maintenance | Ops |
| Mar | Q1 pen test | Security |
| Apr | Q2 planning | Engineering |
| May | Regular maintenance | Ops |
| Jun | Q2 pen test, mid-year review | Security |
| Jul | Q3 planning | Engineering |
| Aug | Regular maintenance | Ops |
| Sep | Q3 pen test | Security |
| Oct | Q4 planning | Engineering |
| Nov | Regular maintenance | Ops |
| Dec | Q4 pen test, annual review | Security |

## Backup Schedule

| Resource | Frequency | Retention | Verify |
|----------|-----------|-----------|--------|
| RDS | Daily | 35 days | Monthly |
| Secrets | On change | Versioned | Quarterly |
| Terraform state | On apply | Versioned | Monthly |

## Dependency Updates

| Type | Frequency | Process |
|------|-----------|---------|
| Security patches | Immediate | PR → staging → prod |
| Minor versions | Monthly | Batch in maintenance window |
| Major versions | Quarterly | With testing plan |

## Pen Test Windows

- Q1: March 15-31
- Q2: June 15-30
- Q3: September 15-30
- Q4: December 1-15
