#!/bin/sh
set -e

echo "===== Terraform Destroy (Dry Run) ====="

cd infra/terraform

terraform plan -destroy -out=plans/destroy.tfplan

echo "Destroy plan saved to infra/terraform/plans/destroy.tfplan"

if [ "$1" = "--apply" ] && [ "$CONFIRM" = "true" ]; then
    echo "Applying destroy..."
    terraform apply plans/destroy.tfplan
else
    echo "Dry run. To destroy: CONFIRM=true ./infra/scripts/destroy_dry_run.sh --apply"
fi
