# BR008: Unique Customer Email

**Entity**: customer
**Severity**: error

## Description
Email addresses must be unique across customers

## Condition
When creating or updating customer

## Constraint
Email must be unique

## Validation Logic
```python

            if customer_exists_with_email(email):
                raise ValidationError("Email already registered")
            return True
        
```
