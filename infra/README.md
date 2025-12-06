# Infrastructure Plan

The following components are planned for the production infrastructure:

-   **Compute**: AWS ECS Fargate
    -   Serverless container execution for scalability and reduced management overhead.
-   **Load Balancing**: Application Load Balancer (ALB)
    -   Distributes incoming traffic across ECS tasks.
    -   Handles SSL termination.
-   **Secret Management**: AWS Secrets Manager
    -   Securely stores `ANTHROPIC_API_KEY` and database credentials.
-   **Caching / Message Broker**: Amazon ElastiCache (Redis)
    -   Used for rate limiting and potentially brokering streaming responses if needed.
-   **Database**: Amazon RDS (PostgreSQL)
    -   Persistent storage for user data, usage logs, etc.
