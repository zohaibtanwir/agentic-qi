# TS002: Cart Abandonment Recovery

**Entity**: cart

## Description
Test cart recovery workflows

## Test Data
```json
{
  "abandoned_carts": 1000,
  "recovery_emails": [
    1,
    24,
    72
  ],
  "incentive_offered": true,
  "channels": [
    "email",
    "push",
    "retargeting"
  ]
}
```

## Success Criteria
```json
{
  "recovery_rate": ">10%",
  "email_open_rate": ">30%",
  "conversion_rate": ">5%"
}
```
