# BR005: Inventory Reservation Timeout

**Entity**: inventory
**Severity**: warning

## Description
Inventory reservations expire after 15 minutes

## Condition
When item added to cart

## Constraint
Reservation valid for 15 minutes

## Validation Logic
```python

            if (current_time - reservation.created_at).minutes > 15:
                release_reservation(reservation.id)
                return False
            return True
        
```
