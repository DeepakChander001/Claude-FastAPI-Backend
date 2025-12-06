# Terraform Infrastructure

## Quick Start

```bash
cd infra/terraform

# Initialize
terraform init

# Plan (dry run)
terraform plan -out=plan.tfplan

# Apply (requires approval)
terraform apply plan.tfplan
```

## State Management
We recommend storing Terraform state in S3 with DynamoDB locking.
See `backend.tf.example` for configuration.

## Policy
-   All changes MUST be reviewed via `terraform plan` before apply.
-   Production changes require approval from at least 2 team members.
