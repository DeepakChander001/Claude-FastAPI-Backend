# CloudFront Functions vs Lambda@Edge

## Overview

| Feature | CloudFront Functions | Lambda@Edge |
|---------|---------------------|-------------|
| **Runtime** | JavaScript only | Node.js, Python |
| **Execution Time** | <1ms | Up to 30s |
| **Memory** | 2MB | Up to 10GB |
| **Network Access** | No | Yes |
| **Cost** | Very cheap | More expensive |
| **Triggers** | Viewer request/response | All 4 triggers |

## When to Use CloudFront Functions

-   **Header Manipulation**: Add/remove/modify headers.
-   **URL Rewrites**: Normalize paths, redirects.
-   **A/B Testing**: Simple cookie-based routing.
-   **Bot Detection**: Basic user-agent checks.

Example:
```javascript
function handler(event) {
    var request = event.request;
    request.headers['x-custom-header'] = {value: 'added-at-edge'};
    return request;
}
```

## When to Use Lambda@Edge

-   **Authentication**: Validate JWTs at edge.
-   **Dynamic Content**: Generate responses.
-   **External API Calls**: Fetch data from other services.
-   **Complex Logic**: Heavy computation.

## Cost Comparison

-   **CloudFront Functions**: $0.10 per million invocations.
-   **Lambda@Edge**: $0.60 per million + compute time.

## Recommendation

Start with CloudFront Functions for simple cases. Use Lambda@Edge only when you need network access or complex logic.
