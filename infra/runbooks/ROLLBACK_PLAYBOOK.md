# Rollback Playbook

## Quick Rollback (< 5 minutes)

### Option 1: ECS Task Definition Rollback
```bash
# Find previous task definition
aws ecs list-task-definitions --family-prefix claude-proxy-api --sort DESC --max-items 5

# Rollback to previous revision
aws ecs update-service \
    --cluster REPLACE_ME_CLUSTER \
    --service api-service \
    --task-definition claude-proxy-api:PREVIOUS_REVISION \
    --force-new-deployment

# Or use the helper script
./infra/scripts/rollback_release.sh --live
```

### Option 2: Canary Rollback (if in canary mode)
```bash
./infra/scripts/canary_release.sh --canary-percent 0 --live
```

---

## Infrastructure Rollback

### Terraform Rollback
```bash
cd infra/terraform

# Show current state
terraform show

# Revert to previous state (if versioned)
git checkout HEAD~1 -- infra/terraform/*.tf
terraform plan
CONFIRM=true ./infra/scripts/terraform_run.sh --apply
```

---

## Secret Rotation Rollback

If secrets were rotated as part of the release:
1. Retrieve previous secret version from Secrets Manager.
2. Update secret to previous value.
3. Force ECS task restart to pick up new secrets.

```bash
aws secretsmanager get-secret-value --secret-id REPLACE_ME_SECRET --version-stage AWSPREVIOUS
```

---

## Cache Invalidation

After rollback, invalidate CloudFront cache:
```bash
./infra/scripts/cloudfront_invalidate.sh --dist-id REPLACE_ME_DIST_ID --paths "/*" --live
```

---

## Post-Rollback Steps

1. **Verify Stability**
   ```bash
   ./infra/scripts/smoke_test.sh --url http://PRODUCTION_ALB_DNS
   ```

2. **Open Postmortem Ticket**
   - Create incident ticket.
   - Assign owner.
   - Schedule postmortem within 48 hours.

3. **Freeze Releases**
   - No new deployments until root cause identified.
   - Update team in #releases channel.

4. **Notify Stakeholders**
   - Customer support team.
   - Affected customers (if applicable).

---

## Rollback Checklist

- [ ] Service reverted to stable version.
- [ ] Smoke tests passing.
- [ ] Error rates normalized.
- [ ] Postmortem ticket created.
- [ ] Team notified.
