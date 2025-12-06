# Queue Backlog Incident Playbook

## Symptoms
- CloudWatch alarm: `SQS ApproximateNumberOfMessagesVisible > 1000`
- High message age in queue
- Worker service appears healthy but not keeping up

## Diagnosis

### 1. Check Queue Metrics
```bash
aws sqs get-queue-attributes \
    --queue-url REPLACE_ME_QUEUE_URL \
    --attribute-names All
```

### 2. Check Worker Health
```bash
aws ecs describe-services --cluster claude-proxy --services worker-service
aws logs filter-log-events --log-group-name /ecs/claude-proxy --filter-pattern "ERROR"
```

### 3. Check for Poison Messages
```bash
# Check DLQ
aws sqs get-queue-attributes --queue-url REPLACE_ME_DLQ_URL --attribute-names ApproximateNumberOfMessagesVisible
```

## Immediate Actions

### 4. Scale Up Workers
```bash
aws ecs update-service --cluster claude-proxy --service worker-service --desired-count 10
```

### 5. Increase Batch Size (if applicable)
Update worker configuration to process more messages per batch.

### 6. Apply Backpressure
If queue is growing due to client abuse:
- Tighten rate limits.
- Return 429 to slow down clients.

## Resolution

### 7. Process Backlog
Monitor until queue depth returns to normal.

### 8. Investigate Root Cause
- Was there a traffic spike?
- Did worker performance degrade?
- Were there many retries/failures?

## Post-Incident
- [ ] Review autoscaling policies.
- [ ] Consider increasing baseline worker count.
- [ ] Add alerts for message age, not just depth.
