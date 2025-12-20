# EC002: Payment Timeout After Authorization

**Category**: network
**Entity**: payment
**Workflow**: checkout
**Severity**: critical

## Description
Network timeout after payment authorized but before confirmation

## Test Approach
Simulate network failure after authorization request

## Expected Behavior
Idempotent retry with status check

## Example Test Data
```json
{
  "payment_amount": 150.0,
  "timeout_after": "authorization",
  "retry_count": 3
}
```
