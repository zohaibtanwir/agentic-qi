# BR009: Loyalty Points Minimum

**Entity**: customer
**Severity**: warning

## Description
Minimum 500 points required for redemption

## Condition
When redeeming loyalty points

## Constraint
Points >= 500

## Validation Logic
```python

            if points_to_redeem < 500:
                raise ValidationError("Minimum 500 points required for redemption")
            return True
        
```
