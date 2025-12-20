# BR002: Cart Item Quantity Limits

**Entity**: cart
**Severity**: error

## Description
Item quantity must be between 1 and 99

## Condition
When adding or updating cart items

## Constraint
1 <= quantity <= 99

## Validation Logic
```python

            if item.quantity < 1 or item.quantity > 99:
                raise ValidationError("Quantity must be between 1 and 99")
            return True
        
```
