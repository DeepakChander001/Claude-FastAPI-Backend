# Secrets Management Guide

## Overview
In production environments (like AWS ECS), we avoid storing sensitive credentials in environment variables or source code. Instead, we use **AWS Secrets Manager**.

## How it Works
1.  **Local Development**: The app reads configuration from `.env`.
2.  **Production**: The app reads non-sensitive config from env vars, but fetches sensitive keys (API keys, DB credentials) from a specified secret in AWS Secrets Manager.

## Setup

### 1. Create a Secret in AWS
Create a new secret (Key/value pair type) in AWS Secrets Manager.
**Example JSON Payload:**
```json
{
  "ANTHROPIC_API_KEY": "sk-ant-api03-...",
  "SUPABASE_URL": "https://xyz.supabase.co",
  "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "DATABASE_URL": "postgresql://user:pass@host:5432/db"
}
```

### 2. Configure the Application
Set the following environment variables in your ECS Task Definition or `.env` file:

-   `AWS_SECRETS_MANAGER_ENABLED=true`
-   `AWS_SECRETS_NAME=my-production-secret-name`
-   `ENVIRONMENT=production`

### 3. IAM Permissions
The ECS Task Execution Role must have permission to read the secret:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "arn:aws:secretsmanager:region:account-id:secret:my-production-secret-name-xxxxxx"
        }
    ]
}
```

## Local Development Workflow
1.  Copy `.env.example` to `.env`.
2.  Fill in `ANTHROPIC_API_KEY` and other keys directly in `.env`.
3.  Ensure `AWS_SECRETS_MANAGER_ENABLED=false`.
4.  **NEVER commit `.env` to git.**

## Testing
To test the secrets loading logic without real AWS access, use the provided mock client pattern (see `tests/test_config_secrets.py`).
