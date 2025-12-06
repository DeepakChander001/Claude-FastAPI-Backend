# GitHub Actions Workflows

This directory contains the CI/CD pipelines for the project.

## Workflows

| Workflow | File | Trigger | Description |
| :--- | :--- | :--- | :--- |
| **CI** | `ci.yml` | Push/PR to `main`, `dev` | Runs unit tests, linting, and verifies Docker build. |
| **CD Plan** | `cd-plan.yml` | Push to `dev`, Manual | Runs `terraform plan` and uploads the plan artifact. |
| **CD Deploy** | `cd-deploy.yml` | Manual Dispatch | Runs `terraform apply`. **Requires manual confirmation.** |

## Setup Requirements

1.  **AWS OIDC**: Configure OpenID Connect in AWS IAM to allow GitHub Actions to assume a role.
2.  **Secrets**: Add the following secrets to your GitHub Repository:
    -   `AWS_ROLE_TO_ASSUME`: ARN of the IAM role for GitHub Actions.
    -   `AWS_REGION`: Target AWS region.
3.  **Environments**: Create a `production` environment in GitHub Settings -> Environments and add **Required Reviewers** to protect the deployment.

## Manual Triggers

To run a deployment manually:
1.  Go to the **Actions** tab in GitHub.
2.  Select **CD Deploy (Terraform Apply)**.
3.  Click **Run workflow**.
4.  Enter "yes" in the confirmation box.
