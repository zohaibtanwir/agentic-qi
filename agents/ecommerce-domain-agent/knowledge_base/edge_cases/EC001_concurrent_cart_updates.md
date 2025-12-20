# EC001: Concurrent Cart Updates

**Category**: concurrency
**Entity**: cart
**Workflow**: cart_management
**Severity**: high

## Description
Multiple sessions updating same cart simultaneously

## Test Approach
Simulate concurrent API calls with different session tokens

## Expected Behavior
Last write wins with proper versioning

## Example Test Data
```json
{
  "session_1": {
    "action": "add_item",
    "product_id": "P123",
    "quantity": 2
  },
  "session_2": {
    "action": "update_quantity",
    "product_id": "P123",
    "quantity": 5
  },
  "timing": "simultaneous"
}
```
