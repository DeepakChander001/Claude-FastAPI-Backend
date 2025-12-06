# Security Rotation Runbook

## Secret Rotation Strategy (Zero Downtime)

We use **AWS Secrets Manager** to store sensitive configuration (e.g., `ANTHROPIC_API_KEY`, `JWT_SECRET`).

### Routine Rotation (Scheduled)
1.  **Create New Version**: Add a new version of the secret in Secrets Manager (staging label).
2.  **Update Application**:
    -   If app loads secrets on startup: Trigger a new deployment (force new deployment) to pick up new values.
    -   If app polls secrets: Wait for refresh interval.
3.  **Verify**: Ensure app is working with new secret.
4.  **Deprecate**: Remove the old secret version.

### Emergency Rotation (Leaked Key)
**Trigger**: You suspect a key has been exposed.

1.  **Revoke Immediately**:
    -   Log in to provider (e.g., Anthropic Console).
    -   Revoke the compromised key.
    -   *Note: This will break the app temporarily.*

2.  **Generate New Key**:
    -   Create a new key in the provider console.

3.  **Update Secrets Manager**:
    ```bash
    aws secretsmanager put-secret-value \
        --secret-id claude-proxy-prod \
        --secret-string '{"ANTHROPIC_API_KEY":"new-key"}'
    ```

4.  **Redeploy Immediately**:
    ```bash
    aws ecs update-service --service claude-proxy --force-new-deployment
    ```

5.  **Audit**:
    -   Search logs for usage of the old key to identify unauthorized access.
    -   Check `logs/audit.log` for anomalous IPs.

## IAM Rotation
-   Rotate IAM User Access Keys every 90 days.
-   Prefer IAM Roles (Task Roles) over long-term user keys.
