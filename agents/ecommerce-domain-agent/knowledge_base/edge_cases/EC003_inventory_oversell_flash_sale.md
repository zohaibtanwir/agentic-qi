# EC003: Inventory Oversell Flash Sale

**Category**: concurrency
**Entity**: inventory
**Workflow**: flash_sale
**Severity**: critical

## Description
Multiple customers buying last units during high traffic

## Test Approach
Load test with 1000 concurrent purchases of 10 items

## Expected Behavior
No overselling, graceful sold out messaging

## Example Test Data
```json
{
  "available_quantity": 10,
  "concurrent_buyers": 1000,
  "requests_per_second": 500
}
```
