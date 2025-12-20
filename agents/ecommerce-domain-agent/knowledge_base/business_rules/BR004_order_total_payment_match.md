# BR004: Order Total Payment Match

**Entity**: order
**Severity**: error

## Description
Order total must match payment amount

## Condition
When processing payment for order

## Constraint
order.total == payment.amount

## Validation Logic
```python

            if abs(order.total - payment.amount) > 0.01:
                raise ValidationError("Payment amount doesn't match order total")
            return True
        
```
