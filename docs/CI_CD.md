# CI/CD Guide

## Overview
We use **GitHub Actions** for Continuous Integration and Continuous Deployment. The pipeline is designed to be safe, secure, and auditable.

## CI Workflow (`ci.yml`)
Runs automatically on every Push and Pull Request to `main` or `dev`.

### Steps:
1.  **Lint**: Checks code style using `flake8`.
2.  **Test**: Runs unit tests using `pytest`.
    -   **Important**: Tests run in "offline mode" using `USE_MOCK_CLIENT=true`. No external API calls are made.
3.  **Build Verify**: Attempts to build the Docker image to ensure the `Dockerfile` is valid.

## CD Workflow

Deployment is a two-stage process to prevent accidental changes.

### Stage 1: Plan (`cd-plan.yml`)
-   **Trigger**: Push to `dev` or Manual.
-   **Action**: Runs `terraform plan`.
-   **Artifact**: Uploads the plan file (`plan.tfplan`) to GitHub Actions artifacts.
-   **Goal**: Allows engineers to inspect what *will* change before applying it.

### Stage 2: Deploy (`cd-deploy.yml`)
-   **Trigger**: **Manual Only** (`workflow_dispatch`).
-   **Protection**: Runs in the `production` GitHub Environment, which should be configured to require **Manual Approval** from specific reviewers.
-   **Action**: Runs `terraform apply`.
-   **Safety**: Requires the user to type "yes" in the input prompt to confirm.

## Configuration

### AWS Authentication (OIDC)
We recommend using **OpenID Connect (OIDC)** instead of long-lived AWS Access Keys.
1.  Create an OIDC Provider in AWS IAM for `token.actions.githubusercontent.com`.
2.  Create an IAM Role with a Trust Policy allowing the GitHub repo to assume it.
3.  Update the workflows to use `aws-actions/configure-aws-credentials` with `role-to-assume`.

### GitHub Secrets
Store these in Settings -> Secrets and variables -> Actions:
-   `AWS_ROLE_TO_ASSUME`: The ARN of your deployment role.
-   `AWS_REGION`: `us-east-1` (or your region).

## Safety Best Practices
-   **Never** use `--auto-approve` in a workflow triggered automatically by a push.
-   **Always** review the `terraform plan` output before approving the deploy job.
-   **Least Privilege**: The CI/CD IAM role should only have permissions to modify the specific resources managed by Terraform (ECS, ALB, IAM roles for tasks).
