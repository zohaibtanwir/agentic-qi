# EC009: International Tax Calculation

**Category**: compliance
**Entity**: order
**Workflow**: international_checkout
**Severity**: critical

## Description
Complex tax calculation for international orders

## Test Approach
Test various country/state combinations

## Expected Behavior
Accurate VAT/GST calculation

## Example Test Data
```json
{
  "shipping_country": "GB",
  "order_value": 150.0,
  "vat_rate": 0.2,
  "customs_threshold": 135.0
}
```
