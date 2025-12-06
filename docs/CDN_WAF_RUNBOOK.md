# CDN & WAF Runbook

## Why CloudFront + WAF?

CloudFront is a global CDN that:
-   **Reduces Latency**: Edge locations serve content closer to users.
-   **DDoS Protection**: AWS Shield Standard is included.
-   **TLS Termination**: Offloads SSL/TLS from your ALB.
-   **Caching**: Reduces load on origin for static content.

WAFv2 adds:
-   **OWASP Top 10 Protection**: SQLi, XSS, etc.
-   **Rate Limiting**: Per-IP throttling.
-   **Bot Control**: Block known bad bots.
-   **Geo-Blocking**: Restrict by country.

## Rollout Strategy

### Phase 1: COUNT Mode (48 hours)
1.  Deploy WAF with all rules in `COUNT` mode.
2.  Monitor CloudWatch metrics for matches.
3.  Identify false positives.

### Phase 2: Tune Rules
1.  Exclude legitimate patterns from rules.
2.  Adjust rate limits based on traffic.

### Phase 3: BLOCK Mode
1.  Move rules to `BLOCK` one at a time.
2.  Monitor for user complaints.

## TLS Certificates (ACM)

1.  Request certificate in **us-east-1** (required for CloudFront).
2.  Use DNS validation (recommended).
3.  Attach to CloudFront distribution.

```bash
aws acm request-certificate \
    --domain-name api.example.com \
    --validation-method DNS \
    --region us-east-1
```

## Cache Invalidation

```bash
./infra/scripts/cloudfront_invalidate.sh --dist-id EDFDVBD632BHDS5 --paths "/*" --live
```

## Cost Considerations

-   **PriceClass_100**: US/EU only (cheapest).
-   **PriceClass_200**: US/EU/Asia.
-   **PriceClass_All**: Global (most expensive).

## Rollback

If WAF blocks legitimate traffic:
1.  Switch rule to `COUNT` mode.
2.  Review sampled requests.
3.  Add exclusion pattern.
