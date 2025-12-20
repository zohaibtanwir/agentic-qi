# EC004: Price Change During Checkout

**Category**: timing
**Entity**: cart
**Workflow**: checkout
**Severity**: high

## Description
Product price changes while customer in checkout

## Test Approach
Update price after checkout started

## Expected Behavior
Honor price at cart addition or notify customer

## Example Test Data
```json
{
  "original_price": 99.99,
  "new_price": 119.99,
  "change_timing": "during_payment"
}
```
