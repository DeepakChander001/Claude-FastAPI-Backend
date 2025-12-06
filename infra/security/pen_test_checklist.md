# Penetration Testing Checklist

## Scope
-   **Target**: `https://api.claude-proxy.com` (Staging/Prod)
-   **Excluded**: AWS Infrastructure (Console, IAM), DDoS attacks.

## Authentication & Authorization
- [ ] **Bypass**: Attempt to access `/api/enqueue` without `X-API-Key` or `Authorization` header.
- [ ] **Privilege Escalation**: Try to access admin routes (if any) with standard user key.
- [ ] **Token Manipulation**: Modify JWT signature or payload (alg: none).

## Input Validation
- [ ] **Injection**: Test SQLi/NoSQLi on `prompt` field (though it goes to LLM, check logging/storage).
- [ ] **XSS**: Check if `prompt` is reflected in any UI or error message without escaping.
- [ ] **Fuzzing**: Send malformed JSON, huge payloads (>10MB), array instead of string.

## Logic & State
- [ ] **Rate Limiting**: Attempt to exceed 60 RPM. Verify 429 response.
- [ ] **Race Conditions**: Send parallel requests to use up quota or double-spend.

## Configuration
- [ ] **Headers**: Verify HSTS, CSP, X-Frame-Options are present.
- [ ] **SSL/TLS**: Verify weak ciphers are disabled (Qualys SSL Labs A+).
- [ ] **Information Disclosure**: Check error messages for stack traces (should be hidden in prod).

## Reporting
-   Report critical findings immediately to security@example.com.
-   Submit final report with reproduction steps and CVSS scores.
