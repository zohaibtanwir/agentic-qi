# EC010: Loyalty Points Race Condition

**Category**: concurrency
**Entity**: customer
**Workflow**: loyalty
**Severity**: high

## Description
Points used simultaneously across channels

## Test Approach
Concurrent point redemption requests

## Expected Behavior
Prevent double spending of points

## Example Test Data
```json
{
  "available_points": 1000,
  "redemption_1": 800,
  "redemption_2": 500,
  "timing": "simultaneous"
}
```
