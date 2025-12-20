# EC006: Split Shipment Tracking

**Category**: complexity
**Entity**: shipping
**Workflow**: fulfillment
**Severity**: medium

## Description
Single order shipped in multiple packages

## Test Approach
Create order with items from different warehouses

## Expected Behavior
Consolidated tracking with all packages

## Example Test Data
```json
{
  "order_id": "ORD-123",
  "packages": [
    {
      "tracking": "TRACK001",
      "warehouse": "WH-EAST"
    },
    {
      "tracking": "TRACK002",
      "warehouse": "WH-WEST"
    }
  ]
}
```
