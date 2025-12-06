# Canary Deployment Checklist

- [ ] **Pre-Flight**:
    - [ ] Build and push Docker image.
    - [ ] Verify current system health (Green dashboard).

- [ ] **Canary 1%**:
    - [ ] Run `canary_release.sh --canary-percent 1`.
    - [ ] Verify `/health/extended` on canary tasks.
    - [ ] Watch logs for 5 mins.

- [ ] **Canary 10%**:
    - [ ] Promote to 10%.
    - [ ] Check Autoscaling behavior (is it scaling up?).

- [ ] **Promotion**:
    - [ ] Promote to 100%.
    - [ ] Verify old tasks drain correctly.

- [ ] **Cleanup**:
    - [ ] Scale down old service (if Blue/Green).
