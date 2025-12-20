# BR001: Cart Minimum Order Value

**Entity**: cart
**Severity**: error

## Description
Shopping cart must have minimum order value of $1.00 to proceed to checkout

## Condition
When customer attempts to checkout

## Constraint
Cart total >= $1.00

## Validation Logic
```python

            if cart.total_amount < 1.00:
                raise ValidationError("Minimum order value is $1.00")
            return True
        
```
