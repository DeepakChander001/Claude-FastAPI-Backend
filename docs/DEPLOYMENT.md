# Production Deployment Runbook

## Architecture Overview

The application is deployed as a containerized service on **AWS ECS Fargate**, providing a serverless, scalable compute environment.

```mermaid
graph LR
    Client --> ALB[Application Load Balancer]
    ALB --> Service[ECS Service (Fargate)]
    Service --> Task1[Task Replica 1]
    Service --> Task2[Task Replica 2]
    Task1 --> Secrets[AWS Secrets Manager]
    Task1 --> Supabase[Supabase DB]
    Task1 --> Anthropic[Anthropic API]
```

-   **Compute**: ECS Fargate (Serverless containers).
-   **Networking**: Tasks run in private subnets; ALB sits in public subnets.
-   **Secrets**: Managed via AWS Secrets Manager.
-   **Persistence**: Supabase (PostgreSQL) for request logs.
-   **Streaming**: Direct SSE connection from client to ALB to Task.

## Security & Networking

1.  **VPC**: Use a VPC with Public and Private subnets.
2.  **Security Groups**:
    -   **ALB SG**: Allow Inbound HTTP/HTTPS (0.0.0.0/0).
    -   **Task SG**: Allow Inbound TCP 8000 **only from ALB SG**.
3.  **IAM Roles**:
    -   **Execution Role**: Minimal permissions to pull images (ECR) and fetch secrets (Secrets Manager).
    -   **Task Role**: Minimal permissions for any other AWS services (e.g., S3, Bedrock) if added later.

## Logging & Observability

-   **Logs**: Application logs are sent to **CloudWatch Logs** (`/ecs/claude-proxy-service`).
-   **Metrics**: Monitor `CPUUtilization` and `MemoryUtilization` in CloudWatch.
-   **Tracing**: (Optional) Enable AWS X-Ray sidecar for distributed tracing if latency issues arise.
-   **Alerts**: Set alarms for:
    -   `5xx` Error Rate > 1%
    -   `CPUUtilization` > 85% (Scale out triggers at 70%)
    -   `UnhealthyHostCount` > 0

## Autoscaling Strategy

We use **Target Tracking Scaling** based on CPU.
-   **Metric**: `ECSServiceAverageCPUUtilization`
-   **Target**: 70%
-   **Min Capacity**: 2 tasks (High Availability)
-   **Max Capacity**: 10 tasks (Cost control)
-   **Cooldown**: 60 seconds scale out, 300 seconds scale in.

*Note: For streaming workloads, CPU is a good proxy, but consider "Active Connections" custom metric if CPU usage is low during waiting periods.*

## Deployment Strategy

**Rolling Update** (Default ECS behavior):
1.  New task definition revision is registered.
2.  ECS starts new tasks (Green).
3.  ALB health checks pass (`/health`).
4.  ECS drains old tasks (Blue).
5.  **Health Check**: Ensure `/health` returns 200 OK quickly.
6.  **Min Healthy Percent**: 100% (Ensure capacity doesn't drop below min during deploy).

## Cost Considerations

-   **Fargate Spot**: Consider using Fargate Spot for non-critical workloads to save up to 70%.
-   **NAT Gateway**: Tasks in private subnets need NAT Gateway to reach Anthropic/Supabase. This has a fixed hourly cost.
-   **Circuit Breakers**: The application handles API errors gracefully, but ensure AWS budget alerts are set.

## Rollback Plan

If a deployment fails or introduces a bug:
1.  **Identify**: High error rate or failed health checks.
2.  **Revert**:
    -   Via Terraform: Revert `container_image` var to previous tag and `terraform apply`.
    -   Via Console: Update Service to use previous Task Definition revision.
3.  **Verify**: Check CloudWatch logs and `/health` endpoint.

## Incident Runbook

**Scenario: High Latency / Stuck Streams**
1.  Check CloudWatch Logs for "Streaming error" or "Timeout".
2.  Check Supabase dashboard for database locks or performance issues.
3.  Check Anthropic status page.
4.  If tasks are stuck, force a new deployment (`aws ecs update-service --force-new-deployment`).

**Scenario: Secrets Rotation**
1.  Update secret in AWS Secrets Manager.
2.  Restart ECS tasks (Secrets are injected as env vars at startup).
    -   `aws ecs update-service --service claude-proxy-service --cluster claude-proxy-cluster --force-new-deployment`
