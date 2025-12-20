# TS003: International Checkout Flow

**Entity**: order

## Description
Complete international checkout testing

## Test Data
```json
{
  "countries": [
    "US",
    "GB",
    "DE",
    "JP",
    "AU"
  ],
  "currencies": [
    "USD",
    "GBP",
    "EUR",
    "JPY",
    "AUD"
  ],
  "payment_methods": [
    "card",
    "paypal",
    "local"
  ],
  "shipping_methods": [
    "standard",
    "express",
    "economy"
  ]
}
```

## Success Criteria
```json
{
  "tax_accuracy": "100%",
  "currency_conversion": "accurate",
  "address_validation": "working",
  "customs_forms": "generated"
}
```
