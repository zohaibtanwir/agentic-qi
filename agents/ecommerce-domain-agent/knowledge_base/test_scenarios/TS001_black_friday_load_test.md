# TS001: Black Friday Load Test

**Entity**: order

## Description
Simulate Black Friday traffic surge

## Test Data
```json
{
  "concurrent_users": 100000,
  "orders_per_minute": 50000,
  "duration_hours": 4,
  "traffic_pattern": "surge"
}
```

## Success Criteria
```json
{
  "uptime": "99.9%",
  "response_time_p95": "3s",
  "order_loss": "0%",
  "payment_failure": "<1%"
}
```
