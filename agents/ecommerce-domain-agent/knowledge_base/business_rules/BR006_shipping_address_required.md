# BR006: Shipping Address Required

**Entity**: order
**Severity**: error

## Description
Physical items require shipping address

## Condition
When order contains physical products

## Constraint
Shipping address must be complete

## Validation Logic
```python

            if order.has_physical_items and not order.shipping_address:
                raise ValidationError("Shipping address required for physical items")
            return True
        
```
