# EC005: Guest to Account Conversion

**Category**: data_integrity
**Entity**: customer
**Workflow**: account_creation
**Severity**: medium

## Description
Guest checkout customer creates account with same email

## Test Approach
Create account after guest checkout with same email

## Expected Behavior
Merge guest orders with new account

## Example Test Data
```json
{
  "guest_email": "user@example.com",
  "guest_orders": [
    "ORD-001",
    "ORD-002"
  ],
  "action": "create_account"
}
```
