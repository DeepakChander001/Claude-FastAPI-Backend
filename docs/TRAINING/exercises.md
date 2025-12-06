# Training Exercises

## Exercise 1: Run Local Stack (15 min)

### Steps
1. Clone the repository
2. Create virtual environment
3. Copy `.env.example` to `.env`
4. Start the server

```bash
git clone REPLACE_ME_REPO
cd claude-proxy
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Verification
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

---

## Exercise 2: Deploy to Staging (Dry-Run) (10 min)

### Steps
1. Review the deploy script
2. Run in dry-run mode

```bash
./infra/scripts/deploy_release.sh --env staging --image test:latest --strategy rolling
```

### Expected Output
- Script prints AWS CLI commands
- Does NOT execute (dry-run)

---

## Exercise 3: Run Smoke Test (5 min)

```bash
./infra/scripts/smoke_test.sh --url http://localhost:8000
```

### Expected Output
- 2 tests passed
- Log file created in `logs/smoke_tests/`

---

## Exercise 4: Simulate Worker Backlog (10 min)

### Steps
1. Open two terminals
2. In terminal 1, stop the worker (if running)
3. In terminal 2, send multiple requests

```bash
# Terminal 2 - Send requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/enqueue \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Test"}'
done
```

### Observation
- Queue depth increases
- Requests remain pending

---

## Exercise 5: Rotate a Secret (Dry-Run) (10 min)

```bash
# View current secret
aws secretsmanager get-secret-value --secret-id claude-proxy-secrets

# Rotate (dry-run - just print)
echo "aws secretsmanager put-secret-value --secret-id claude-proxy-secrets --secret-string '...'"
```

---

## Exercise 6: Perform a Rollback (Dry-Run) (5 min)

```bash
./infra/scripts/rollback_release.sh
```

### Expected Output
- Script prints previous task definition
- Shows `aws ecs update-service` command

---

## Exercise 7: Read the Dashboard (5 min)

1. Open Grafana/CloudWatch
2. Find the API Overview dashboard
3. Identify: request rate, P95 latency, error rate
4. Note the SLO threshold lines

### Discussion
- When would you scale up?
- What error rate triggers an alert?
