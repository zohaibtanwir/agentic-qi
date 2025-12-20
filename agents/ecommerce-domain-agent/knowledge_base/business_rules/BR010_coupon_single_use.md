# BR010: Coupon Single Use

**Entity**: discount
**Severity**: error

## Description
Single-use coupons can only be used once per customer

## Condition
When applying coupon

## Constraint
One use per customer

## Validation Logic
```python

            if coupon.single_use and customer_used_coupon(customer_id, coupon_code):
                raise ValidationError("Coupon already used")
            return True
        
```
