# EC007: Partial Refund Complex Order

**Category**: financial
**Entity**: payment
**Workflow**: refund
**Severity**: high

## Description
Partial refund on order with discounts and loyalty points

## Test Approach
Return subset of items from discounted order

## Expected Behavior
Proportional refund calculation

## Example Test Data
```json
{
  "order_total": 200.0,
  "discount": 20.0,
  "points_used": 1000,
  "items_to_return": [
    "ITEM-001"
  ],
  "item_value": 50.0
}
```
