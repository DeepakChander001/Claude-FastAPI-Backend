# Claude API Key Leak Incident Playbook

## CRITICAL: Time is of the essence!

## Immediate Actions (within 5 minutes)

### 1. Rotate the Key Immediately
```bash
# Generate new key in Anthropic console
# Update AWS Secrets Manager
aws secretsmanager put-secret-value \
    --secret-id claude-proxy-secrets \
    --secret-string '{"ANTHROPIC_API_KEY":"NEW_KEY_HERE",...}'

# Force ECS to pick up new secret
aws ecs update-service --cluster claude-proxy --service api-service --force-new-deployment
```

### 2. Revoke Old Key
- Log into Anthropic console.
- Revoke the compromised key.

### 3. Check for Unauthorized Usage
- Review Anthropic dashboard for unusual API calls.
- Check CloudTrail for Secrets Manager access.
- Review application logs for suspicious requests.

## Investigation

### 4. Identify Leak Source
- Git history (check for committed secrets).
- Log files (were secrets logged?).
- Third-party integrations.
- Developer machines.

### 5. Audit Access
```bash
# Check who accessed the secret
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=GetSecretValue
```

## Notification

### 6. Notify Stakeholders
- [ ] Security team
- [ ] Engineering lead
- [ ] Legal (if customer data at risk)
- [ ] Anthropic support (if significant unauthorized usage)

## Post-Incident

- [ ] Postmortem within 48 hours.
- [ ] Review secret handling practices.
- [ ] Implement additional controls (secret scanning, rotation).
