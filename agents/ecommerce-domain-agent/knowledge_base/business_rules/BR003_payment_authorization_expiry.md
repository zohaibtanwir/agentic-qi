# BR003: Payment Authorization Expiry

**Entity**: payment
**Severity**: warning

## Description
Payment authorizations expire after 7 days

## Condition
After payment authorization

## Constraint
Authorization valid for 7 days

## Validation Logic
```python

            if (current_time - authorization.created_at).days >= 7:
                void_authorization(authorization.id)
                return False
            return True
        
```
