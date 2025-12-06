# FAQ and Known Issues

## Frequently Asked Questions

### Q: How do I get an API key?

Contact REPLACE_ME_EMAIL or request via REPLACE_ME_PORTAL.

### Q: What's the rate limit?

Default: 100 requests/minute per API key. Contact us for higher limits.

### Q: How do I rotate my API key?

1. Request new key from REPLACE_ME_PORTAL
2. Update your application
3. Old key remains valid for 24 hours

### Q: Why is my request timing out?

- Check if prompt is very long (>100k tokens)
- Verify you're using async endpoint for long requests
- Check our status page: REPLACE_ME_STATUS_PAGE

---

## Known Issues

### Rate Limit Tuning

**Issue**: Default rate limits may be too strict for batch workloads.

**Workaround**: Request higher limits or use queue-based async endpoint.

### Streaming Connection Resets

**Issue**: Long-running streams may reset after 60 seconds of no data.

**Workaround**: Implement client-side reconnection with exponential backoff.

### Health Check Failures After Deploy

**Issue**: Health checks may fail for 30 seconds after deployment.

**Cause**: Container startup time.

**Fix**: ALB has 60-second grace period configured.

### High Memory on Long Prompts

**Issue**: Very long prompts (>50k tokens) may cause OOM.

**Workaround**: Split into smaller chunks or use streaming.

### SQS Message Visibility

**Issue**: If worker crashes, message reappears after 30 seconds.

**Expected behavior**: Messages are reprocessed by another worker.

---

## Troubleshooting

### "401 Unauthorized"
- Check API key is correct
- Verify key is in `X-API-Key` header

### "429 Too Many Requests"
- You've exceeded rate limit
- Wait 60 seconds or use backoff

### "503 Service Unavailable"
- Service is starting up or overloaded
- Check status page
- Retry with exponential backoff
