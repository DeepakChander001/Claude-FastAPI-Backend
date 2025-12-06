# CI Secrets Handling

## Principles
1.  **Least Privilege**: CI roles should only have permissions to push to specific ECR repos.
2.  **Short-Lived Credentials**: Use OIDC (OpenID Connect) instead of long-lived access keys.
3.  **No Secrets in Logs**: Ensure all secrets are masked in CI logs.

## GitHub Actions OIDC
Configure AWS to trust GitHub's OIDC provider.
-   **Role**: `arn:aws:iam::REPLACE_ME_ACCOUNT:role/GitHubActionsECRPush`
-   **Trust Policy**: Allow `repo:REPLACE_ME_ORG/claude-proxy:ref:refs/heads/dev`.

## IAM Policy Example (ECR Push)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CompleteLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "arn:aws:ecr:REPLACE_ME_REGION:REPLACE_ME_ACCOUNT:repository/claude-proxy"
        },
        {
            "Effect": "Allow",
            "Action": "ecr:GetAuthorizationToken",
            "Resource": "*"
        }
    ]
}
```

## Rotation
-   If using Access Keys, rotate every 90 days.
-   If using OIDC, no rotation needed (tokens are ephemeral).
