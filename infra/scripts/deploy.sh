#!/bin/bash
set -e

echo "--------------------------------------------------"
echo "Deploying Infrastructure with Terraform"
echo "--------------------------------------------------"

cd infra/terraform

# 1. Initialize
echo "Initializing Terraform..."
terraform init

# 2. Plan
echo "Planning deployment..."
terraform plan -out=plan.tfplan

echo "--------------------------------------------------"
echo "Plan saved to 'plan.tfplan'. Review it above."
echo "To apply, run:"
echo "  terraform apply plan.tfplan"
echo "--------------------------------------------------"

# Uncomment to auto-apply (Use with caution in CI/CD)
# terraform apply plan.tfplan --auto-approve
