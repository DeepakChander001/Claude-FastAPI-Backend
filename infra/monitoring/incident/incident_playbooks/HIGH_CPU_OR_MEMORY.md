# High CPU or Memory Incident Playbook

## Symptoms
- CloudWatch alarm: `CPU > 80%` or `Memory > 80%`
- Slow response times
- Task restarts

## Immediate Actions

### 1. Assess Scope
```bash
aws ecs describe-services --cluster claude-proxy --services api-service
aws cloudwatch get-metric-statistics --namespace AWS/ECS --metric-name CPUUtilization ...
```

### 2. Scale Up (if needed)
```bash
aws ecs update-service --cluster claude-proxy --service api-service --desired-count 4
```

### 3. Check for Memory Leaks
- Review recent deployments.
- Check container logs for OOM errors.
- Review application metrics for memory growth.

### 4. Temporary Throttling
If scaling doesn't help, reduce load:
- Increase rate limits.
- Return 503 for non-critical endpoints.

### 5. Collect Diagnostics
```bash
# Get container logs
aws logs get-log-events --log-group-name /ecs/claude-proxy --log-stream-name api/...

# Get task details
aws ecs describe-tasks --cluster claude-proxy --tasks TASK_ARN
```

## Resolution
- Identify root cause (traffic spike, memory leak, inefficient query).
- Deploy fix or adjust resources.
- Update runbook if needed.

## Post-Incident
- Open postmortem if SLO was breached.
- Review autoscaling policies.
