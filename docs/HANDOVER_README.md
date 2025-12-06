# Claude Proxy Backend - Handover README

## Executive Summary

The Claude Proxy Backend is a production-ready FastAPI service that provides:
- Secure API gateway to Anthropic Claude models
- Queue-based async processing for reliability
- Streaming and synchronous response modes
- Enterprise-grade observability and security

## Architecture At-a-Glance

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ CloudFront  │────▶│     ALB      │────▶│  API (ECS)  │
│    + WAF    │     │              │     │             │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐     ┌──────▼──────┐
                    │   Workers    │◀────│     SQS     │
                    │    (ECS)     │     │             │
                    └──────┬───────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Secrets  │ │ Supabase │ │  Claude  │
        │ Manager  │ │    DB    │ │   API    │
        └──────────┘ └──────────┘ └──────────┘
```

## Owners & Contacts

| Role | Name | Contact |
|------|------|---------|
| Service Owner | REPLACE_ME | REPLACE_ME_EMAIL |
| On-Call Primary | REPLACE_ME | REPLACE_ME_PHONE |
| Security Lead | REPLACE_ME | REPLACE_ME_EMAIL |

## SLAs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Availability | 99.9% | 30-day rolling |
| P95 Latency | < 500ms | 5-minute windows |
| Error Rate | < 1% | 30-day rolling |

## Documentation Index

| Doc | Purpose |
|-----|---------|
| [Operational Runbook](OPERATIONAL_RUNBOOK_FULL.md) | Day-to-day operations |
| [On-Call Guide](ONCALL_AND_ESCALATION.md) | Incident response |
| [Deployment Runbook](DEPLOYMENT_RUNBOOK.md) | Release process |
| [CDN/WAF Runbook](CDN_WAF_RUNBOOK.md) | Edge configuration |
| [SLO Definitions](../infra/slo/SLO_AND_ALERTS.md) | Service objectives |

## Infrastructure State

- **Terraform State**: `s3://REPLACE_ME_BUCKET/terraform/state`
- **Secrets**: AWS Secrets Manager `claude-proxy-secrets`
- **ECR Repository**: `REPLACE_ME_ACCOUNT.dkr.ecr.REPLACE_ME_REGION.amazonaws.com/claude-proxy`
- **CloudWatch Logs**: `/ecs/claude-proxy`

## Quick Start

```bash
# Clone and setup
git clone REPLACE_ME_REPO_URL
cd claude-proxy
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run locally
cp .env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload

# Deploy (dry-run)
./infra/scripts/deploy_release.sh --env staging --image latest --strategy rolling
```
