# WAFv2 Policy Recommendations

## Overview
We recommend deploying AWS WAFv2 on the Application Load Balancer (ALB).

## Managed Rule Groups
Enable the following AWS Managed Rules (Core rule set):
1.  **AWSManagedRulesCommonRuleSet**: Protects against OWASP Top 10 (SQLi, XSS, etc.).
    -   Priority: 10
    -   Action: Block
2.  **AWSManagedRulesKnownBadInputsRuleSet**: Blocks known bad inputs (e.g., Log4j).
    -   Priority: 20
    -   Action: Block
3.  **AWSManagedRulesAmazonIpReputationList**: Blocks IPs from Amazon's threat intel.
    -   Priority: 30
    -   Action: Block

## Custom Rules

### 1. Rate Limiting (IP-based)
Block IPs that send too many requests.
-   **Name**: `RateLimit-Global`
-   **Priority**: 40
-   **Limit**: 2000 requests per 5 minutes.
-   **Action**: Block

### 2. JSON Body Size Limit
Protect `/api/enqueue` from large payloads.
-   **Name**: `SizeLimit-Enqueue`
-   **Priority**: 50
-   **Statement**:
    -   ByteMatchStatement: Body
    -   PositionalConstraint: CONTAINS
    -   SearchString: "" (Check size < 10KB)
-   **Action**: Block

## Geo-Blocking (Optional)
If business is regional, block high-risk countries.
-   **Name**: `GeoBlock`
-   **Priority**: 60
-   **Statement**: GeoMatchStatement (CountryCodes: [Block List])
-   **Action**: Block
