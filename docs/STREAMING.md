# Brokered Streaming Architecture

## Overview
The streaming subsystem uses a **Brokered Pattern** to decouple the generation worker from the HTTP client. This ensures reliability, scalability, and the ability to handle disconnects/reconnects.

## Components

### 1. Broker (`src/app/streaming/broker.py`)
-   Acts as a Pub/Sub message bus.
-   In production, this wraps **Redis Pub/Sub**.
-   In tests, we use an in-memory `FakeBroker`.
-   **Channels**: Each request has a unique channel `request:{request_id}`.

### 2. Streaming Worker (`src/app/streaming/worker.py`)
-   Receives a generation request.
-   Calls the Anthropic API (via `stream_generate`).
-   As tokens arrive, it **publishes** `chunk` messages to the broker.
-   When finished, it publishes a `done` message.

### 3. SSE Endpoint (`src/app/streaming/sse_endpoint.py`)
-   FastAPI endpoint that **subscribes** to the broker channel.
-   Yields messages as **Server-Sent Events (SSE)** to the HTTP client.
-   Format: `data: {"type": "chunk", "token": "..."}\n\n`

## Message Protocol
-   **Chunk**: `{"type": "chunk", "token": "Hello", "seq": 1, "request_id": "..."}`
-   **Done**: `{"type": "done", "final": "Hello world", "request_id": "..."}`
-   **Error**: `{"type": "error", "error": "Something went wrong", "request_id": "..."}`

## Local Development & Testing
-   **Tests**: See `tests/test_streaming.py`. We use `FakeBroker` and `FakeAnthropicStreamer` to simulate the entire flow without real network calls.
-   **Running Locally**: Ensure Redis is running (via Docker Compose) if you switch to the real Broker implementation. Currently, the code supports injection of any client.
