# Job Queue & Worker Pool

## Architecture

The system uses a pluggable **Job Queue** to handle asynchronous LLM generation tasks.

1.  **Enqueue**: API receives a request, saves it to DB (`pending`), and pushes a job to the queue.
2.  **Worker**: Polls the queue, reserves a job, and executes it.
3.  **Streaming**: The worker streams tokens to the **Broker** (Redis Pub/Sub) which pushes them to the client via SSE.
4.  **Completion**: Worker updates DB status to `done` and ACKs the job.

## Components

-   **QueueAdapter**: Abstract interface (`enqueue`, `reserve`, `ack`, `fail`).
-   **RedisAdapter**: Production implementation using Redis Lists/Sorted Sets.
-   **SQSAdapter**: Alternative implementation for AWS SQS.
-   **WorkerRunner**: The loop that processes jobs.
-   **Dead Letter Queue (DLQ)**: Failed jobs after max retries are moved here.

## Autoscaling

To scale workers on AWS ECS:

1.  **Metric**: `ApproximateNumberOfMessagesVisible` (SQS) or `LLEN` (Redis).
2.  **CloudWatch**: Publish queue length as a custom metric.
3.  **Scaling Policy**: Target Tracking (e.g., maintain 5 messages per worker).

## Runbook

### Stuck Jobs
If a job remains `running` for too long (e.g., worker crash):
-   **Redis**: Use a visibility timeout/monitor script to re-queue "orphaned" reserved jobs.
-   **SQS**: Handled automatically by Visibility Timeout.

### DLQ Processing
Jobs in DLQ need manual inspection.
1.  Check `error_message` in DB.
2.  Fix bug/data.
3.  Re-drive: Move messages from DLQ back to Main Queue.

## Configuration

-   `QUEUE_MAX_ATTEMPTS`: Default 3.
-   `QUEUE_DLQ_NAME`: Default `dead_letter_queue`.
