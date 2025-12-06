# Backup and Retention Runbook

## RDS Snapshots (if applicable)

### Automated Snapshots
AWS RDS automatically creates daily snapshots with configurable retention.

```bash
# List snapshots
aws rds describe-db-snapshots --db-instance-identifier REPLACE_ME_DB_ID

# Create manual snapshot (dry run)
echo "aws rds create-db-snapshot --db-instance-identifier REPLACE_ME_DB_ID --db-snapshot-identifier manual-YYYYMMDD"
```

### Restore from Snapshot
```bash
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier REPLACE_ME_NEW_DB \
    --db-snapshot-identifier REPLACE_ME_SNAPSHOT_ID
```

---

## S3 Lifecycle Rules

Configure lifecycle rules in Terraform or via CLI:
```bash
aws s3api put-bucket-lifecycle-configuration \
    --bucket REPLACE_ME_BUCKET \
    --lifecycle-configuration file://lifecycle.json
```

Example lifecycle.json:
```json
{
  "Rules": [
    {"ID": "expire-old-logs", "Status": "Enabled", "Expiration": {"Days": 90}},
    {"ID": "archive-to-glacier", "Status": "Enabled", "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]}
  ]
}
```

---

## Secrets Manager Rotation

Set up automatic rotation:
```bash
aws secretsmanager rotate-secret --secret-id REPLACE_ME_SECRET --rotation-lambda-arn REPLACE_ME_LAMBDA
```

Manual rotation:
1. Generate new secret value.
2. Update secret in Secrets Manager.
3. Force ECS task restart to pick up new secret.

---

## Retention Windows

| Resource | Retention | Notes |
|----------|-----------|-------|
| RDS Snapshots | 35 days | Automated |
| CloudWatch Logs | 90 days | Configurable |
| S3 Access Logs | 90 days | Lifecycle rule |

---

## Test Restore Verification

Quarterly, verify backups are restorable:
1. Restore RDS snapshot to test instance.
2. Verify data integrity.
3. Delete test instance.
4. Document results.
