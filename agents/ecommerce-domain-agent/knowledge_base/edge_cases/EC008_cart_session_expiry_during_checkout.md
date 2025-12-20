# EC008: Cart Session Expiry During Checkout

**Category**: timing
**Entity**: cart
**Workflow**: checkout
**Severity**: high

## Description
User session expires during payment entry

## Test Approach
Expire session after checkout start

## Expected Behavior
Preserve cart and allow continuation

## Example Test Data
```json
{
  "session_timeout": 900,
  "checkout_duration": 1200,
  "cart_items": 5
}
```
