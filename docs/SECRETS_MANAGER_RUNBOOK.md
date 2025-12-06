# AWS Secrets Manager Runbook

## Overview
We use AWS Secrets Manager to store sensitive configuration like API keys and database credentials. These are injected into the ECS containers as environment variables at runtime.

## Secret Structure
The secret should be stored as a **Key/value** (JSON) secret.

**Secret Name**: `my-app-secrets-prod` (Matches `secrets_manager_name` in Terraform)

**JSON Payload**:
```json
{
  "ANTHROPIC_API_KEY": "sk-ant-api03-...",
  "SUPABASE_URL": "https://xyz.supabase.co",
  "SUPABASE_KEY": "eyJhbGci..."
}
```

## IAM Permissions
The ECS Task Execution Role needs permission to read this secret.
**Policy Example** (Included in `infra/terraform/iam.tf`):
```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-app-secrets-prod-*"
}
```

## Rotation Procedure (Zero Downtime)

Since secrets are injected as environment variables, simply updating the secret in AWS **does not** update the running containers. You must restart the tasks.

1.  **Update Secret**:
    Go to AWS Console -> Secrets Manager -> `my-app-secrets-prod` -> Retrieve secret value -> Edit -> Update values -> Save.

2.  **Rotate Tasks**:
    Force a new deployment to pick up the new values.
    ```bash
    aws ecs update-service \
        --cluster claude-proxy-cluster \
        --service claude-proxy-service \
        --force-new-deployment
    ```
    ECS will start new tasks (with new secrets), wait for them to be healthy, and then drain the old tasks.

## Local Testing
To verify you can fetch secrets (requires AWS credentials):

```bash
aws secretsmanager get-secret-value \
    --secret-id my-app-secrets-prod \
    --query SecretString \
    --output text
```
