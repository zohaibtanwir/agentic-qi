# BP001: Implement Idempotent Payment Processing

**Category**: payment
**Impact**: critical
**Entities**: payment, order

## Description

        Always use idempotency keys for payment operations to prevent duplicate charges.

        Implementation:
        - Generate unique idempotency key for each payment request
        - Store key with payment status
        - Return cached result for duplicate requests
        - Expire keys after 24 hours

        Benefits:
        - Prevents double charging
        - Safe retry on network failures
        - Better customer experience
        
