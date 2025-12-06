# AWS Cost Control

## Alarms
Set up CloudWatch alarms for:
-   **Unexpected Scaling**: Alert if ECS task count exceeds expected maximum.
-   **High EC2 Costs**: (If using EC2 launch type)
-   **SQS Queue Depth**: Alert if messages pile up.

## Budgets
Use AWS Budgets to set spending limits:
```bash
aws budgets create-budget --account-id REPLACE_ME_ACCOUNT --budget file://budget.json
```

## Service Limits
Request limit increases for:
-   ECS tasks per cluster.
-   ALB target groups.

## Destroy Resources
To remove all resources (dry run):
```bash
./infra/scripts/destroy_dry_run.sh
```

To actually destroy:
```bash
CONFIRM=true ./infra/scripts/destroy_dry_run.sh --apply
```
