# SEC002: API Rate Limiting

**Category**: api_security
**Severity**: high
**Compliance**: N/A

## Description

        Implement rate limiting to prevent abuse.

        Limits:
        - Guest: 100 req/min
        - Authenticated: 1000 req/min
        - Cart operations: 10 req/min
        - Checkout: 5 req/hour

        Response:
        - 429 Too Many Requests
        - Retry-After header
        - Progressive penalties
        
