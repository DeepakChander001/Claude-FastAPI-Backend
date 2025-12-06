# Deployment Notes

## Local vs. Production
-   **Local (Docker Compose)**:
    -   Uses a mounted volume (`./:/app`) for hot-reloading code changes.
    -   Runs `uvicorn` with `--reload`.
    -   Redis runs as a container in the same network.
    -   Environment variables are read from `.env`.

-   **Production (AWS ECS Fargate)**:
    -   Code is baked into the image (no volume mounts).
    -   Runs `uvicorn` via the `CMD` in `Dockerfile` (no reload).
    -   Redis should be an external AWS ElastiCache instance.
    -   Secrets (API keys, DB URLs) must be injected via AWS Secrets Manager, NOT `.env` files.
    -   Load balancing is handled by AWS ALB, not exposed ports directly.

## Reminder
Always build fresh images for production deployment to ensure all dependencies and code are up to date.
