# Chaos Testing Playbook

## Scope
**Staging environment only.** Never run chaos tests in production without explicit approval.

## Prerequisites
- Staging environment is healthy.
- Traffic is diverted or synthetic.
- Monitoring dashboards are open.
- Rollback plan is ready.

---

## Test 1: Kill Worker Task

**Objective**: Verify SQS redrive and worker restart behavior.

### Docker Compose (Local)
```bash
# Identify worker container
docker ps | grep worker

# Kill worker container
docker kill <worker_container_id>

# Observe: Worker should restart, queue messages should not be lost.
```

### ECS (Staging - DRY RUN)
```bash
# List tasks
aws ecs list-tasks --cluster REPLACE_ME_CLUSTER --service worker-service

# Stop a task (DRY RUN - prints only)
echo "aws ecs stop-task --cluster REPLACE_ME_CLUSTER --task REPLACE_ME_TASK_ARN"

# Expected: ECS will start a new task, SQS messages will be redelivered.
```

---

## Test 2: Throttle Network

**Objective**: Simulate network latency or packet loss.

### Using tc (Linux)
```bash
# Add 200ms latency to outbound traffic
sudo tc qdisc add dev eth0 root netem delay 200ms

# Remove after test
sudo tc qdisc del dev eth0 root netem
```

### Docker (Local)
```bash
docker run --rm -it --network container:<target_container> --cap-add NET_ADMIN nicolaka/netshoot tc qdisc add dev eth0 root netem delay 200ms
```

---

## Test 3: Database Connection Exhaustion

**Objective**: Verify connection pool behavior under load.

```bash
# Run load test with high concurrency
k6 run --vus 100 --duration 5m infra/tests/load/k6/smoke_and_rps_test.js
```

---

## Expected Recovery

| Test | Expected Behavior |
|------|-------------------|
| Worker Kill | New task starts within 60s, no message loss |
| Network Throttle | Requests slow but don't fail (with retries) |
| Connection Exhaustion | Graceful degradation, error responses |

---

## Safety Checklist

- [ ] Running in staging only.
- [ ] Real traffic diverted.
- [ ] Team notified.
- [ ] Rollback commands ready.
