# Canary Rollback & Autoscaling Runbook

## Canary Deployment Strategy

We use a weighted traffic shifting strategy via ALB.

1.  **Phase 1: 1% Traffic**
    -   Deploy new version to `CanaryService`.
    -   Shift 1% of traffic.
    -   Wait 5 minutes.
    -   Check Alarms: `HighErrorRate`, `HighLatency`.
    -   Run Smoke Tests.

2.  **Phase 2: 10% Traffic**
    -   Increase weight to 10%.
    -   Wait 15 minutes.
    -   Monitor business metrics (Queue processing rate).

3.  **Phase 3: 100% Promotion**
    -   Shift 100% to `CanaryService` (or swap Blue/Green).
    -   Scale down old service.

## Rollback Triggers

Initiate immediate rollback if:
-   **Error Rate** > 1% (HTTP 5xx).
-   **Latency P95** > 2s.
-   **Smoke Tests** fail.
-   **Queue Stalled**: Oldest message > 10 mins.

**Rollback Command:**
```bash
./infra/scripts/canary_release.sh --image OLD_IMAGE --canary-percent 0 --live
```

## Autoscaling Configuration

### Worker Service
Scales based on **Queue Depth**.
-   **Metric**: `ClaudeProxy/Queue/QueueDepth` (Custom Metric).
-   **Target**: 10 messages per worker.
-   **Scale Out**: Aggressive (60s cooldown).
-   **Scale In**: Conservative (300s cooldown) to prevent thrashing.

### API Service
Scales based on **CPU Utilization**.
-   **Target**: 60% CPU.

## Local Testing
You can simulate the canary flow locally using the provided scripts in dry-run mode.
```bash
./infra/scripts/canary_release.sh --image test:latest --canary-percent 10
```
