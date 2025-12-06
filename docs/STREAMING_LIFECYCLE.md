# Streaming Lifecycle & Backpressure

## Request Lifecycle
1.  **Client Connects**: HTTP Client connects to `/api/generate/stream/{request_id}` (SSE).
2.  **Registration**: `ConnectionManager` registers the connection ID.
3.  **Streaming**: `StreamingWorker` generates tokens and publishes to Redis.
4.  **Relay**: SSE Endpoint subscribes to Redis and pushes events to client.
5.  **Completion**: Worker publishes `done`, endpoint closes connection.

## Cancellation Flow
If a client disconnects mid-stream:
1.  **Disconnect Detected**: The SSE generator loop exits (or catches exception).
2.  **Unregistration**: `ConnectionManager` removes the connection ID.
3.  **Check Active**: If 0 subscribers remain, `ConnectionManager` flags for cancellation.
4.  **Signal**: `CancellationCoordinator` sets the `CancellationToken` for that `request_id`.
5.  **Worker Stop**: The `StreamingWorker` checks the token between chunks. If set, it stops generation and publishes `cancelled`.

## Backpressure
In a decoupled system, the worker might generate faster than the client can consume.
-   **Current Implementation**: The worker adds a `backpressure` hint ("low", "medium", "high") to messages based on the sequence number.
-   **Production Strategy**:
    -   **Broker-side**: Monitor Redis list lengths.
    -   **Worker-side**: Pause generation if "high" backpressure is detected (requires feedback channel).
    -   **Client-side**: Clients should handle buffering or disconnect if overwhelmed.

## Distributed Considerations
The current `ConnectionManager` is in-memory. For multiple API replicas:
-   Use **Redis Sets** to track active connection IDs per request.
-   Use **Redis Pub/Sub** for the cancellation signal (broadcast to all workers).
