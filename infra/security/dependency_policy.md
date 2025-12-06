# Dependency Management Policy

## Audit Frequency
-   **CI Pipeline**: Runs `pip-audit` and `safety` on every PR and merge to `dev`.
-   **Scheduled**: GitHub Actions scheduled workflow runs weekly to detect new vulnerabilities in existing locks.

## Triage Process
1.  **High/Critical**: Must be fixed within 24 hours. Block deployment.
2.  **Medium**: Fix within next sprint.
3.  **Low**: Fix when convenient.

## False Positives
If a vulnerability is flagged but not exploitable in our context:
1.  Document reasoning in `docs/SECURITY_EXCEPTIONS.md`.
2.  Add to ignore list (e.g., `--ignore-vuln ID`).

## Upgrade Strategy
-   Use `pip-compile` (pip-tools) to manage `requirements.txt`.
-   **Major Upgrades**: Quarterly review.
-   **Minor/Patch**: Monthly or automated via Dependabot.

## Testing Updates
1.  Create branch `chore/deps-upgrade`.
2.  Run `pip-compile --upgrade`.
3.  Run full test suite + Smoke Tests.
4.  Deploy to Staging for 24h soak test.
