# TS005: Payment Failure Recovery

**Entity**: payment

## Description
Test payment failure handling

## Test Data
```json
{
  "failure_types": [
    "declined",
    "timeout",
    "insufficient_funds",
    "3ds_fail"
  ],
  "retry_strategy": "exponential_backoff",
  "alternative_methods": [
    "different_card",
    "paypal",
    "pay_later"
  ],
  "communication": [
    "inline_message",
    "email",
    "support"
  ]
}
```

## Success Criteria
```json
{
  "recovery_rate": ">30%",
  "customer_clarity": "high",
  "support_tickets": "<5%"
}
```
