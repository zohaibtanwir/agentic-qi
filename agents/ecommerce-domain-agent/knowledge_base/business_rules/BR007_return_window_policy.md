# BR007: Return Window Policy

**Entity**: return
**Severity**: error

## Description
Items can be returned within 30 days of delivery

## Condition
When initiating return

## Constraint
Return within 30 days of delivery

## Validation Logic
```python

            if (current_date - delivery_date).days > 30:
                raise ValidationError("Return window has expired")
            return True
        
```
