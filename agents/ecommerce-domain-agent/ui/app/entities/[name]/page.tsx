"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Database, Link2, Shield, AlertCircle, CheckCircle } from "lucide-react";

// Complete entity data for all eCommerce domain entities
const entitiesData: Record<string, any> = {
  // Shopping Cart entities
  cart: {
    name: "cart",
    displayName: "Shopping Cart",
    description: "Shopping cart containing items selected for purchase before checkout",
    category: "transactional",
    fields: [
      { name: "id", type: "string", required: true, description: "Unique cart identifier" },
      { name: "userId", type: "string", required: true, description: "User who owns the cart" },
      { name: "sessionId", type: "string", required: false, description: "Session identifier for guest carts" },
      { name: "items", type: "array", required: true, description: "Array of cart items" },
      { name: "subtotal", type: "decimal", required: true, description: "Total before tax and shipping" },
      { name: "tax", type: "decimal", required: true, description: "Calculated tax amount" },
      { name: "total", type: "decimal", required: true, description: "Final total including tax" },
      { name: "createdAt", type: "datetime", required: true, description: "When cart was created" },
      { name: "updatedAt", type: "datetime", required: true, description: "Last update timestamp" },
      { name: "expiresAt", type: "datetime", required: false, description: "Cart expiration time" },
      { name: "status", type: "enum", required: true, description: "Cart status (active, abandoned, converted)" },
    ],
    relationships: [
      { target: "user", type: "belongs_to", description: "Cart belongs to a user" },
      { target: "cart_item", type: "has_many", description: "Cart contains multiple items" },
    ],
    businessRules: [
      "Cart expires after 30 days of inactivity",
      "Maximum 100 items per cart",
      "Prices recalculated on each view",
      "Guest carts converted on registration",
      "Abandoned cart emails after 24 hours",
    ],
    edgeCases: [
      "Empty cart handling",
      "Expired product prices",
      "Out of stock items",
      "Multiple currency support",
      "Tax calculation errors",
      "Session timeout during checkout",
    ],
    testScenarios: [
      { name: "Happy Path", description: "Standard cart with valid items" },
      { name: "Empty Cart", description: "Cart with no items" },
      { name: "Large Cart", description: "Cart with 100+ items" },
      { name: "Expired Items", description: "Cart with discontinued products" },
      { name: "Mixed Currencies", description: "Items with different currencies" },
    ],
  },
  order: {
    name: "order",
    displayName: "Order",
    description: "Confirmed purchase order after successful checkout process",
    category: "transactional",
    fields: [
      { name: "id", type: "string", required: true, description: "Unique order identifier" },
      { name: "orderNumber", type: "string", required: true, description: "Human-readable order number" },
      { name: "customerId", type: "string", required: true, description: "Customer who placed the order" },
      { name: "items", type: "array", required: true, description: "Ordered items" },
      { name: "subtotal", type: "decimal", required: true, description: "Total before tax and shipping" },
      { name: "tax", type: "decimal", required: true, description: "Tax amount" },
      { name: "shipping", type: "decimal", required: true, description: "Shipping cost" },
      { name: "total", type: "decimal", required: true, description: "Final total amount" },
      { name: "status", type: "enum", required: true, description: "Order status" },
      { name: "paymentStatus", type: "enum", required: true, description: "Payment status" },
      { name: "shippingAddress", type: "object", required: true, description: "Delivery address" },
      { name: "billingAddress", type: "object", required: true, description: "Billing address" },
      { name: "createdAt", type: "datetime", required: true, description: "Order placement time" },
    ],
    relationships: [
      { target: "customer", type: "belongs_to", description: "Order belongs to customer" },
      { target: "order_item", type: "has_many", description: "Order contains items" },
      { target: "payment", type: "has_one", description: "Order has payment" },
      { target: "shipment", type: "has_many", description: "Order may have multiple shipments" },
    ],
    businessRules: [
      "Order cannot be modified after confirmation",
      "Refunds allowed within 30 days",
      "Shipping address validation required",
      "Payment must be authorized before fulfillment",
      "Order status transitions are one-way",
    ],
    edgeCases: [
      "Split shipments",
      "Partial refunds",
      "International orders",
      "Tax-exempt customers",
      "Order cancellation after shipment",
      "Payment failure after confirmation",
    ],
    testScenarios: [
      { name: "Standard Order", description: "Single shipment, standard items" },
      { name: "Split Shipment", description: "Multiple shipments for one order" },
      { name: "International", description: "Cross-border order with customs" },
      { name: "Subscription", description: "Recurring order" },
      { name: "B2B Order", description: "Business customer with tax exemption" },
    ],
  },
  payment: {
    name: "payment",
    displayName: "Payment",
    description: "Payment transaction record for order processing",
    category: "financial",
    fields: [
      { name: "id", type: "string", required: true, description: "Payment transaction ID" },
      { name: "orderId", type: "string", required: true, description: "Associated order" },
      { name: "amount", type: "decimal", required: true, description: "Payment amount" },
      { name: "currency", type: "string", required: true, description: "Currency code" },
      { name: "method", type: "enum", required: true, description: "Payment method" },
      { name: "status", type: "enum", required: true, description: "Payment status" },
      { name: "gateway", type: "string", required: true, description: "Payment gateway used" },
      { name: "transactionId", type: "string", required: false, description: "Gateway transaction ID" },
      { name: "authCode", type: "string", required: false, description: "Authorization code" },
      { name: "processedAt", type: "datetime", required: true, description: "Processing timestamp" },
    ],
    relationships: [
      { target: "order", type: "belongs_to", description: "Payment for an order" },
      { target: "customer", type: "belongs_to", description: "Payment by customer" },
      { target: "refund", type: "has_many", description: "Payment may have refunds" },
    ],
    businessRules: [
      "PCI compliance required",
      "3D Secure for high-value transactions",
      "Automatic retry for failures",
      "Fraud detection rules applied",
      "Settlement within 2-3 business days",
    ],
    edgeCases: [
      "Payment gateway timeout",
      "Duplicate payment attempts",
      "Currency conversion",
      "Partial payments",
      "Chargeback handling",
      "Network failures during processing",
    ],
    testScenarios: [
      { name: "Successful Payment", description: "Standard credit card payment" },
      { name: "Failed Payment", description: "Insufficient funds" },
      { name: "3D Secure", description: "Additional authentication required" },
      { name: "Multiple Methods", description: "Split payment across methods" },
      { name: "Refund", description: "Full or partial refund" },
    ],
  },

  // Customer Management
  customer: {
    name: "customer",
    displayName: "Customer",
    description: "Registered customer profile with purchase history and preferences",
    category: "user_management",
    fields: [
      { name: "id", type: "string", required: true, description: "Unique customer identifier" },
      { name: "email", type: "string", required: true, description: "Primary email address" },
      { name: "firstName", type: "string", required: true, description: "Customer first name" },
      { name: "lastName", type: "string", required: true, description: "Customer last name" },
      { name: "phone", type: "string", required: false, description: "Contact phone number" },
      { name: "dateOfBirth", type: "date", required: false, description: "Birth date for age verification" },
      { name: "gender", type: "enum", required: false, description: "Gender preference" },
      { name: "loyaltyTier", type: "enum", required: true, description: "Loyalty program tier" },
      { name: "loyaltyPoints", type: "integer", required: true, description: "Current loyalty points balance" },
      { name: "lifetimeValue", type: "decimal", required: true, description: "Total purchase value" },
      { name: "registeredAt", type: "datetime", required: true, description: "Registration timestamp" },
      { name: "lastLoginAt", type: "datetime", required: false, description: "Last login timestamp" },
      { name: "status", type: "enum", required: true, description: "Account status (active, suspended, deleted)" },
    ],
    relationships: [
      { target: "order", type: "has_many", description: "Customer has multiple orders" },
      { target: "address", type: "has_many", description: "Customer has multiple addresses" },
      { target: "payment_method", type: "has_many", description: "Customer saved payment methods" },
      { target: "wishlist", type: "has_many", description: "Customer wishlists" },
      { target: "review", type: "has_many", description: "Product reviews by customer" },
    ],
    businessRules: [
      "Email must be unique across system",
      "Age verification required for restricted products",
      "Loyalty points expire after 12 months",
      "Tier upgrades based on annual spend",
      "GDPR compliance for data retention",
      "Account deletion after 5 years of inactivity",
    ],
    edgeCases: [
      "Duplicate account detection",
      "Account merge after guest checkout",
      "International phone number formats",
      "Loyalty point adjustments",
      "Account recovery without email",
      "Minor age restrictions",
    ],
    testScenarios: [
      { name: "New Registration", description: "First-time customer signup" },
      { name: "VIP Customer", description: "High-value customer with platinum tier" },
      { name: "Inactive Account", description: "Customer hasn't logged in for 2+ years" },
      { name: "Guest to Registered", description: "Guest checkout converting to account" },
      { name: "International Customer", description: "Non-US customer with different formats" },
    ],
  },

  // Inventory Management
  inventory: {
    name: "inventory",
    displayName: "Inventory",
    description: "Real-time inventory tracking and stock management",
    category: "catalog",
    fields: [
      { name: "id", type: "string", required: true, description: "Inventory record ID" },
      { name: "sku", type: "string", required: true, description: "Stock keeping unit" },
      { name: "productId", type: "string", required: true, description: "Associated product" },
      { name: "warehouseId", type: "string", required: true, description: "Warehouse location" },
      { name: "quantityOnHand", type: "integer", required: true, description: "Current stock level" },
      { name: "quantityAvailable", type: "integer", required: true, description: "Available for sale" },
      { name: "quantityReserved", type: "integer", required: true, description: "Reserved for orders" },
      { name: "quantityInTransit", type: "integer", required: false, description: "Stock being transferred" },
      { name: "reorderPoint", type: "integer", required: true, description: "Minimum stock trigger" },
      { name: "reorderQuantity", type: "integer", required: true, description: "Standard reorder amount" },
      { name: "lastRestockedAt", type: "datetime", required: false, description: "Last restock timestamp" },
      { name: "nextRestockDate", type: "date", required: false, description: "Expected restock date" },
      { name: "cost", type: "decimal", required: true, description: "Unit cost" },
    ],
    relationships: [
      { target: "product", type: "belongs_to", description: "Inventory for a product" },
      { target: "warehouse", type: "belongs_to", description: "Located in warehouse" },
      { target: "inventory_movement", type: "has_many", description: "Stock movement history" },
      { target: "purchase_order", type: "has_many", description: "Related purchase orders" },
    ],
    businessRules: [
      "Available quantity cannot exceed on-hand quantity",
      "Reserved stock released after 24 hours if not purchased",
      "Automatic reorder when hitting reorder point",
      "FIFO for stock rotation",
      "Safety stock maintained for high-demand items",
      "Real-time sync across all channels",
    ],
    edgeCases: [
      "Negative inventory scenarios",
      "Overselling prevention",
      "Multi-warehouse allocation",
      "Stock reconciliation discrepancies",
      "Damaged goods handling",
      "Seasonal stock adjustments",
      "Drop-ship inventory tracking",
    ],
    testScenarios: [
      { name: "Low Stock Alert", description: "Inventory below reorder point" },
      { name: "Out of Stock", description: "Zero availability scenario" },
      { name: "Overstock", description: "Excess inventory management" },
      { name: "Multi-Location", description: "Stock across multiple warehouses" },
      { name: "Reserved Stock", description: "Inventory reserved for pending orders" },
    ],
  },

  // Product Catalog
  product: {
    name: "product",
    displayName: "Product",
    description: "Product catalog item with pricing, attributes, and media",
    category: "catalog",
    fields: [
      { name: "id", type: "string", required: true, description: "Product identifier" },
      { name: "sku", type: "string", required: true, description: "Stock keeping unit" },
      { name: "name", type: "string", required: true, description: "Product name" },
      { name: "description", type: "text", required: true, description: "Detailed description" },
      { name: "shortDescription", type: "string", required: false, description: "Brief summary" },
      { name: "brand", type: "string", required: true, description: "Brand name" },
      { name: "categoryId", type: "string", required: true, description: "Primary category" },
      { name: "price", type: "decimal", required: true, description: "Base price" },
      { name: "compareAtPrice", type: "decimal", required: false, description: "Original price for sale items" },
      { name: "cost", type: "decimal", required: true, description: "Product cost" },
      { name: "weight", type: "decimal", required: false, description: "Shipping weight" },
      { name: "dimensions", type: "object", required: false, description: "Product dimensions" },
      { name: "images", type: "array", required: true, description: "Product images" },
      { name: "status", type: "enum", required: true, description: "Product status (active, draft, archived)" },
      { name: "publishedAt", type: "datetime", required: false, description: "Publishing timestamp" },
    ],
    relationships: [
      { target: "category", type: "belongs_to", description: "Product in category" },
      { target: "brand", type: "belongs_to", description: "Product from brand" },
      { target: "inventory", type: "has_many", description: "Inventory records" },
      { target: "variant", type: "has_many", description: "Product variants" },
      { target: "review", type: "has_many", description: "Customer reviews" },
      { target: "related_product", type: "has_many", description: "Related products" },
    ],
    businessRules: [
      "SKU must be unique",
      "At least one image required",
      "Price must be greater than cost",
      "Category assignment required",
      "SEO-friendly URLs generated from name",
      "Variant prices inherit from parent if not specified",
    ],
    edgeCases: [
      "Digital products without shipping",
      "Bundle products with components",
      "Configurable products",
      "Products with dynamic pricing",
      "Pre-order products",
      "Discontinued products with existing orders",
      "Gift cards and virtual products",
    ],
    testScenarios: [
      { name: "Simple Product", description: "Basic product without variants" },
      { name: "Variable Product", description: "Product with size/color variants" },
      { name: "Bundle Product", description: "Product sold as a bundle" },
      { name: "Digital Product", description: "Downloadable or virtual product" },
      { name: "Sale Product", description: "Product with discount pricing" },
    ],
  },

  // Shipping
  shipping: {
    name: "shipping",
    displayName: "Shipping",
    description: "Shipping methods, rates, and delivery tracking",
    category: "fulfillment",
    fields: [
      { name: "id", type: "string", required: true, description: "Shipping record ID" },
      { name: "orderId", type: "string", required: true, description: "Associated order" },
      { name: "carrier", type: "string", required: true, description: "Shipping carrier" },
      { name: "service", type: "string", required: true, description: "Service level" },
      { name: "trackingNumber", type: "string", required: false, description: "Tracking identifier" },
      { name: "status", type: "enum", required: true, description: "Shipment status" },
      { name: "estimatedDelivery", type: "date", required: true, description: "Expected delivery date" },
      { name: "actualDelivery", type: "datetime", required: false, description: "Actual delivery timestamp" },
      { name: "shippingCost", type: "decimal", required: true, description: "Shipping charge" },
      { name: "weight", type: "decimal", required: true, description: "Package weight" },
      { name: "dimensions", type: "object", required: false, description: "Package dimensions" },
      { name: "shippedAt", type: "datetime", required: false, description: "Ship timestamp" },
      { name: "deliveredAt", type: "datetime", required: false, description: "Delivery timestamp" },
    ],
    relationships: [
      { target: "order", type: "belongs_to", description: "Shipping for order" },
      { target: "shipping_address", type: "has_one", description: "Delivery address" },
      { target: "tracking_event", type: "has_many", description: "Tracking updates" },
      { target: "shipment_item", type: "has_many", description: "Items in shipment" },
    ],
    businessRules: [
      "Tracking number required for all carriers",
      "Address validation before shipping",
      "Insurance required for high-value orders",
      "Signature required for orders over $500",
      "International shipping requires customs forms",
      "Same-day delivery cutoff at 12 PM",
    ],
    edgeCases: [
      "Split shipments for single order",
      "Failed delivery attempts",
      "Address correction mid-transit",
      "Lost package claims",
      "International customs delays",
      "Holiday shipping surcharges",
      "Oversized item handling",
    ],
    testScenarios: [
      { name: "Standard Shipping", description: "Regular ground shipping" },
      { name: "Express Shipping", description: "Next-day or 2-day delivery" },
      { name: "International", description: "Cross-border shipping" },
      { name: "Split Shipment", description: "Order shipped in multiple packages" },
      { name: "Failed Delivery", description: "Undeliverable package scenario" },
    ],
  },

  // Promotions
  promotion: {
    name: "promotion",
    displayName: "Promotion",
    description: "Discounts, coupons, and promotional campaigns",
    category: "marketing",
    fields: [
      { name: "id", type: "string", required: true, description: "Promotion identifier" },
      { name: "code", type: "string", required: false, description: "Promo code" },
      { name: "name", type: "string", required: true, description: "Promotion name" },
      { name: "description", type: "text", required: true, description: "Promotion details" },
      { name: "type", type: "enum", required: true, description: "Promotion type (percentage, fixed, bogo)" },
      { name: "value", type: "decimal", required: true, description: "Discount value" },
      { name: "minimumPurchase", type: "decimal", required: false, description: "Minimum order amount" },
      { name: "usageLimit", type: "integer", required: false, description: "Total usage limit" },
      { name: "usagePerCustomer", type: "integer", required: false, description: "Per-customer limit" },
      { name: "startDate", type: "datetime", required: true, description: "Promotion start" },
      { name: "endDate", type: "datetime", required: true, description: "Promotion end" },
      { name: "status", type: "enum", required: true, description: "Active, scheduled, expired" },
    ],
    relationships: [
      { target: "product", type: "has_many", description: "Applicable products" },
      { target: "category", type: "has_many", description: "Applicable categories" },
      { target: "customer_segment", type: "has_many", description: "Target segments" },
      { target: "order", type: "has_many", description: "Orders using promotion" },
    ],
    businessRules: [
      "Promotions cannot be combined unless specified",
      "Automatic application for eligible carts",
      "Expiration enforced at checkout",
      "Minimum purchase calculated before tax",
      "Free shipping promotions override shipping rates",
      "Tiered promotions apply highest eligible discount",
    ],
    edgeCases: [
      "Multiple promotion conflicts",
      "Promotion on already discounted items",
      "Retroactive promotion application",
      "Cart abandonment with active promotion",
      "Promotion code sharing/abuse",
      "Time zone considerations for start/end",
    ],
    testScenarios: [
      { name: "Percentage Discount", description: "20% off entire order" },
      { name: "Fixed Discount", description: "$10 off orders over $50" },
      { name: "BOGO", description: "Buy one get one free promotion" },
      { name: "Free Shipping", description: "Free shipping on qualifying orders" },
      { name: "Tiered Discount", description: "Progressive discounts based on spend" },
    ],
  },

  // Reviews
  review: {
    name: "review",
    displayName: "Review",
    description: "Product reviews and ratings from customers",
    category: "engagement",
    fields: [
      { name: "id", type: "string", required: true, description: "Review identifier" },
      { name: "productId", type: "string", required: true, description: "Reviewed product" },
      { name: "customerId", type: "string", required: true, description: "Review author" },
      { name: "orderId", type: "string", required: false, description: "Associated order" },
      { name: "rating", type: "integer", required: true, description: "Star rating (1-5)" },
      { name: "title", type: "string", required: true, description: "Review title" },
      { name: "comment", type: "text", required: true, description: "Review text" },
      { name: "verified", type: "boolean", required: true, description: "Verified purchase" },
      { name: "helpful", type: "integer", required: false, description: "Helpful vote count" },
      { name: "images", type: "array", required: false, description: "Review photos" },
      { name: "status", type: "enum", required: true, description: "Pending, approved, rejected" },
      { name: "createdAt", type: "datetime", required: true, description: "Review date" },
    ],
    relationships: [
      { target: "product", type: "belongs_to", description: "Review for product" },
      { target: "customer", type: "belongs_to", description: "Review by customer" },
      { target: "order", type: "belongs_to", description: "Review from order" },
      { target: "review_response", type: "has_one", description: "Merchant response" },
    ],
    businessRules: [
      "Reviews only after order delivery",
      "One review per product per order",
      "Profanity filter applied automatically",
      "Verified badge for confirmed purchases",
      "Reviews affect product rating calculation",
      "30-day window for leaving reviews",
    ],
    edgeCases: [
      "Fake review detection",
      "Review bombing prevention",
      "Edited review versioning",
      "Anonymous review handling",
      "Review incentive compliance",
      "Multi-language reviews",
    ],
    testScenarios: [
      { name: "Positive Review", description: "5-star satisfied customer" },
      { name: "Negative Review", description: "1-star complaint" },
      { name: "Detailed Review", description: "Review with photos and long text" },
      { name: "Verified Purchase", description: "Review from confirmed buyer" },
      { name: "Moderated Review", description: "Review requiring moderation" },
    ],
  },

  // Wishlist
  wishlist: {
    name: "wishlist",
    displayName: "Wishlist",
    description: "Customer saved items for future purchase",
    category: "personalization",
    fields: [
      { name: "id", type: "string", required: true, description: "Wishlist identifier" },
      { name: "customerId", type: "string", required: true, description: "Wishlist owner" },
      { name: "name", type: "string", required: true, description: "Wishlist name" },
      { name: "description", type: "text", required: false, description: "Wishlist description" },
      { name: "visibility", type: "enum", required: true, description: "Public, private, shared" },
      { name: "items", type: "array", required: true, description: "Wishlist items" },
      { name: "shareToken", type: "string", required: false, description: "Sharing token" },
      { name: "createdAt", type: "datetime", required: true, description: "Creation date" },
      { name: "updatedAt", type: "datetime", required: true, description: "Last update" },
    ],
    relationships: [
      { target: "customer", type: "belongs_to", description: "Wishlist owner" },
      { target: "wishlist_item", type: "has_many", description: "Items in wishlist" },
      { target: "share", type: "has_many", description: "Wishlist shares" },
    ],
    businessRules: [
      "Default wishlist created on first save",
      "Maximum 10 wishlists per customer",
      "Items removed when out of stock for 90 days",
      "Price drop notifications for wishlist items",
      "Shared wishlists expire after 1 year",
      "Registry wishlists for special events",
    ],
    edgeCases: [
      "Product discontinuation in wishlist",
      "Price changes for wishlist items",
      "Wishlist merging on account merge",
      "Gift registry fulfillment tracking",
      "Anonymous wishlist conversion",
      "Wishlist item availability changes",
    ],
    testScenarios: [
      { name: "Private Wishlist", description: "Personal wishlist" },
      { name: "Gift Registry", description: "Wedding or baby registry" },
      { name: "Shared Wishlist", description: "Wishlist shared with family" },
      { name: "Price Alert", description: "Wishlist with price tracking" },
      { name: "Holiday Wishlist", description: "Seasonal gift list" },
    ],
  },

  // Returns
  return_request: {
    name: "return_request",
    displayName: "Return Request",
    description: "Product return and exchange requests",
    category: "customer_service",
    fields: [
      { name: "id", type: "string", required: true, description: "Return request ID" },
      { name: "orderId", type: "string", required: true, description: "Original order" },
      { name: "customerId", type: "string", required: true, description: "Customer requesting return" },
      { name: "items", type: "array", required: true, description: "Items being returned" },
      { name: "reason", type: "enum", required: true, description: "Return reason" },
      { name: "type", type: "enum", required: true, description: "Return, exchange, store credit" },
      { name: "status", type: "enum", required: true, description: "Request status" },
      { name: "rmaNumber", type: "string", required: false, description: "Return authorization number" },
      { name: "shippingLabel", type: "string", required: false, description: "Return shipping label" },
      { name: "refundAmount", type: "decimal", required: false, description: "Refund total" },
      { name: "createdAt", type: "datetime", required: true, description: "Request date" },
      { name: "resolvedAt", type: "datetime", required: false, description: "Resolution date" },
    ],
    relationships: [
      { target: "order", type: "belongs_to", description: "Return for order" },
      { target: "customer", type: "belongs_to", description: "Return by customer" },
      { target: "refund", type: "has_one", description: "Associated refund" },
      { target: "return_shipment", type: "has_one", description: "Return shipping" },
    ],
    businessRules: [
      "Returns allowed within 30 days",
      "Original packaging required for electronics",
      "Restocking fee for opened items",
      "Free returns for defective products",
      "Exchange processed as return plus new order",
      "Store credit valid for 1 year",
    ],
    edgeCases: [
      "Partial return processing",
      "Return without receipt",
      "Damaged return shipment",
      "Return fraud detection",
      "International return handling",
      "Return of personalized items",
      "Warranty vs return policy conflicts",
    ],
    testScenarios: [
      { name: "Simple Return", description: "Full order return" },
      { name: "Partial Return", description: "Some items from order" },
      { name: "Exchange", description: "Size or color exchange" },
      { name: "Defective Return", description: "Damaged product return" },
      { name: "Store Credit", description: "Return for store credit" },
    ],
  },

  // Gift Cards
  gift_card: {
    name: "gift_card",
    displayName: "Gift Card",
    description: "Digital and physical gift cards",
    category: "payment",
    fields: [
      { name: "id", type: "string", required: true, description: "Gift card identifier" },
      { name: "code", type: "string", required: true, description: "Redemption code" },
      { name: "pin", type: "string", required: false, description: "Security PIN" },
      { name: "type", type: "enum", required: true, description: "Physical or digital" },
      { name: "initialBalance", type: "decimal", required: true, description: "Starting balance" },
      { name: "currentBalance", type: "decimal", required: true, description: "Remaining balance" },
      { name: "currency", type: "string", required: true, description: "Currency code" },
      { name: "purchaserId", type: "string", required: false, description: "Buyer customer ID" },
      { name: "recipientEmail", type: "string", required: false, description: "Recipient for digital cards" },
      { name: "message", type: "text", required: false, description: "Gift message" },
      { name: "issuedAt", type: "datetime", required: true, description: "Issue date" },
      { name: "expiresAt", type: "datetime", required: false, description: "Expiration date" },
      { name: "status", type: "enum", required: true, description: "Active, used, expired, cancelled" },
    ],
    relationships: [
      { target: "order", type: "belongs_to", description: "Purchase order" },
      { target: "customer", type: "belongs_to", description: "Purchaser" },
      { target: "transaction", type: "has_many", description: "Usage transactions" },
    ],
    businessRules: [
      "Non-refundable once issued",
      "Cannot be used to purchase gift cards",
      "Balance check without redemption",
      "Partial redemption allowed",
      "Lost card replacement with proof of purchase",
      "Corporate bulk purchase discounts",
    ],
    edgeCases: [
      "Partial balance usage",
      "Multiple gift cards on single order",
      "Gift card fraud prevention",
      "International currency conversion",
      "Expired card reactivation",
      "Lost physical card replacement",
      "Gift card as change for returns",
    ],
    testScenarios: [
      { name: "Digital Gift Card", description: "Email delivery gift card" },
      { name: "Physical Card", description: "Plastic gift card" },
      { name: "Partial Use", description: "Using part of balance" },
      { name: "Multiple Cards", description: "Multiple cards on order" },
      { name: "Corporate Bulk", description: "Bulk purchase for company" },
    ],
  },

  // Subscriptions
  subscription: {
    name: "subscription",
    displayName: "Subscription",
    description: "Recurring product subscriptions",
    category: "recurring",
    fields: [
      { name: "id", type: "string", required: true, description: "Subscription identifier" },
      { name: "customerId", type: "string", required: true, description: "Subscriber" },
      { name: "productId", type: "string", required: true, description: "Subscription product" },
      { name: "frequency", type: "enum", required: true, description: "Weekly, monthly, quarterly" },
      { name: "quantity", type: "integer", required: true, description: "Items per delivery" },
      { name: "price", type: "decimal", required: true, description: "Subscription price" },
      { name: "discount", type: "decimal", required: false, description: "Subscription discount" },
      { name: "nextDelivery", type: "date", required: true, description: "Next shipment date" },
      { name: "status", type: "enum", required: true, description: "Active, paused, cancelled" },
      { name: "startDate", type: "date", required: true, description: "Subscription start" },
      { name: "endDate", type: "date", required: false, description: "Cancellation date" },
      { name: "paymentMethodId", type: "string", required: true, description: "Payment method" },
    ],
    relationships: [
      { target: "customer", type: "belongs_to", description: "Subscriber" },
      { target: "product", type: "belongs_to", description: "Subscription product" },
      { target: "subscription_order", type: "has_many", description: "Generated orders" },
      { target: "payment_method", type: "belongs_to", description: "Payment source" },
    ],
    businessRules: [
      "First order ships immediately",
      "Skip or reschedule up to 3 times per year",
      "10% discount for subscriptions",
      "Auto-pause after 3 failed payments",
      "Cancellation effective after current period",
      "Price changes with 30-day notice",
    ],
    edgeCases: [
      "Payment failure handling",
      "Product unavailability",
      "Address change mid-cycle",
      "Subscription upgrade/downgrade",
      "Pause and resume logic",
      "Proration calculations",
      "Gift subscriptions",
    ],
    testScenarios: [
      { name: "New Subscription", description: "First-time subscriber" },
      { name: "Skip Delivery", description: "Customer skips next delivery" },
      { name: "Payment Failure", description: "Failed payment retry" },
      { name: "Subscription Change", description: "Modify frequency or quantity" },
      { name: "Cancellation", description: "Customer cancels subscription" },
    ],
  },

  // Additional Catalog Entities
  category: {
    name: "category",
    displayName: "Category",
    description: "Product categories and taxonomy hierarchy",
    category: "catalog",
    fields: [
      { name: "id", type: "string", required: true, description: "Category identifier" },
      { name: "name", type: "string", required: true, description: "Category name" },
      { name: "slug", type: "string", required: true, description: "URL-friendly identifier" },
      { name: "description", type: "text", required: false, description: "Category description" },
      { name: "parentId", type: "string", required: false, description: "Parent category for hierarchy" },
      { name: "level", type: "integer", required: true, description: "Hierarchy level" },
      { name: "path", type: "string", required: true, description: "Full category path" },
      { name: "image", type: "string", required: false, description: "Category image URL" },
      { name: "displayOrder", type: "integer", required: true, description: "Display sequence" },
      { name: "isActive", type: "boolean", required: true, description: "Category visibility" },
      { name: "productCount", type: "integer", required: true, description: "Number of products" },
    ],
    relationships: [
      { target: "product", type: "has_many", description: "Products in category" },
      { target: "category", type: "has_many", description: "Subcategories" },
      { target: "category", type: "belongs_to", description: "Parent category" },
    ],
    businessRules: [
      "Maximum 5 levels of category depth",
      "Unique slug required per level",
      "Cannot delete category with products",
      "Automatic breadcrumb generation",
      "SEO metadata inheritance from parent",
    ],
    edgeCases: [
      "Circular category references",
      "Orphaned categories",
      "Category merge operations",
      "Multi-store category visibility",
      "Dynamic category assignment",
    ],
    testScenarios: [
      { name: "Root Category", description: "Top-level category" },
      { name: "Nested Category", description: "Multi-level hierarchy" },
      { name: "Empty Category", description: "Category without products" },
      { name: "Large Category", description: "Category with 1000+ products" },
    ],
  },

  brand: {
    name: "brand",
    displayName: "Brand",
    description: "Product brands and manufacturers",
    category: "catalog",
    fields: [
      { name: "id", type: "string", required: true, description: "Brand identifier" },
      { name: "name", type: "string", required: true, description: "Brand name" },
      { name: "slug", type: "string", required: true, description: "URL-friendly identifier" },
      { name: "description", type: "text", required: false, description: "Brand description" },
      { name: "logo", type: "string", required: false, description: "Brand logo URL" },
      { name: "website", type: "string", required: false, description: "Brand website" },
      { name: "countryOfOrigin", type: "string", required: false, description: "Manufacturing country" },
      { name: "isActive", type: "boolean", required: true, description: "Brand status" },
      { name: "tier", type: "enum", required: false, description: "Premium, standard, budget" },
    ],
    relationships: [
      { target: "product", type: "has_many", description: "Products from brand" },
      { target: "vendor", type: "belongs_to", description: "Brand vendor/supplier" },
    ],
    businessRules: [
      "Unique brand name required",
      "Brand slug must be unique",
      "Cannot delete brand with active products",
      "Brand tier affects pricing rules",
    ],
    edgeCases: [
      "Brand name changes",
      "Multi-brand products",
      "White-label brands",
      "Brand acquisitions/mergers",
    ],
    testScenarios: [
      { name: "Premium Brand", description: "High-tier luxury brand" },
      { name: "New Brand", description: "Recently added brand" },
      { name: "Multi-Category Brand", description: "Brand across categories" },
    ],
  },

  variant: {
    name: "variant",
    displayName: "Product Variant",
    description: "Product variations like size, color, style",
    category: "catalog",
    fields: [
      { name: "id", type: "string", required: true, description: "Variant identifier" },
      { name: "productId", type: "string", required: true, description: "Parent product" },
      { name: "sku", type: "string", required: true, description: "Variant SKU" },
      { name: "attributes", type: "object", required: true, description: "Variant attributes" },
      { name: "price", type: "decimal", required: false, description: "Variant price override" },
      { name: "weight", type: "decimal", required: false, description: "Variant weight" },
      { name: "barcode", type: "string", required: false, description: "UPC/EAN code" },
      { name: "image", type: "string", required: false, description: "Variant image" },
    ],
    relationships: [
      { target: "product", type: "belongs_to", description: "Parent product" },
      { target: "inventory", type: "has_one", description: "Variant inventory" },
    ],
    businessRules: [
      "SKU must be globally unique",
      "At least one attribute required",
      "Price inherits from parent if null",
      "Inventory tracked per variant",
    ],
    edgeCases: [
      "Variant-specific promotions",
      "Out-of-stock variant handling",
      "Variant image fallback",
      "Dynamic variant generation",
    ],
    testScenarios: [
      { name: "Size Variant", description: "Different sizes of product" },
      { name: "Color Variant", description: "Different colors available" },
      { name: "Multi-Attribute", description: "Size and color combinations" },
    ],
  },

  // User Management Entities
  user: {
    name: "user",
    displayName: "User",
    description: "System user account with authentication",
    category: "user_management",
    fields: [
      { name: "id", type: "string", required: true, description: "User identifier" },
      { name: "username", type: "string", required: true, description: "Login username" },
      { name: "email", type: "string", required: true, description: "Email address" },
      { name: "passwordHash", type: "string", required: true, description: "Encrypted password" },
      { name: "role", type: "enum", required: true, description: "User role" },
      { name: "isActive", type: "boolean", required: true, description: "Account status" },
      { name: "lastLogin", type: "datetime", required: false, description: "Last login time" },
      { name: "createdAt", type: "datetime", required: true, description: "Account creation" },
    ],
    relationships: [
      { target: "customer", type: "has_one", description: "Customer profile" },
      { target: "session", type: "has_many", description: "Active sessions" },
    ],
    businessRules: [
      "Email must be unique",
      "Password complexity requirements",
      "Account lockout after failed attempts",
      "Two-factor authentication optional",
    ],
    edgeCases: [
      "Password reset flow",
      "Account recovery",
      "Session management",
      "Role permission changes",
    ],
    testScenarios: [
      { name: "New User", description: "First-time registration" },
      { name: "Admin User", description: "Administrator account" },
      { name: "Locked Account", description: "Too many failed logins" },
    ],
  },

  address: {
    name: "address",
    displayName: "Address",
    description: "Customer addresses for billing and shipping",
    category: "user_management",
    fields: [
      { name: "id", type: "string", required: true, description: "Address identifier" },
      { name: "customerId", type: "string", required: true, description: "Address owner" },
      { name: "type", type: "enum", required: true, description: "Billing or shipping" },
      { name: "isDefault", type: "boolean", required: true, description: "Default address flag" },
      { name: "firstName", type: "string", required: true, description: "Recipient first name" },
      { name: "lastName", type: "string", required: true, description: "Recipient last name" },
      { name: "company", type: "string", required: false, description: "Company name" },
      { name: "street1", type: "string", required: true, description: "Street address line 1" },
      { name: "street2", type: "string", required: false, description: "Street address line 2" },
      { name: "city", type: "string", required: true, description: "City" },
      { name: "state", type: "string", required: true, description: "State/Province" },
      { name: "postalCode", type: "string", required: true, description: "ZIP/Postal code" },
      { name: "country", type: "string", required: true, description: "Country code" },
      { name: "phone", type: "string", required: false, description: "Contact phone" },
    ],
    relationships: [
      { target: "customer", type: "belongs_to", description: "Address owner" },
      { target: "order", type: "has_many", description: "Orders to this address" },
    ],
    businessRules: [
      "Address validation required",
      "One default per type per customer",
      "Cannot delete address with pending orders",
      "International format support",
    ],
    edgeCases: [
      "PO Box restrictions",
      "Military addresses (APO/FPO)",
      "International addresses",
      "Address standardization",
    ],
    testScenarios: [
      { name: "US Address", description: "Standard US address" },
      { name: "International", description: "Non-US address" },
      { name: "PO Box", description: "Post office box address" },
    ],
  },

  // Financial Entities
  invoice: {
    name: "invoice",
    displayName: "Invoice",
    description: "Billing invoice for orders",
    category: "financial",
    fields: [
      { name: "id", type: "string", required: true, description: "Invoice number" },
      { name: "orderId", type: "string", required: true, description: "Related order" },
      { name: "customerId", type: "string", required: true, description: "Invoice recipient" },
      { name: "status", type: "enum", required: true, description: "Draft, sent, paid, overdue" },
      { name: "issueDate", type: "date", required: true, description: "Invoice date" },
      { name: "dueDate", type: "date", required: true, description: "Payment due date" },
      { name: "subtotal", type: "decimal", required: true, description: "Pre-tax total" },
      { name: "tax", type: "decimal", required: true, description: "Tax amount" },
      { name: "total", type: "decimal", required: true, description: "Total due" },
      { name: "paidAmount", type: "decimal", required: true, description: "Amount paid" },
      { name: "notes", type: "text", required: false, description: "Invoice notes" },
    ],
    relationships: [
      { target: "order", type: "belongs_to", description: "Invoice for order" },
      { target: "payment", type: "has_many", description: "Invoice payments" },
      { target: "credit_note", type: "has_many", description: "Credit adjustments" },
    ],
    businessRules: [
      "Sequential invoice numbering",
      "Cannot modify after sending",
      "Automatic overdue status",
      "Tax calculation per jurisdiction",
    ],
    edgeCases: [
      "Partial payments",
      "Currency conversions",
      "Tax exemptions",
      "Invoice corrections",
    ],
    testScenarios: [
      { name: "Standard Invoice", description: "Regular order invoice" },
      { name: "Overdue Invoice", description: "Past due payment" },
      { name: "Partial Payment", description: "Partially paid invoice" },
    ],
  },

  refund: {
    name: "refund",
    displayName: "Refund",
    description: "Payment refunds and adjustments",
    category: "financial",
    fields: [
      { name: "id", type: "string", required: true, description: "Refund identifier" },
      { name: "paymentId", type: "string", required: true, description: "Original payment" },
      { name: "orderId", type: "string", required: true, description: "Related order" },
      { name: "amount", type: "decimal", required: true, description: "Refund amount" },
      { name: "reason", type: "enum", required: true, description: "Refund reason" },
      { name: "status", type: "enum", required: true, description: "Pending, processed, failed" },
      { name: "processedAt", type: "datetime", required: false, description: "Processing time" },
      { name: "notes", type: "text", required: false, description: "Internal notes" },
    ],
    relationships: [
      { target: "payment", type: "belongs_to", description: "Refund of payment" },
      { target: "return_request", type: "belongs_to", description: "Related return" },
    ],
    businessRules: [
      "Cannot exceed original payment",
      "Processing time 3-5 business days",
      "Automatic inventory adjustment",
      "Commission reversal for marketplace",
    ],
    edgeCases: [
      "Partial refunds",
      "Multiple refunds per order",
      "Refund to different method",
      "Currency rate changes",
    ],
    testScenarios: [
      { name: "Full Refund", description: "Complete order refund" },
      { name: "Partial Refund", description: "Partial amount refund" },
      { name: "Failed Refund", description: "Processing failure" },
    ],
  },

  tax: {
    name: "tax",
    displayName: "Tax",
    description: "Tax calculations and rates",
    category: "financial",
    fields: [
      { name: "id", type: "string", required: true, description: "Tax record ID" },
      { name: "jurisdiction", type: "string", required: true, description: "Tax jurisdiction" },
      { name: "type", type: "enum", required: true, description: "Sales, VAT, GST" },
      { name: "rate", type: "decimal", required: true, description: "Tax percentage" },
      { name: "category", type: "string", required: false, description: "Product category" },
      { name: "effectiveDate", type: "date", required: true, description: "Rate effective from" },
      { name: "expiryDate", type: "date", required: false, description: "Rate expiry" },
    ],
    relationships: [
      { target: "order", type: "has_many", description: "Orders with this tax" },
      { target: "location", type: "belongs_to", description: "Tax location" },
    ],
    businessRules: [
      "Nexus determination required",
      "Rate updates quarterly",
      "Exemption certificate validation",
      "Compound tax calculation support",
    ],
    edgeCases: [
      "Tax holidays",
      "Interstate commerce",
      "Digital goods taxation",
      "Tax-exempt customers",
    ],
    testScenarios: [
      { name: "Single Tax", description: "Simple tax calculation" },
      { name: "Compound Tax", description: "Multiple tax types" },
      { name: "Tax Exempt", description: "Exempt customer" },
    ],
  },

  // Analytics Entities
  analytics_event: {
    name: "analytics_event",
    displayName: "Analytics Event",
    description: "User behavior and tracking events",
    category: "analytics",
    fields: [
      { name: "id", type: "string", required: true, description: "Event identifier" },
      { name: "sessionId", type: "string", required: true, description: "User session" },
      { name: "userId", type: "string", required: false, description: "Logged-in user" },
      { name: "eventType", type: "string", required: true, description: "Event category" },
      { name: "eventName", type: "string", required: true, description: "Specific event" },
      { name: "properties", type: "object", required: false, description: "Event data" },
      { name: "timestamp", type: "datetime", required: true, description: "Event time" },
      { name: "source", type: "string", required: true, description: "Web, mobile, api" },
    ],
    relationships: [
      { target: "session", type: "belongs_to", description: "Event in session" },
      { target: "user", type: "belongs_to", description: "Event by user" },
    ],
    businessRules: [
      "Real-time event processing",
      "PII data anonymization",
      "30-day data retention",
      "Batch processing every hour",
    ],
    edgeCases: [
      "High-volume event bursts",
      "Duplicate event detection",
      "Cross-device tracking",
      "Bot traffic filtering",
    ],
    testScenarios: [
      { name: "Page View", description: "User views page" },
      { name: "Add to Cart", description: "Product added to cart" },
      { name: "Purchase", description: "Conversion event" },
    ],
  },

  report: {
    name: "report",
    displayName: "Report",
    description: "Business intelligence and reporting",
    category: "analytics",
    fields: [
      { name: "id", type: "string", required: true, description: "Report identifier" },
      { name: "name", type: "string", required: true, description: "Report name" },
      { name: "type", type: "enum", required: true, description: "Sales, inventory, customer" },
      { name: "frequency", type: "enum", required: true, description: "Daily, weekly, monthly" },
      { name: "parameters", type: "object", required: false, description: "Report filters" },
      { name: "format", type: "enum", required: true, description: "PDF, Excel, CSV" },
      { name: "recipients", type: "array", required: false, description: "Email recipients" },
      { name: "lastRun", type: "datetime", required: false, description: "Last execution" },
      { name: "nextRun", type: "datetime", required: false, description: "Scheduled run" },
    ],
    relationships: [
      { target: "user", type: "belongs_to", description: "Report owner" },
      { target: "report_run", type: "has_many", description: "Execution history" },
    ],
    businessRules: [
      "Scheduled execution limits",
      "Data access permissions",
      "Report caching for performance",
      "Export size limitations",
    ],
    edgeCases: [
      "Large dataset handling",
      "Real-time vs cached data",
      "Cross-timezone scheduling",
      "Failed report delivery",
    ],
    testScenarios: [
      { name: "Sales Report", description: "Daily sales summary" },
      { name: "Inventory Report", description: "Stock levels report" },
      { name: "Custom Report", description: "User-defined metrics" },
    ],
  },

  // Support Entities
  support_ticket: {
    name: "support_ticket",
    displayName: "Support Ticket",
    description: "Customer support requests and issues",
    category: "customer_service",
    fields: [
      { name: "id", type: "string", required: true, description: "Ticket number" },
      { name: "customerId", type: "string", required: true, description: "Requesting customer" },
      { name: "subject", type: "string", required: true, description: "Issue summary" },
      { name: "description", type: "text", required: true, description: "Detailed description" },
      { name: "category", type: "enum", required: true, description: "Issue category" },
      { name: "priority", type: "enum", required: true, description: "Low, medium, high, critical" },
      { name: "status", type: "enum", required: true, description: "Open, in progress, resolved, closed" },
      { name: "assignedTo", type: "string", required: false, description: "Support agent" },
      { name: "createdAt", type: "datetime", required: true, description: "Ticket creation" },
      { name: "resolvedAt", type: "datetime", required: false, description: "Resolution time" },
    ],
    relationships: [
      { target: "customer", type: "belongs_to", description: "Ticket creator" },
      { target: "order", type: "belongs_to", description: "Related order" },
      { target: "ticket_message", type: "has_many", description: "Conversation thread" },
    ],
    businessRules: [
      "SLA response times by priority",
      "Automatic escalation rules",
      "Customer satisfaction survey after closure",
      "Ticket merge for duplicates",
    ],
    edgeCases: [
      "VIP customer handling",
      "Multiple related orders",
      "Language translation needs",
      "Legal/compliance issues",
    ],
    testScenarios: [
      { name: "Order Issue", description: "Problem with order" },
      { name: "Technical Support", description: "Website/app issues" },
      { name: "Escalation", description: "High priority issue" },
    ],
  },

  // Warehouse & Fulfillment
  warehouse: {
    name: "warehouse",
    displayName: "Warehouse",
    description: "Distribution centers and storage facilities",
    category: "fulfillment",
    fields: [
      { name: "id", type: "string", required: true, description: "Warehouse code" },
      { name: "name", type: "string", required: true, description: "Warehouse name" },
      { name: "type", type: "enum", required: true, description: "Distribution, fulfillment, returns" },
      { name: "address", type: "object", required: true, description: "Location address" },
      { name: "capacity", type: "integer", required: true, description: "Storage capacity" },
      { name: "currentUtilization", type: "decimal", required: true, description: "Space usage %" },
      { name: "operatingHours", type: "object", required: true, description: "Business hours" },
      { name: "isActive", type: "boolean", required: true, description: "Operational status" },
    ],
    relationships: [
      { target: "inventory", type: "has_many", description: "Stock in warehouse" },
      { target: "shipment", type: "has_many", description: "Outbound shipments" },
      { target: "transfer", type: "has_many", description: "Stock transfers" },
    ],
    businessRules: [
      "Capacity cannot exceed 100%",
      "Transfer lead times by distance",
      "Safety stock requirements",
      "Regional shipping zones",
    ],
    edgeCases: [
      "Natural disaster closure",
      "Peak season overflow",
      "Cross-dock operations",
      "Temperature-controlled zones",
    ],
    testScenarios: [
      { name: "Main Warehouse", description: "Primary distribution center" },
      { name: "Regional Hub", description: "Local fulfillment center" },
      { name: "Returns Center", description: "Dedicated returns facility" },
    ],
  },

  shipment: {
    name: "shipment",
    displayName: "Shipment",
    description: "Outbound shipment tracking",
    category: "fulfillment",
    fields: [
      { name: "id", type: "string", required: true, description: "Shipment ID" },
      { name: "orderId", type: "string", required: true, description: "Order reference" },
      { name: "warehouseId", type: "string", required: true, description: "Origin warehouse" },
      { name: "carrier", type: "string", required: true, description: "Shipping carrier" },
      { name: "trackingNumber", type: "string", required: true, description: "Tracking code" },
      { name: "status", type: "enum", required: true, description: "Shipment status" },
      { name: "shippedDate", type: "datetime", required: false, description: "Ship date" },
      { name: "deliveryDate", type: "datetime", required: false, description: "Delivery date" },
    ],
    relationships: [
      { target: "order", type: "belongs_to", description: "Shipment for order" },
      { target: "warehouse", type: "belongs_to", description: "Shipped from" },
      { target: "tracking_event", type: "has_many", description: "Tracking updates" },
    ],
    businessRules: [
      "Carrier integration required",
      "Insurance for high-value items",
      "Signature on delivery rules",
      "Customs documentation for international",
    ],
    edgeCases: [
      "Lost in transit",
      "Damaged shipment",
      "Wrong address delivery",
      "Carrier exceptions",
    ],
    testScenarios: [
      { name: "Standard Shipment", description: "Regular delivery" },
      { name: "Express Shipment", description: "Priority delivery" },
      { name: "International", description: "Cross-border shipment" },
    ],
  },
};

