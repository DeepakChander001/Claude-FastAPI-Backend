# API Endpoints

## POST /api/generate
-   **Route**: `/api/generate`
-   **Headers**:
    -   `Authorization`: `Bearer <token>` OR
    -   `X-API-Key`: `REPLACE_ME`
-   **Validation**: Validates `GenerateRequest` body. Returns 400 if `prompt` is missing.
-   **Status Codes**: 200 (OK), 400 (Bad Request), 401 (Unauthorized), 429 (Too Many Requests), 500 (Internal Error).

## GET /health
-   **Route**: `/health`
-   **Headers**: None required.
-   **Validation**: None.
-   **Status Codes**: 200 (OK), 500 (Unhealthy).

## GET /status/{request_id}
-   **Route**: `/status/{request_id}`
-   **Headers**: Auth headers required.
-   **Validation**: Checks if `request_id` exists.
-   **Status Codes**: 200 (OK), 404 (Not Found), 401 (Unauthorized).
