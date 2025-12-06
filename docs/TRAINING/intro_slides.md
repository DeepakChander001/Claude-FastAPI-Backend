# Claude Proxy Backend - Onboarding Training

---

## Slide 1: Welcome (5 min)

### Claude Proxy Backend

**What you'll learn:**
- System architecture
- How to deploy
- How to monitor
- Common troubleshooting

> Speaker notes: Welcome attendees, introduce yourself, explain this is a 60-minute session.

---

## Slide 2: Architecture Overview (10 min)

### Key Components

- **API Service**: FastAPI on ECS Fargate
- **Queue**: SQS for async processing
- **Workers**: Process Claude API requests
- **Storage**: Supabase for persistence

> Speaker notes: Draw on whiteboard if possible. Explain request flow.

---

## Slide 3: Request Flow (5 min)

```
Client → CloudFront → ALB → API → SQS → Worker → Claude API
                                              ↓
                                         Supabase
```

> Speaker notes: Walk through sync vs async flows.

---

## Slide 4: Deployment Process (10 min)

### Steps

1. Push to `main` branch
2. CI builds Docker image
3. Deploy to staging (automatic)
4. Smoke tests run
5. Manual approval for production
6. Canary deployment

```bash
./infra/scripts/deploy_release.sh --env staging --strategy canary
```

> Speaker notes: Demo the dry-run output.

---

## Slide 5: Monitoring Dashboards (10 min)

### Key Metrics

- **Request Rate**: Requests per second
- **Latency**: P50, P95, P99
- **Error Rate**: 5xx responses
- **Queue Depth**: SQS messages

> Speaker notes: Show live dashboard. Point out SLO thresholds.

---

## Slide 6: Running Smoke Tests (5 min)

```bash
./infra/scripts/smoke_test.sh --url http://localhost:8000
```

### Expected Output

- GET /health → 200 OK
- POST /api/enqueue → 200/202

> Speaker notes: Run the command live.

---

## Slide 7: Common Issues (10 min)

| Issue | Solution |
|-------|----------|
| Health check failing | Check DB connection |
| Queue backlog | Scale workers |
| Rate limit errors | Adjust limits |
| OOM kills | Increase memory |

> Speaker notes: Share real examples from past incidents.

---

## Slide 8: Q&A (5 min)

### Questions?

- Slack: #claude-proxy-help
- Wiki: REPLACE_ME_WIKI_URL
- On-call: REPLACE_ME_PAGER

> Speaker notes: Address questions. Point to resources for self-learning.
