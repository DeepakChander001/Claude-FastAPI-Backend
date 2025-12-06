# System Architecture

## Request Flow
1.  **Client**: Initiates a request (e.g., chat completion).
2.  **ALB**: Receives request, terminates SSL, forwards to FastAPI service.
3.  **FastAPI (ECS)**:
    -   Validates request and authentication.
    -   Checks rate limits via Redis.
    -   Forwards prompt to Anthropic Claude API.
4.  **Claude API**: Processes prompt and streams back tokens.
5.  **FastAPI**: Receives tokens and streams them back to the Client (Server-Sent Events - SSE).

## Streaming Design
-   **Protocol**: Server-Sent Events (SSE) is recommended for its simplicity and native browser support for unidirectional text streaming.
-   **Broker**: Redis can be used as a pub/sub broker if we need to decouple the Claude consumer from the client responder, but for a simple proxy, direct streaming from the upstream response is often sufficient.
