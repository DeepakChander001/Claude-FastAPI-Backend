# API Specification

## Overview
This API acts as a secure, scalable proxy for the Anthropic Claude API. It manages authentication, rate limiting, and request brokering, allowing client applications to generate text using Claude models.

## Endpoints

### 1. POST /api/generate
Generates text based on a provided prompt.

-   **Authentication**: Required (Bearer Token or API Key).
-   **Request Schema**:
    -   `prompt` (string, required): The input text.
    -   `model` (string, optional): Default "claude-3.5".
    -   `stream` (boolean, optional): Default `false`.
    -   `max_tokens` (integer, optional): Default 800.
    -   `temperature` (float, optional): Default 0.0.
    -   `metadata` (object, optional): Custom key-value pairs.
-   **Example Request**:
    ```json
    {
      "prompt": "Explain quantum computing to a 5-year-old.",
      "model": "claude-3.5",
      "max_tokens": 100
    }
    ```
-   **Example Response**:
    ```json
    {
      "request_id": "req_12345",
      "output": "Quantum computing is like...",
      "model": "claude-3.5",
      "usage": {"input_tokens": 10, "output_tokens": 20}
    }
    ```
-   **Error Codes**:
    -   `400 Bad Request`: Invalid input schema.
    -   `401 Unauthorized`: Missing or invalid API key.
    -   `429 Too Many Requests`: Rate limit exceeded.
    -   `500 Internal Server Error`: Upstream failure or internal error.

### 2. GET /health
Health check endpoint for load balancers.

-   **Authentication**: None.
-   **Response**: `{"status": "ok"}`
-   **Error Codes**: `500` if service is unhealthy.

### 3. GET /status/{request_id}
Check the status of an asynchronous or long-running generation request.

-   **Authentication**: Required.
-   **Response Schema**:
    -   `request_id` (string)
    -   `status` (string): "queued", "running", "done", "failed"
    -   `created_at` (string)
    -   `completed_at` (string, optional)
    -   `partial_output` (string, optional)
-   **Error Codes**:
    -   `404 Not Found`: Request ID does not exist.

## Streaming Note
Streaming is supported via Server-Sent Events (SSE). To enable, set `"stream": true` in the `POST /api/generate` body. The response will be a stream of events. (Implementation pending).
