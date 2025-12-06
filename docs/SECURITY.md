# Security Runbook

## Authentication

The application supports two authentication modes, controlled by `AUTH_MODE` in `.env`.

### 1. API Key (`AUTH_MODE=api_key`)
-   **Mechanism**: Clients must send `X-API-Key: <key>` header.
-   **Validation**: Keys are validated against `ALLOWED_API_KEYS` (comma-separated list).
-   **Use Case**: Service-to-service communication, simple clients.

### 2. JWT (`AUTH_MODE=jwt`)
-   **Mechanism**: Clients must send `Authorization: Bearer <token>` header.
-   **Validation**: Tokens are verified using `HS256` signature with `JWT_SECRET`.
-   **Use Case**: User-facing applications, frontend integration.

### Switching Modes
1.  Update `AUTH_MODE` in `.env` or AWS Secrets Manager.
2.  Restart the application.

## Rate Limiting

We use a **Token Bucket** algorithm to limit request rates.

-   **Configuration**: `RATE_LIMIT_PER_MINUTE` (default: 60).
-   **Headers**:
    -   `X-RateLimit-Limit`: Total requests allowed per window.
    -   `X-RateLimit-Remaining`: Requests remaining.
    -   `Retry-After`: Seconds until reset.
-   **Production**: The current implementation is **In-Memory**. For multi-instance production, replace `InMemoryRateLimiter` with a Redis-backed implementation in `src/app/security/rate_limiter.py`.

## Audit Logging

Every request is logged to `logs/audit.log` (configurable via `AUDIT_LOG_PATH`).

-   **Format**: JSON Lines.
-   **Fields**: Timestamp, Client ID, Method, Path, Status, Duration, IP.
-   **Retention**: Configure a log agent (e.g., CloudWatch Agent, Filebeat) to ship these logs to a central store and rotate the local files.

## Secret Management

-   **Storage**: Never commit secrets to Git. Use `.env` for local dev and **AWS Secrets Manager** for production.
-   **Rotation**:
    1.  Generate new key/secret.
    2.  Update AWS Secrets Manager.
    3.  Restart ECS Service (force new deployment).

## Incident Response

### Leaked Key
1.  **Identify**: Which key was leaked.
2.  **Revoke**: Remove it from `ALLOWED_API_KEYS` or rotate `JWT_SECRET`.
3.  **Deploy**: Force deployment to apply changes immediately.
4.  **Audit**: Check `audit.log` for suspicious activity using the leaked key.

### Vulnerable Dependency
1.  **Scan**: CI runs `pip-audit` weekly.
2.  **Patch**: Update `requirements.txt` with patched version.
3.  **Verify**: Run tests and deploy.
