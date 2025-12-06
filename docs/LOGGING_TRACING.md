# Logging & Tracing Guide

## Overview
We use **Structured Logging (JSON)** and **Distributed Tracing** to achieve observability.
-   **Logs**: Provide discrete event details (errors, status changes).
-   **Traces**: Provide request lifecycle context (latency, path).
-   **Correlation**: `request_id` and `trace_id` link logs to traces.

## Correlation Strategy
1.  **Entry**: Middleware generates `request_id` and starts a Trace Span.
2.  **Propagation**: `request_id` and `trace_id` are injected into `request.state`.
3.  **Logging**: The `StructuredLogger` automatically includes these IDs in every log entry.
4.  **Async**: When enqueuing jobs, these IDs are passed in the job payload/headers to Worker.

## Configuration
Control observability via `.env`:
```bash
ENABLE_TRACING=true
LOG_JSON=true
TRACE_SAMPLING_RATE=0.1 # Sample 10% of requests
```

## OpenTelemetry Setup (Production)
To enable real tracing in production:
1.  Install packages: `pip install opentelemetry-sdk opentelemetry-exporter-otlp`
2.  Set `ENABLE_TRACING=true`.
3.  Configure Exporter in `src/app/tracing/otel_shim.py` (uncomment OTLP section).
4.  Set `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Log Ingestion
We recommend **Filebeat** or **Fluentd** to ship logs to ELK or CloudWatch.
-   **Format**: JSON (one object per line).
-   **Schema**: See `infra/logging/elk/elk_ingest_template.json`.

## PII Redaction
Sensitive data is redacted automatically using `src/app/logging/redaction.py`.
-   **Patterns**: Emails, API Keys, JWTs.
-   **Headers**: Authorization, Cookie.

## Alerting Rules (Log-to-Metrics)
Create CloudWatch Metric Filters or ELK Watchers:
1.  **High Error Rate**: Count logs where `level="ERROR"`.
2.  **Slow Requests**: Count logs where `latency_ms > 2000`.
