# Service Definition and SLA

## Service Overview

**Claude Proxy Backend** provides managed access to Anthropic Claude models via a REST API with enterprise security, reliability, and observability.

## Consumer-Facing SLA

| Metric | Target | Measurement |
|--------|--------|-------------|
| Availability | 99.9% | Monthly |
| P95 Latency | < 500ms | Rolling 5-min |
| Error Rate | < 1% | Monthly |

### SLA Credits

| Availability | Credit |
|--------------|--------|
| < 99.9% | 10% |
| < 99.0% | 25% |
| < 95.0% | 50% |

## Maintenance Windows

- **Standard**: Sunday 02:00-06:00 UTC
- **Emergency**: As needed with minimum 1-hour notice
- **Excludes**: Planned maintenance does not count against SLA

## API Usage Policy

- Maximum request size: 1MB
- Maximum prompt tokens: 100,000
- Rate limit: 100 requests/minute (default)
- Burst limit: 200 requests
- Connection timeout: 60 seconds

## Onboarding Steps

1. Request access via REPLACE_ME_PORTAL
2. Complete security questionnaire
3. Sign data processing agreement
4. Receive API key
5. Test in staging environment
6. Production access granted

## Production API Key Request

To request a production API key:

1. Email: REPLACE_ME_EMAIL
2. Include:
   - Organization name
   - Expected usage (requests/day)
   - Use case description
   - Contact information

## Support

| Tier | Response Time | Contact |
|------|---------------|---------|
| P1 Critical | 15 min | REPLACE_ME_PAGER |
| P2 High | 4 hours | REPLACE_ME_EMAIL |
| P3 Normal | 24 hours | REPLACE_ME_EMAIL |
