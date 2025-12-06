#!/bin/sh
set -e

echo "===== Terraform Run Helper ====="

# Check Terraform installed
if ! command -v terraform >/dev/null 2>&1; then
    echo "ERROR: Terraform is not installed."
    exit 1
fi

cd infra/terraform

# Initialize
echo "[Step 1] Running terraform init..."
terraform init

# Plan
echo "[Step 2] Running terraform plan..."
terraform plan -out=plans/plan.tfplan

echo "Plan saved to infra/terraform/plans/plan.tfplan"

# Apply (Gated)
if [ "$1" = "--apply" ]; then
    if [ "$CONFIRM" = "true" ]; then
        echo "[Step 3] Applying..."
        terraform apply plans/plan.tfplan
    else
        echo "ERROR: CONFIRM=true not set. Aborting."
        echo "To apply, run: CONFIRM=true ./infra/scripts/terraform_run.sh --apply"
        exit 1
    fi
else
    echo "Dry run complete. To apply: CONFIRM=true ./infra/scripts/terraform_run.sh --apply"
fi
