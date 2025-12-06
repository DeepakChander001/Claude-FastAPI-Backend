# Deployment Preparation Runbook

## 1. Container Image

### Building for Production
Use the multi-stage `infra/docker/Dockerfile.prod` to ensure a small, secure image.

```bash
docker build -f infra/docker/Dockerfile.prod -t claude-proxy:latest .
```

### ECR Tagging
Tag images with the Git SHA for traceability.
```bash
docker tag claude-proxy:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/claude-proxy:git-sha
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/claude-proxy:git-sha
```

## 2. ECS Task Definition

The task definition (`infra/ecs/task_definition.json`) defines how the container runs.

-   **Secrets**: Mapped from AWS Secrets Manager. Ensure the Task Execution Role has `secretsmanager:GetSecretValue` permission.
-   **Logs**: Configured for CloudWatch Logs (`awslogs`).
-   **Resources**: Default is 0.5 vCPU / 1 GB RAM. Adjust based on load testing.

## 3. Graceful Shutdown

We use `tini` as the init process and `gunicorn` to manage workers.
-   **SIGTERM**: ECS sends SIGTERM to stop a task.
-   **Timeout**: Gunicorn is configured with a timeout.
-   **Draining**: The ALB stops sending new requests. Existing requests have `stopTimeout` (default 30s) to complete.

## 4. Autoscaling

Scale based on **Queue Depth** (custom metric) or **CPU**.

### Queue Depth Scaling (Recommended)
1.  Publish `QueueLength` to CloudWatch (e.g., via a sidecar or Lambda).
2.  Create a Target Tracking Policy:
    -   Target: 5 messages per visible worker.
    -   Scale Out Cooldown: 60s.
    -   Scale In Cooldown: 300s.

## 5. Canary Deployment

1.  Deploy new Task Definition.
2.  ECS updates the service.
3.  New tasks start; ALB health checks (`/health`) must pass.
4.  Old tasks are drained and stopped.

## 6. Rollback

If a deployment fails:
1.  **Identify**: Check CloudWatch Logs / Sentry.
2.  **Revert**: Update Service to use the *previous* Task Definition Revision.
    ```bash
    aws ecs update-service --service claude-proxy --task-definition claude-proxy:PREV_REV
    ```
3.  **Verify**: Run smoke tests.

## 7. Cost Control

-   **Fargate Spot**: Use Fargate Spot for workers to save up to 70%.
-   **Rightsizing**: Monitor CPU/Memory utilization. If < 50%, reduce task size.
-   **Budgets**: Set up AWS Budgets to alert on forecast overage.
