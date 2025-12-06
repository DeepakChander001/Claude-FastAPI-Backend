# Monitoring & Observability Runbook

## Overview
We use a combination of **Prometheus** for metrics and **OpenTelemetry** for distributed tracing to monitor the health and performance of the Claude Proxy.

## Metrics (Prometheus)

### Key Metrics
-   `http_requests_total`: Counter of all requests by method, path, and status.
-   `http_request_duration_seconds`: Histogram of response latency.
-   `http_requests_in_flight`: Gauge of currently active requests.

### Enabling Metrics
1.  Set `ENABLE_METRICS=true` in `.env`.
2.  Ensure `prometheus-client` is installed (it is by default).
3.  The application exposes metrics at `/metrics`.

### Grafana Dashboard
A template dashboard is provided at `infra/monitoring/grafana_dashboard.json`.
1.  Import this JSON into Grafana.
2.  Select your Prometheus datasource.
3.  You will see panels for RPS, Error Rate, Latency, and Concurrency.

## Tracing (OpenTelemetry)

### Enabling Tracing
1.  Set `ENABLE_TRACING=true` in `.env`.
2.  Set `OTEL_EXPORTER` to your backend (e.g., `otlp`, `jaeger`, or `console`).
3.  Set `OTEL_EXPORTER_ENDPOINT` (e.g., `http://jaeger:4317`).

### Debugging Incidents
1.  **High Error Rate**: Check the "Error Rate" panel. Filter logs by `status=500`.
2.  **High Latency**: Check the "Latency P95" panel. Use the Trace ID from logs (if logged) to find the trace in Jaeger/Tempo.
3.  **Stuck Requests**: Check "In-Flight Requests". If high and constant, workers might be deadlocked or waiting on Anthropic.

## Alerting Rules (Suggested)
-   **High Error Rate**: `rate(5xx) / rate(total) > 0.01` (1% errors) for 5m.
-   **High Latency**: `P95(duration) > 2s` for 5m.
-   **Saturation**: `in_flight > 80% of max_workers`.
