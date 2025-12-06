# Data Models & Schemas

## GenerateRequest
**Use when**: Sending a prompt to the API for text generation.
-   **prompt**: The main input text.
-   **model**: Specific Claude model version (e.g., "claude-3.5").
-   **stream**: Set to `true` for streaming responses (SSE).
-   **max_tokens**: Limit the length of the generated output.
-   **temperature**: Control randomness (0.0 = deterministic).
-   **metadata**: Pass arbitrary data to track requests.

## GenerateResponse
**Use when**: Receiving a non-streaming response from the API.
-   **request_id**: Use this to track or debug specific requests.
-   **output**: The complete generated text.
-   **usage**: Check token consumption here.
-   **warnings**: Check for any non-critical issues from the provider.

## StatusResponse
**Use when**: Polling for the status of a long-running or async request.
-   **status**: "queued", "running", "done", or "failed".
-   **partial_output**: May contain text generated so far if supported.