export default function EntityDetailsPage() {
  const params = useParams();
  const entityName = params.name as string;
  const entity = entitiesData[entityName] || {
    name: entityName,
    displayName: entityName.charAt(0).toUpperCase() + entityName.slice(1),
    description: `Details for ${entityName} entity`,
    fields: [],
    relationships: [],
    businessRules: [],
    edgeCases: [],
    testScenarios: [],
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b pb-6">
        <Link href="/entities">
          <Button variant="outline" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Entities
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{entity.displayName}</h1>
        <p className="text-gray-600 mt-2">{entity.description}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fields */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="mr-2 h-5 w-5" />
              Fields ({entity.fields.length})
            </CardTitle>
            <CardDescription>Data structure and field definitions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {entity.fields.map((field: any) => (
                <div key={field.name} className="border-l-2 border-gray-200 pl-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-mono text-sm font-medium">{field.name}</span>
                      {field.required && (
                        <span className="ml-2 text-xs text-red-600">required</span>
                      )}
                      <p className="text-xs text-gray-600 mt-1">{field.description}</p>
                    </div>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">{field.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Relationships */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Link2 className="mr-2 h-5 w-5" />
              Relationships ({entity.relationships.length})
            </CardTitle>
            <CardDescription>Connections to other entities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {entity.relationships.map((rel: any) => (
                <div key={rel.target} className="border-l-2 border-blue-200 pl-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">{rel.target}</span>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {rel.type}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{rel.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Business Rules */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="mr-2 h-5 w-5" />
              Business Rules ({entity.businessRules.length})
            </CardTitle>
            <CardDescription>Domain constraints and validations</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {entity.businessRules.map((rule: string, index: number) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{rule}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Edge Cases */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="mr-2 h-5 w-5" />
              Edge Cases ({entity.edgeCases.length})
            </CardTitle>
            <CardDescription>Special scenarios to consider</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {entity.edgeCases.map((edge: string, index: number) => (
                <li key={index} className="flex items-start">
                  <AlertCircle className="mr-2 h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{edge}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Test Scenarios */}
      <Card>
        <CardHeader>
          <CardTitle>Test Scenarios</CardTitle>
          <CardDescription>Common testing scenarios for this entity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {entity.testScenarios.map((scenario: any) => (
              <div key={scenario.name} className="border rounded-lg p-3">
                <h4 className="font-medium text-sm">{scenario.name}</h4>
                <p className="text-xs text-gray-600 mt-1">{scenario.description}</p>
                <Link href={`/generate?entity=${entity.name}&scenario=${scenario.name.toLowerCase().replace(/\s+/g, '_')}`}>
                  <Button size="sm" variant="outline" className="mt-2">
                    Generate Test Data
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <Link href={`/generate?entity=${entity.name}`}>
          <Button size="lg">
            Generate Test Data for {entity.displayName}
          </Button>
        </Link>
      </div>
    </div>
  );
}