# Legal & Compliance Checklist

## ⚠️ Review with Legal Before Production

This service processes user prompts and AI model outputs. Ensure compliance before launch.

---

## Data Retention

- [ ] Define retention period for request logs (recommend: 90 days)
- [ ] Define retention period for prompt/response content (recommend: 30 days or per policy)
- [ ] Implement automated deletion after retention period
- [ ] **LEGAL REVIEW REQUIRED**

## PII Handling

- [ ] Audit what PII may be in prompts (names, emails, addresses)
- [ ] Implement PII redaction in logs (see OTEL config)
- [ ] Document data minimization practices
- [ ] **LEGAL REVIEW REQUIRED**

## GDPR Compliance

- [ ] Right to erasure (data deletion API)
- [ ] Right to access (data export API)
- [ ] Data processing agreement with Anthropic
- [ ] Data processing agreement with Supabase
- [ ] Privacy policy updated
- [ ] **LEGAL REVIEW REQUIRED**

## CCPA Compliance

- [ ] "Do Not Sell" opt-out if applicable
- [ ] Consumer data access request process
- [ ] **LEGAL REVIEW REQUIRED**

## Access Controls

- [ ] API keys required for all endpoints
- [ ] Rate limiting enforced
- [ ] IP allowlisting for admin endpoints
- [ ] Audit logging enabled

## Logging & Monitoring

- [ ] Logs do not contain API keys
- [ ] Logs do not contain full prompts (or are encrypted)
- [ ] Log retention policy defined
- [ ] Access to logs restricted

## Breach Notification

- [ ] Incident response plan documented
- [ ] Notification timeline defined (72 hours for GDPR)
- [ ] Contact list for legal/security
- [ ] **LEGAL REVIEW REQUIRED**

---

## Data Processing Addendum Template

```
REPLACE_ME_WITH_DPA_TEMPLATE

This agreement covers:
- Data categories processed
- Processing purposes
- Security measures
- Sub-processors
- Data transfer mechanisms
```

## Sign-Off

| Reviewer | Date | Signature |
|----------|------|-----------|
| Legal | REPLACE_ME | _________ |
| Security | REPLACE_ME | _________ |
| Engineering | REPLACE_ME | _________ |
