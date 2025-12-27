from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntityField:
    """Definition of an entity field."""

    name: str
    type: str
    description: str
    required: bool = True
    validations: list[str] = field(default_factory=list)
    example: str = ""


@dataclass
class EntityRelationship:
    """Relationship between entities."""

    target: str
    type: str  # belongs_to, has_many, has_one, many_to_many
    description: str = ""
    required: bool = False


@dataclass
class EntityDefinition:
    """Complete entity definition."""

    name: str
    description: str
    category: str  # core, transactional, financial, catalog, etc.
    fields: list[EntityField]
    relationships: list[EntityRelationship] = field(default_factory=list)
    business_rules: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)
    test_scenarios: list[str] = field(default_factory=list)


# Entity Definitions
ENTITIES: dict[str, EntityDefinition] = {
    "cart": EntityDefinition(
        name="cart",
        description="Shopping cart containing items before checkout",
        category="transactional",
        fields=[
            EntityField(
                "cart_id", "string", "Unique cart identifier", example="CRT-2025-1234567"
            ),
            EntityField(
                "customer_id", "string", "Customer who owns the cart", example="USR-1234567"
            ),
            EntityField("items", "array", "List of cart items"),
            EntityField("subtotal", "decimal", "Sum of item prices before tax", example="149.99"),
            EntityField("tax", "decimal", "Calculated tax amount", example="12.37"),
            EntityField("total", "decimal", "Final cart total including tax", example="162.36"),
            EntityField("currency", "string", "Currency code", example="USD"),
            EntityField(
                "status", "enum", "Cart status: active, abandoned, converted", example="active"
            ),
            EntityField("created_at", "datetime", "Cart creation timestamp"),
            EntityField("updated_at", "datetime", "Last modification timestamp"),
        ],
        relationships=[
            EntityRelationship(
                "customer", "belongs_to", "Customer who owns this cart", required=True
            ),
            EntityRelationship("cart_item", "has_many", "Items in the cart"),
            EntityRelationship("order", "converts_to", "Order created from this cart"),
        ],
        business_rules=[
            "BR001: Cart must have at least 1 item at checkout",
            "BR002: Cart total must be >= $1.00 for payment",
            "BR003: Item quantity must be 1-99",
        ],
        edge_cases=[
            "Concurrent cart updates from multiple sessions",
            "Cart with out-of-stock items",
            "Cart with expired promotions",
            "Cart exceeding max item limit",
        ],
        test_scenarios=[
            "happy_path",
            "high_value",
            "single_item",
            "max_items",
            "abandoned",
            "multi_currency",
        ],
    ),
    "order": EntityDefinition(
        name="order",
        description="Completed purchase after checkout",
        category="transactional",
        fields=[
            EntityField(
                "order_id", "string", "Unique order identifier", example="ORD-2025-1234567"
            ),
            EntityField("customer_id", "string", "Customer who placed the order"),
            EntityField("cart_id", "string", "Source cart ID"),
            EntityField("items", "array", "Ordered items"),
            EntityField("subtotal", "decimal", "Items total before tax"),
            EntityField("tax", "decimal", "Tax amount"),
            EntityField("shipping", "decimal", "Shipping cost"),
            EntityField("total", "decimal", "Final order total"),
            EntityField(
                "status",
                "enum",
                "Order status: pending, confirmed, shipped, delivered, cancelled",
            ),
            EntityField(
                "payment_status", "enum", "Payment status: pending, paid, failed, refunded"
            ),
            EntityField("shipping_address", "object", "Delivery address"),
            EntityField("billing_address", "object", "Billing address"),
            EntityField("placed_at", "datetime", "Order placement time"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", required=True),
            EntityRelationship("cart", "created_from"),
            EntityRelationship("payment", "has_many"),
            EntityRelationship("shipment", "has_many"),
            EntityRelationship("return", "has_many"),
        ],
        business_rules=[
            "BR004: Order total must match payment amount",
            "BR005: Shipping address required for physical items",
            "BR006: Cannot cancel shipped orders",
        ],
        edge_cases=[
            "Order with partial inventory availability",
            "Order during price change",
            "Split shipment order",
            "Order with mixed digital and physical items",
        ],
        test_scenarios=[
            "happy_path",
            "high_value",
            "express_shipping",
            "international",
            "partial_fulfillment",
            "cancelled",
        ],
    ),
    "payment": EntityDefinition(
        name="payment",
        description="Payment transaction for an order",
        category="financial",
        fields=[
            EntityField("payment_id", "string", "Unique payment identifier"),
            EntityField("order_id", "string", "Associated order"),
            EntityField("amount", "decimal", "Payment amount"),
            EntityField("currency", "string", "Currency code"),
            EntityField("method", "enum", "Payment method: card, paypal, apple_pay, etc."),
            EntityField(
                "status",
                "enum",
                "Status: pending, authorized, captured, failed, refunded",
            ),
            EntityField("gateway_reference", "string", "Payment gateway reference ID"),
            EntityField("card_last_four", "string", "Last 4 digits of card", required=False),
            EntityField("processor_response", "string", "Gateway response code"),
            EntityField("created_at", "datetime", "Payment initiation time"),
            EntityField("completed_at", "datetime", "Payment completion time", required=False),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", required=True),
            EntityRelationship("refund", "has_many"),
        ],
        business_rules=[
            "BR007: Payment amount must match order total",
            "BR008: Card expiry must be future date",
            "BR009: CVV required for card payments",
        ],
        edge_cases=[
            "Payment timeout after authorization",
            "Duplicate payment submission",
            "Payment with expired card",
            "3D Secure authentication failure",
        ],
        test_scenarios=[
            "card_success",
            "card_declined",
            "paypal_success",
            "apple_pay",
            "insufficient_funds",
            "fraud_detected",
        ],
    ),
    "inventory": EntityDefinition(
        name="inventory",
        description="Product inventory tracking stock levels and availability",
        category="catalog",
        fields=[
            EntityField(
                "inventory_id", "string", "Unique inventory record identifier",
                example="INV-2025-8934521"
            ),
            EntityField(
                "product_id", "string", "Associated product identifier",
                example="PRD-8472936"
            ),
            EntityField(
                "sku", "string", "Stock keeping unit",
                example="MEN-SHIRT-BLU-L"
            ),
            EntityField(
                "location_id", "string", "Warehouse or store location",
                example="WH-NYC-01"
            ),
            EntityField(
                "quantity_on_hand", "integer", "Current stock quantity",
                example="150"
            ),
            EntityField(
                "quantity_reserved", "integer", "Reserved for pending orders",
                example="12"
            ),
            EntityField(
                "quantity_available", "integer", "Available for sale",
                example="138"
            ),
            EntityField(
                "reorder_point", "integer", "Minimum stock before reorder",
                example="50"
            ),
            EntityField(
                "reorder_quantity", "integer", "Quantity to reorder",
                example="200"
            ),
            EntityField(
                "unit_cost", "decimal", "Cost per unit",
                example="24.99"
            ),
            EntityField(
                "last_restock_date", "datetime", "Last restocking date",
                example="2024-01-10T09:00:00Z"
            ),
            EntityField(
                "next_restock_date", "datetime", "Expected restock date",
                required=False,
                example="2024-02-01T09:00:00Z"
            ),
            EntityField(
                "status", "string", "Inventory status",
                example="in_stock",
                validations=["enum:in_stock,low_stock,out_of_stock,discontinued"]
            ),
        ],
        relationships=[
            EntityRelationship("product", "belongs_to", "Links to product catalog"),
            EntityRelationship("location", "belongs_to", "Physical location of inventory"),
            EntityRelationship("supplier", "has_one", "Supplier for restocking"),
        ],
        business_rules=[
            "quantity_available = quantity_on_hand - quantity_reserved",
            "Alert when quantity_available < reorder_point",
            "Cannot reserve more than quantity_available",
            "Track inventory movements with audit log",
        ],
        edge_cases=[
            "Negative inventory (oversold)",
            "Multiple warehouse locations",
            "Perishable items with expiration dates",
            "Bundle products affecting multiple SKUs",
            "Inventory reconciliation discrepancies",
        ],
        test_scenarios=[
            "normal_stock",
            "low_stock_alert",
            "out_of_stock",
            "bulk_restock",
            "inventory_transfer",
            "damaged_goods",
        ]
    ),
    "customer": EntityDefinition(
        name="customer",
        description="Customer profile and account information",
        category="core",
        fields=[
            EntityField(
                "customer_id", "string", "Unique customer identifier",
                example="CUST-2025-7834521"
            ),
            EntityField(
                "email", "string", "Customer email address",
                example="sarah.johnson@example.com"
            ),
            EntityField(
                "first_name", "string", "Customer first name",
                example="Sarah"
            ),
            EntityField(
                "last_name", "string", "Customer last name",
                example="Johnson"
            ),
            EntityField(
                "phone", "string", "Phone number",
                example="+1-555-0123"
            ),
            EntityField(
                "date_of_birth", "date", "Date of birth",
                required=False,
                example="1985-03-15"
            ),
            EntityField(
                "gender", "string", "Gender",
                required=False,
                example="female"
            ),
            EntityField(
                "loyalty_tier", "string", "Loyalty program tier",
                example="gold",
                validations=["enum:bronze,silver,gold,platinum,vip"]
            ),
            EntityField(
                "loyalty_points", "integer", "Current loyalty points",
                example="12500"
            ),
            EntityField(
                "lifetime_value", "decimal", "Total lifetime purchase value",
                example="8450.75"
            ),
            EntityField(
                "registration_date", "datetime", "Account creation date",
                example="2020-06-15T14:30:00Z"
            ),
            EntityField(
                "last_login", "datetime", "Last login timestamp",
                example="2024-01-15T09:22:00Z"
            ),
            EntityField(
                "preferred_language", "string", "Language preference",
                example="en-US"
            ),
            EntityField(
                "marketing_consent", "boolean", "Email marketing consent",
                example="true"
            ),
            EntityField(
                "account_status", "string", "Account status",
                example="active",
                validations=["enum:active,suspended,closed,pending_verification"]
            ),
        ],
        relationships=[
            EntityRelationship("order", "has_many", "Customer orders"),
            EntityRelationship("address", "has_many", "Saved addresses"),
            EntityRelationship("payment_method", "has_many", "Saved payment methods"),
            EntityRelationship("wishlist", "has_one", "Customer wishlist"),
        ],
        business_rules=[
            "Email must be unique across customers",
            "Loyalty tier based on lifetime value or points",
            "Cannot delete customer with order history",
            "Age verification for restricted products",
        ],
        edge_cases=[
            "Guest checkout conversion",
            "Duplicate account merge",
            "GDPR data deletion request",
            "Corporate/B2B customers",
            "Minor age restrictions",
        ],
        test_scenarios=[
            "new_customer",
            "vip_customer",
            "inactive_customer",
            "guest_to_registered",
            "loyalty_upgrade",
        ]
    ),
    "shipping": EntityDefinition(
        name="shipping",
        description="Shipping and delivery information for orders",
        category="fulfillment",
        fields=[
            EntityField(
                "shipping_id", "string", "Unique shipping identifier",
                example="SHIP-2025-9834521"
            ),
            EntityField(
                "order_id", "string", "Associated order",
                example="ORD-2025-1234567"
            ),
            EntityField(
                "carrier", "string", "Shipping carrier",
                example="FedEx",
                validations=["enum:FedEx,UPS,USPS,DHL,Local"]
            ),
            EntityField(
                "service_type", "string", "Shipping service level",
                example="express",
                validations=["enum:standard,express,overnight,same_day,economy"]
            ),
            EntityField(
                "tracking_number", "string", "Carrier tracking number",
                example="1Z999AA10123456784"
            ),
            EntityField(
                "shipping_cost", "decimal", "Shipping cost",
                example="12.99"
            ),
            EntityField(
                "weight", "decimal", "Package weight in lbs",
                example="2.5"
            ),
            EntityField(
                "dimensions", "object", "Package dimensions",
                example='{"length": 12, "width": 8, "height": 6}'
            ),
            EntityField(
                "ship_date", "datetime", "Shipment date",
                example="2024-01-15T10:00:00Z"
            ),
            EntityField(
                "estimated_delivery", "datetime", "Estimated delivery date",
                example="2024-01-17T18:00:00Z"
            ),
            EntityField(
                "actual_delivery", "datetime", "Actual delivery date",
                required=False,
                example="2024-01-17T14:30:00Z"
            ),
            EntityField(
                "signature_required", "boolean", "Signature required flag",
                example="false"
            ),
            EntityField(
                "insurance_amount", "decimal", "Insurance coverage",
                required=False,
                example="500.00"
            ),
            EntityField(
                "status", "string", "Shipping status",
                example="in_transit",
                validations=["enum:pending,picked_up,in_transit,out_for_delivery,delivered,returned,lost"]
            ),
            EntityField(
                "delivery_instructions", "string", "Special delivery instructions",
                required=False,
                example="Leave at front door"
            ),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Parent order"),
            EntityRelationship("address", "has_one", "Delivery address"),
            EntityRelationship("tracking_event", "has_many", "Tracking updates"),
        ],
        business_rules=[
            "Tracking number must be unique per carrier",
            "Cannot ship before order is paid",
            "Weight/dimension limits per service type",
            "International shipping requires customs info",
        ],
        edge_cases=[
            "Split shipments for single order",
            "Address correction mid-transit",
            "Failed delivery attempts",
            "International customs delays",
            "Damaged in transit claims",
        ],
        test_scenarios=[
            "standard_delivery",
            "express_shipping",
            "international",
            "multiple_packages",
            "delivery_exception",
            "return_to_sender",
        ]
    ),
    # Additional Shopping Entities
    "cart_item": EntityDefinition(
        name="cart_item",
        description="Individual item in a shopping cart",
        category="transactional",
        fields=[
            EntityField("cart_item_id", "string", "Unique cart item identifier", example="CI-2025-1234567"),
            EntityField("cart_id", "string", "Parent cart ID", example="CRT-2025-1234567"),
            EntityField("product_id", "string", "Product identifier", example="PRD-8472936"),
            EntityField("sku", "string", "Stock keeping unit", example="MEN-SHIRT-BLU-L"),
            EntityField("quantity", "integer", "Item quantity", example="2"),
            EntityField("unit_price", "decimal", "Price per unit", example="49.99"),
        ],
        relationships=[
            EntityRelationship("cart", "belongs_to", "Parent shopping cart", required=True),
            EntityRelationship("product", "belongs_to", "Product in cart"),
        ],
        business_rules=[
            "Quantity must be between 1 and 99",
            "Unit price must match current product price",
        ],
        edge_cases=[
            "Product price changed while in cart",
            "Product becomes unavailable",
            "Quantity exceeds available stock",
        ],
        test_scenarios=["single_item", "multiple_quantity", "max_quantity"],
    ),
    "saved_cart": EntityDefinition(
        name="saved_cart",
        description="Cart saved for later purchase",
        category="transactional",
        fields=[
            EntityField("saved_cart_id", "string", "Unique saved cart identifier", example="SC-2025-1234567"),
            EntityField("customer_id", "string", "Customer who saved the cart", example="CUST-2025-7834521"),
            EntityField("name", "string", "User-defined cart name", example="Holiday Shopping"),
            EntityField("items", "array", "List of saved items"),
            EntityField("created_at", "datetime", "Save date"),
            EntityField("expires_at", "datetime", "Expiration date", required=False),
            EntityField("status", "enum", "Status: active, expired, converted", example="active"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Cart owner", required=True),
        ],
        business_rules=[
            "Saved carts expire after 90 days",
            "Maximum 10 saved carts per customer",
        ],
        edge_cases=[
            "Expired saved cart restoration",
            "Items no longer available",
        ],
        test_scenarios=["save_cart", "restore_cart", "expired_cart"],
    ),
    # Additional Order Entities
    "order_item": EntityDefinition(
        name="order_item",
        description="Individual item within an order",
        category="transactional",
        fields=[
            EntityField("order_item_id", "string", "Unique order item identifier", example="OI-2025-1234567"),
            EntityField("order_id", "string", "Parent order ID", example="ORD-2025-1234567"),
            EntityField("product_id", "string", "Product identifier", example="PRD-8472936"),
            EntityField("sku", "string", "Stock keeping unit", example="MEN-SHIRT-BLU-L"),
            EntityField("quantity", "integer", "Ordered quantity", example="2"),
            EntityField("unit_price", "decimal", "Price per unit at time of order", example="49.99"),
            EntityField("total_price", "decimal", "Line item total", example="99.98"),
            EntityField("status", "enum", "Item status: pending, shipped, delivered, returned", example="shipped"),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Parent order", required=True),
            EntityRelationship("product", "belongs_to", "Ordered product"),
        ],
        business_rules=[
            "Total price = quantity * unit_price",
            "Cannot modify after shipment",
            "Return window is 30 days from delivery",
        ],
        edge_cases=[
            "Partial item return",
            "Item substitution",
            "Backordered item fulfillment",
            "Damaged item replacement",
        ],
        test_scenarios=["single_item", "bulk_order", "partial_shipment", "return_item"],
    ),
    "order_status": EntityDefinition(
        name="order_status",
        description="Status tracking for orders",
        category="transactional",
        fields=[
            EntityField("status_id", "string", "Unique status record identifier", example="OS-2025-1234567"),
            EntityField("order_id", "string", "Associated order", example="ORD-2025-1234567"),
            EntityField("status", "enum", "Order status value", example="shipped"),
            EntityField("timestamp", "datetime", "Status change time"),
            EntityField("notes", "string", "Status notes", required=False),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Associated order", required=True),
        ],
        business_rules=[
            "Status changes must follow valid transitions",
            "Cannot revert to previous status",
        ],
        edge_cases=[
            "Status update during system maintenance",
            "Concurrent status updates",
            "Missing intermediate status",
        ],
        test_scenarios=["status_progression", "status_rollback_attempt"],
    ),
    # Additional Payment Entities
    "refund": EntityDefinition(
        name="refund",
        description="Refund transaction for returned items",
        category="financial",
        fields=[
            EntityField("refund_id", "string", "Unique refund identifier", example="REF-2025-1234567"),
            EntityField("order_id", "string", "Original order ID", example="ORD-2025-1234567"),
            EntityField("payment_id", "string", "Original payment ID", example="PAY-2025-1234567"),
            EntityField("amount", "decimal", "Refund amount", example="49.99"),
            EntityField("reason", "string", "Refund reason", example="Product defective"),
            EntityField("status", "enum", "Status: pending, processed, failed", example="processed"),
            EntityField("processed_at", "datetime", "Processing timestamp", required=False),
            EntityField("gateway_reference", "string", "Payment gateway refund ID"),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Original order", required=True),
            EntityRelationship("payment", "belongs_to", "Original payment"),
        ],
        business_rules=[
            "Refund cannot exceed original payment",
            "Refund must be processed within 5 business days",
            "Partial refunds allowed for partial returns",
        ],
        edge_cases=[
            "Refund to expired card",
            "Multiple partial refunds",
            "Refund after chargeback",
        ],
        test_scenarios=["full_refund", "partial_refund", "refund_declined"],
    ),
    "payment_authorization": EntityDefinition(
        name="payment_authorization",
        description="Authorization for payment processing",
        category="financial",
        fields=[
            EntityField("auth_id", "string", "Authorization identifier", example="AUTH-2025-1234567"),
            EntityField("order_id", "string", "Associated order", example="ORD-2025-1234567"),
            EntityField("amount", "decimal", "Authorized amount", example="162.36"),
            EntityField("status", "enum", "Status: pending, approved, declined, expired", example="approved"),
            EntityField("expires_at", "datetime", "Authorization expiry"),
            EntityField("auth_code", "string", "Bank authorization code"),
            EntityField("created_at", "datetime", "Authorization timestamp"),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Order being authorized", required=True),
        ],
        business_rules=[
            "Authorization expires after 7 days",
            "Cannot capture more than authorized amount",
        ],
        edge_cases=[
            "Authorization expired before capture",
            "Partial capture scenarios",
        ],
        test_scenarios=["authorize_capture", "auth_expired", "partial_capture"],
    ),
    # Additional Inventory Entities
    "stock": EntityDefinition(
        name="stock",
        description="Current stock levels",
        category="catalog",
        fields=[
            EntityField("stock_id", "string", "Stock record identifier", example="STK-2025-1234567"),
            EntityField("sku", "string", "Stock keeping unit", example="MEN-SHIRT-BLU-L"),
            EntityField("location_id", "string", "Warehouse location", example="WH-NYC-01"),
            EntityField("quantity", "integer", "Available quantity", example="150"),
            EntityField("reserved", "integer", "Reserved quantity", example="12"),
            EntityField("last_updated", "datetime", "Last update timestamp"),
        ],
        relationships=[
            EntityRelationship("inventory", "belongs_to", "Parent inventory record"),
        ],
        business_rules=[
            "Quantity cannot be negative",
            "Reserved cannot exceed quantity",
        ],
        edge_cases=[
            "Stock sync discrepancy",
            "Negative stock correction",
            "Multi-warehouse stock transfer",
        ],
        test_scenarios=["check_stock", "reserve_stock", "release_stock"],
    ),
    "stock_alert": EntityDefinition(
        name="stock_alert",
        description="Low stock notifications",
        category="catalog",
        fields=[
            EntityField("alert_id", "string", "Alert identifier", example="SA-2025-1234567"),
            EntityField("sku", "string", "Stock keeping unit", example="MEN-SHIRT-BLU-L"),
            EntityField("threshold", "integer", "Alert threshold", example="10"),
            EntityField("current_level", "integer", "Current stock level", example="5"),
            EntityField("triggered_at", "datetime", "Alert trigger time"),
        ],
        relationships=[
            EntityRelationship("inventory", "belongs_to", "Related inventory"),
        ],
        business_rules=[
            "Alert when stock falls below threshold",
            "One active alert per SKU",
        ],
        edge_cases=[
            "Rapid stock depletion",
            "Alert during restocking",
        ],
        test_scenarios=["trigger_alert", "clear_alert"],
    ),
    # Additional Customer Entities
    "loyalty_member": EntityDefinition(
        name="loyalty_member",
        description="Loyalty program membership",
        category="core",
        fields=[
            EntityField("member_id", "string", "Membership identifier", example="LM-2025-1234567"),
            EntityField("customer_id", "string", "Customer ID", example="CUST-2025-7834521"),
            EntityField("tier", "enum", "Membership tier: bronze, silver, gold, platinum", example="gold"),
            EntityField("points_balance", "integer", "Current points", example="12500"),
            EntityField("points_earned_ytd", "integer", "Points earned this year", example="5000"),
            EntityField("tier_expiry", "date", "Tier expiration date"),
            EntityField("enrolled_at", "datetime", "Enrollment date"),
            EntityField("status", "enum", "Status: active, suspended, expired", example="active"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Member customer", required=True),
            EntityRelationship("loyalty_transaction", "has_many", "Points transactions"),
        ],
        business_rules=[
            "Tier upgrade based on points threshold",
            "Points expire after 12 months of inactivity",
            "Minimum 100 points for redemption",
        ],
        edge_cases=[
            "Tier downgrade at renewal",
            "Points expiration notice",
            "Merged account points consolidation",
        ],
        test_scenarios=["earn_points", "redeem_points", "tier_upgrade"],
    ),
    "customer_preferences": EntityDefinition(
        name="customer_preferences",
        description="Customer shopping preferences",
        category="core",
        fields=[
            EntityField("preference_id", "string", "Preference record ID", example="CP-2025-1234567"),
            EntityField("customer_id", "string", "Customer ID", example="CUST-2025-7834521"),
            EntityField("preferred_categories", "array", "Preferred product categories"),
            EntityField("communication_channels", "array", "Preferred contact methods"),
            EntityField("language", "string", "Language preference", example="en-US"),
            EntityField("currency", "string", "Currency preference", example="USD"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Associated customer", required=True),
        ],
        business_rules=[
            "At least one communication channel required",
            "Preferences sync across devices",
        ],
        edge_cases=[
            "Conflicting preferences on merge",
            "Legacy preference migration",
        ],
        test_scenarios=["set_preferences", "update_preferences"],
    ),
    # Additional Shipping Entities
    "shipment": EntityDefinition(
        name="shipment",
        description="Individual shipment tracking",
        category="fulfillment",
        fields=[
            EntityField("shipment_id", "string", "Shipment identifier", example="SHP-2025-1234567"),
            EntityField("order_id", "string", "Parent order ID", example="ORD-2025-1234567"),
            EntityField("package_count", "integer", "Number of packages", example="2"),
            EntityField("carrier", "string", "Shipping carrier", example="FedEx"),
            EntityField("tracking_number", "string", "Tracking number", example="1Z999AA10123456784"),
            EntityField("ship_date", "datetime", "Ship date"),
            EntityField("delivery_date", "datetime", "Delivery date", required=False),
            EntityField("status", "enum", "Status: preparing, shipped, in_transit, delivered", example="in_transit"),
            EntityField("items", "array", "Items in shipment"),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Parent order", required=True),
            EntityRelationship("tracking", "has_many", "Tracking events"),
        ],
        business_rules=[
            "Each package must have tracking",
            "Cannot ship cancelled items",
            "Signature required for high-value items",
        ],
        edge_cases=[
            "Lost package claim",
            "Delivery to wrong address",
            "Package refused by recipient",
        ],
        test_scenarios=["single_shipment", "split_shipment", "return_shipment"],
    ),
    "tracking": EntityDefinition(
        name="tracking",
        description="Package tracking information",
        category="fulfillment",
        fields=[
            EntityField("tracking_id", "string", "Tracking event ID", example="TRK-2025-1234567"),
            EntityField("shipment_id", "string", "Parent shipment", example="SHP-2025-1234567"),
            EntityField("tracking_number", "string", "Carrier tracking number"),
            EntityField("status", "string", "Tracking status", example="In Transit"),
            EntityField("location", "string", "Current location", example="Chicago, IL"),
            EntityField("timestamp", "datetime", "Event timestamp"),
            EntityField("description", "string", "Event description"),
        ],
        relationships=[
            EntityRelationship("shipment", "belongs_to", "Parent shipment", required=True),
        ],
        business_rules=[
            "Events must be chronologically ordered",
            "Location required for transit events",
        ],
        edge_cases=[
            "Out of sequence tracking updates",
            "Carrier system delays",
            "International tracking handoff",
        ],
        test_scenarios=["track_package", "delivery_exception"],
    ),
    # Promotion Entities
    "discount": EntityDefinition(
        name="discount",
        description="Discount rules and applications",
        category="promotions",
        fields=[
            EntityField("discount_id", "string", "Discount identifier", example="DSC-2025-1234567"),
            EntityField("name", "string", "Discount name", example="Summer Sale 20%"),
            EntityField("type", "enum", "Type: percentage, fixed, bogo", example="percentage"),
            EntityField("value", "decimal", "Discount value", example="20"),
            EntityField("min_purchase", "decimal", "Minimum purchase amount", example="50.00"),
            EntityField("max_discount", "decimal", "Maximum discount cap", required=False),
            EntityField("start_date", "datetime", "Start date"),
            EntityField("end_date", "datetime", "End date"),
        ],
        relationships=[
            EntityRelationship("product", "applies_to", "Applicable products"),
            EntityRelationship("category", "applies_to", "Applicable categories"),
        ],
        business_rules=[
            "Cannot combine with other discounts unless specified",
            "Discount cannot exceed item price",
            "Min purchase required before discount applies",
            "End date must be after start date",
        ],
        edge_cases=[
            "Discount applied to sale items",
            "Stacking multiple discounts",
            "Discount on final item in cart",
            "Price change during discount period",
            "Cart value drops below minimum",
        ],
        test_scenarios=["apply_percentage", "apply_fixed", "bogo_discount", "expired_discount"],
    ),
    "coupon": EntityDefinition(
        name="coupon",
        description="Coupon codes for discounts",
        category="promotions",
        fields=[
            EntityField("coupon_id", "string", "Coupon identifier", example="CPN-2025-1234567"),
            EntityField("code", "string", "Coupon code", example="SAVE20"),
            EntityField("discount_id", "string", "Associated discount", example="DSC-2025-1234567"),
            EntityField("usage_limit", "integer", "Maximum total uses", example="1000"),
            EntityField("usage_count", "integer", "Current usage count", example="450"),
            EntityField("per_customer_limit", "integer", "Uses per customer", example="1"),
            EntityField("valid_from", "datetime", "Valid from date"),
            EntityField("valid_until", "datetime", "Valid until date"),
        ],
        relationships=[
            EntityRelationship("discount", "belongs_to", "Associated discount rule", required=True),
        ],
        business_rules=[
            "Coupon code must be unique",
            "Cannot exceed usage limits",
            "Single use per customer by default",
        ],
        edge_cases=[
            "Coupon race condition at limit",
            "Expired coupon in cart",
            "Coupon on already discounted item",
            "Customer coupon limit reached",
        ],
        test_scenarios=["apply_coupon", "invalid_coupon", "expired_coupon", "limit_reached"],
    ),
    "promotion": EntityDefinition(
        name="promotion",
        description="Promotional campaigns",
        category="promotions",
        fields=[
            EntityField("promotion_id", "string", "Promotion identifier", example="PRM-2025-1234567"),
            EntityField("name", "string", "Promotion name", example="Black Friday Sale"),
            EntityField("description", "string", "Promotion description"),
            EntityField("type", "enum", "Type: sale, bundle, flash, loyalty", example="sale"),
            EntityField("start_date", "datetime", "Campaign start"),
            EntityField("end_date", "datetime", "Campaign end"),
            EntityField("priority", "integer", "Priority for stacking", example="1"),
            EntityField("rules", "object", "Promotion rules"),
            EntityField("status", "enum", "Status: draft, active, paused, ended", example="active"),
        ],
        relationships=[
            EntityRelationship("discount", "has_many", "Associated discounts"),
            EntityRelationship("coupon", "has_many", "Associated coupons"),
        ],
        business_rules=[
            "Only one flash sale active at a time",
            "Priority determines application order",
            "Cannot modify active promotion",
        ],
        edge_cases=[
            "Overlapping promotions",
            "Promotion start at midnight across timezones",
            "System load during flash sale",
            "Early promotion termination",
        ],
        test_scenarios=["create_promotion", "activate_promotion", "flash_sale"],
    ),
    # Review Entities
    "review": EntityDefinition(
        name="review",
        description="Product reviews from customers",
        category="reviews",
        fields=[
            EntityField("review_id", "string", "Review identifier", example="REV-2025-1234567"),
            EntityField("product_id", "string", "Reviewed product", example="PRD-8472936"),
            EntityField("customer_id", "string", "Reviewer", example="CUST-2025-7834521"),
            EntityField("order_id", "string", "Purchase order", example="ORD-2025-1234567"),
            EntityField("rating", "integer", "Star rating 1-5", example="4"),
            EntityField("title", "string", "Review title", example="Great product!"),
            EntityField("content", "string", "Review text"),
            EntityField("verified_purchase", "boolean", "Verified buyer", example="true"),
        ],
        relationships=[
            EntityRelationship("product", "belongs_to", "Reviewed product", required=True),
            EntityRelationship("customer", "belongs_to", "Reviewer", required=True),
        ],
        business_rules=[
            "One review per product per customer",
            "Must have purchased to leave verified review",
            "Review must be approved before display",
        ],
        edge_cases=[
            "Review for returned item",
            "Inappropriate content flagging",
            "Review for discontinued product",
        ],
        test_scenarios=["submit_review", "edit_review", "flag_review"],
    ),
    "rating": EntityDefinition(
        name="rating",
        description="Product rating scores",
        category="reviews",
        fields=[
            EntityField("rating_id", "string", "Rating identifier", example="RAT-2025-1234567"),
            EntityField("product_id", "string", "Rated product", example="PRD-8472936"),
            EntityField("average_rating", "decimal", "Average rating", example="4.2"),
            EntityField("total_reviews", "integer", "Total review count", example="156"),
            EntityField("rating_distribution", "object", "Distribution by stars"),
        ],
        relationships=[
            EntityRelationship("product", "belongs_to", "Associated product", required=True),
            EntityRelationship("review", "aggregates", "Source reviews"),
        ],
        business_rules=[
            "Rating recalculated on new review",
            "Minimum 5 reviews for display",
        ],
        edge_cases=[
            "First review for product",
            "Rating after review deletion",
        ],
        test_scenarios=["calculate_rating", "update_rating"],
    ),
    # Wishlist Entities
    "wishlist": EntityDefinition(
        name="wishlist",
        description="Customer's saved items for later",
        category="wishlist",
        fields=[
            EntityField("wishlist_id", "string", "Wishlist identifier", example="WL-2025-1234567"),
            EntityField("customer_id", "string", "Wishlist owner", example="CUST-2025-7834521"),
            EntityField("name", "string", "Wishlist name", example="Holiday Gifts"),
            EntityField("items", "array", "Wishlist items"),
            EntityField("is_public", "boolean", "Public visibility", example="false"),
            EntityField("created_at", "datetime", "Creation date"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Wishlist owner", required=True),
            EntityRelationship("product", "has_many", "Saved products"),
        ],
        business_rules=[
            "Maximum 5 wishlists per customer",
            "Maximum 100 items per wishlist",
        ],
        edge_cases=[
            "Item discontinued while on wishlist",
            "Price drop notification",
            "Sharing private wishlist",
        ],
        test_scenarios=["add_to_wishlist", "share_wishlist", "move_to_cart"],
    ),
    "favorites": EntityDefinition(
        name="favorites",
        description="Customer's favorite products",
        category="wishlist",
        fields=[
            EntityField("favorite_id", "string", "Favorite identifier", example="FAV-2025-1234567"),
            EntityField("customer_id", "string", "Customer ID", example="CUST-2025-7834521"),
            EntityField("product_id", "string", "Favorited product", example="PRD-8472936"),
            EntityField("added_at", "datetime", "Date added"),
            EntityField("notes", "string", "Personal notes", required=False),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Customer", required=True),
            EntityRelationship("product", "belongs_to", "Product", required=True),
        ],
        business_rules=[
            "No duplicate favorites per customer",
            "Maximum 500 favorites",
        ],
        edge_cases=[
            "Favoriting unavailable product",
            "Product variant changes",
        ],
        test_scenarios=["add_favorite", "remove_favorite"],
    ),
    # Return Entities
    "return": EntityDefinition(
        name="return",
        description="Product return request",
        category="returns",
        fields=[
            EntityField("return_id", "string", "Return identifier", example="RET-2025-1234567"),
            EntityField("order_id", "string", "Original order", example="ORD-2025-1234567"),
            EntityField("customer_id", "string", "Customer ID", example="CUST-2025-7834521"),
            EntityField("items", "array", "Items being returned"),
            EntityField("reason", "enum", "Return reason", example="defective"),
            EntityField("status", "enum", "Status: requested, approved, received, refunded", example="approved"),
            EntityField("return_label", "string", "Return shipping label", required=False),
            EntityField("refund_amount", "decimal", "Refund amount", example="49.99"),
            EntityField("created_at", "datetime", "Request date"),
            EntityField("processed_at", "datetime", "Processing date", required=False),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Original order", required=True),
            EntityRelationship("refund", "has_one", "Associated refund"),
        ],
        business_rules=[
            "Return within 30 days of delivery",
            "Some items are final sale",
            "Return shipping paid by customer unless defective",
            "Refund processed within 5 days of receipt",
        ],
        edge_cases=[
            "Return window expired",
            "Missing return items",
            "Damaged return claim",
            "Return of gift item",
            "Partial return processing",
        ],
        test_scenarios=["request_return", "process_return", "reject_return", "partial_return"],
    ),
    "exchange": EntityDefinition(
        name="exchange",
        description="Product exchange request",
        category="returns",
        fields=[
            EntityField("exchange_id", "string", "Exchange identifier", example="EXC-2025-1234567"),
            EntityField("return_id", "string", "Associated return", example="RET-2025-1234567"),
            EntityField("original_item", "object", "Original item details"),
            EntityField("new_item", "object", "Replacement item details"),
            EntityField("price_difference", "decimal", "Price difference", example="10.00"),
            EntityField("status", "enum", "Status: pending, approved, shipped, completed", example="approved"),
            EntityField("created_at", "datetime", "Request date"),
            EntityField("completed_at", "datetime", "Completion date", required=False),
        ],
        relationships=[
            EntityRelationship("return", "belongs_to", "Associated return", required=True),
            EntityRelationship("order", "belongs_to", "Original order"),
        ],
        business_rules=[
            "Exchange item must be available",
            "Price difference charged or refunded",
            "Same category exchanges only",
        ],
        edge_cases=[
            "Replacement item out of stock",
            "Price increased since purchase",
            "Exchange during promotion",
            "Multiple exchange requests",
        ],
        test_scenarios=["even_exchange", "exchange_with_upcharge", "exchange_with_refund"],
    ),
    # Analytics Entity
    "analytics_event": EntityDefinition(
        name="analytics_event",
        description="User behavior tracking events",
        category="analytics",
        fields=[
            EntityField("event_id", "string", "Event identifier", example="EVT-2025-1234567"),
            EntityField("event_type", "string", "Event type", example="product_view"),
            EntityField("customer_id", "string", "Customer ID", required=False),
            EntityField("session_id", "string", "Session identifier"),
            EntityField("product_id", "string", "Related product", required=False),
            EntityField("metadata", "object", "Event metadata"),
            EntityField("timestamp", "datetime", "Event timestamp"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Associated customer"),
            EntityRelationship("product", "belongs_to", "Related product"),
        ],
        business_rules=[
            "Events anonymized after 90 days",
            "Session expires after 30 minutes inactivity",
        ],
        edge_cases=[
            "Anonymous user tracking",
            "Cross-device session linking",
            "Bot traffic filtering",
        ],
        test_scenarios=["track_pageview", "track_purchase", "track_search"],
    ),
    # Communication Entity
    "notification": EntityDefinition(
        name="notification",
        description="Customer notifications",
        category="communications",
        fields=[
            EntityField("notification_id", "string", "Notification identifier", example="NOT-2025-1234567"),
            EntityField("customer_id", "string", "Recipient", example="CUST-2025-7834521"),
            EntityField("type", "enum", "Type: order, shipping, promotion, alert", example="shipping"),
            EntityField("channel", "enum", "Channel: email, sms, push", example="email"),
            EntityField("subject", "string", "Notification subject"),
            EntityField("content", "string", "Notification content"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Recipient customer", required=True),
        ],
        business_rules=[
            "Respect customer communication preferences",
            "Rate limit per channel per customer",
        ],
        edge_cases=[
            "Undeliverable email",
            "SMS to invalid number",
            "Notification during quiet hours",
        ],
        test_scenarios=["send_order_notification", "send_promo_notification"],
    ),
    # Subscription Entity
    "subscription": EntityDefinition(
        name="subscription",
        description="Recurring subscription service",
        category="subscriptions",
        fields=[
            EntityField("subscription_id", "string", "Subscription identifier", example="SUB-2025-1234567"),
            EntityField("customer_id", "string", "Subscriber", example="CUST-2025-7834521"),
            EntityField("product_id", "string", "Subscribed product", example="PRD-8472936"),
            EntityField("frequency", "enum", "Delivery frequency: weekly, monthly, quarterly", example="monthly"),
            EntityField("quantity", "integer", "Quantity per delivery", example="1"),
            EntityField("price", "decimal", "Subscription price", example="29.99"),
            EntityField("next_delivery", "date", "Next delivery date"),
            EntityField("status", "enum", "Status: active, paused, cancelled", example="active"),
            EntityField("started_at", "datetime", "Start date"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Subscriber", required=True),
            EntityRelationship("product", "belongs_to", "Subscribed product", required=True),
            EntityRelationship("order", "has_many", "Subscription orders"),
        ],
        business_rules=[
            "Payment method required for subscription",
            "3 failed payments triggers suspension",
            "30 day notice for price changes",
        ],
        edge_cases=[
            "Payment failure on renewal",
            "Product discontinued mid-subscription",
            "Subscription product out of stock",
            "Price change notification",
        ],
        test_scenarios=["create_subscription", "pause_subscription", "cancel_subscription"],
    ),
    # Gift Card Entity
    "gift_card": EntityDefinition(
        name="gift_card",
        description="Gift card purchase and redemption",
        category="gift_cards",
        fields=[
            EntityField("gift_card_id", "string", "Gift card identifier", example="GC-2025-1234567"),
            EntityField("code", "string", "Gift card code", example="GIFT-ABCD-1234-EFGH"),
            EntityField("initial_value", "decimal", "Original value", example="100.00"),
            EntityField("current_balance", "decimal", "Current balance", example="75.50"),
            EntityField("currency", "string", "Currency", example="USD"),
            EntityField("purchaser_id", "string", "Purchaser customer ID", required=False),
            EntityField("recipient_email", "string", "Recipient email", required=False),
            EntityField("expires_at", "date", "Expiration date", required=False),
        ],
        relationships=[
            EntityRelationship("order", "purchased_in", "Purchase order"),
            EntityRelationship("transaction", "has_many", "Usage transactions"),
        ],
        business_rules=[
            "Gift card codes must be unique",
            "Cannot reload physical gift cards",
            "Minimum purchase amount $10",
        ],
        edge_cases=[
            "Partial redemption",
            "Gift card fraud attempt",
            "Expired gift card reactivation",
            "Lost gift card replacement",
        ],
        test_scenarios=["purchase_gift_card", "redeem_gift_card", "check_balance"],
    ),
    # Search Entity
    "search_query": EntityDefinition(
        name="search_query",
        description="Customer search queries",
        category="search",
        fields=[
            EntityField("query_id", "string", "Query identifier", example="SQ-2025-1234567"),
            EntityField("query_text", "string", "Search query", example="blue running shoes"),
            EntityField("customer_id", "string", "Searcher", required=False),
            EntityField("results_count", "integer", "Number of results", example="42"),
            EntityField("clicked_products", "array", "Products clicked from results"),
            EntityField("timestamp", "datetime", "Search timestamp"),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Searcher"),
            EntityRelationship("product", "has_many", "Clicked products"),
        ],
        business_rules=[
            "Log all searches for analytics",
            "Personalize results for logged in users",
        ],
        edge_cases=[
            "Zero results search",
            "Misspelled query handling",
            "Search injection attempt",
        ],
        test_scenarios=["successful_search", "no_results", "filtered_search"],
    ),
    # Security Entity
    "fraud_check": EntityDefinition(
        name="fraud_check",
        description="Fraud detection and prevention",
        category="security",
        fields=[
            EntityField("check_id", "string", "Check identifier", example="FC-2025-1234567"),
            EntityField("order_id", "string", "Order being checked", example="ORD-2025-1234567"),
            EntityField("risk_score", "decimal", "Risk score 0-100", example="15.5"),
            EntityField("signals", "array", "Risk signals detected"),
            EntityField("decision", "enum", "Decision: approve, review, decline", example="approve"),
            EntityField("reviewed_by", "string", "Manual reviewer ID", required=False),
            EntityField("timestamp", "datetime", "Check timestamp"),
            EntityField("notes", "string", "Review notes", required=False),
        ],
        relationships=[
            EntityRelationship("order", "belongs_to", "Checked order", required=True),
            EntityRelationship("customer", "belongs_to", "Customer"),
        ],
        business_rules=[
            "Orders above $500 require additional verification",
            "New customers have elevated scrutiny",
            "Declined orders require manual review appeal",
            "IP geolocation must match billing country",
        ],
        edge_cases=[
            "False positive blocking legitimate order",
            "Sophisticated fraud pattern",
            "Account takeover detection",
            "Gift card fraud rings",
            "Friendly fraud (chargeback abuse)",
        ],
        test_scenarios=["low_risk_order", "high_risk_order", "manual_review"],
    ),
    # Support Entity
    "support_ticket": EntityDefinition(
        name="support_ticket",
        description="Customer support requests",
        category="support",
        fields=[
            EntityField("ticket_id", "string", "Ticket identifier", example="TKT-2025-1234567"),
            EntityField("customer_id", "string", "Customer", example="CUST-2025-7834521"),
            EntityField("order_id", "string", "Related order", required=False),
            EntityField("category", "enum", "Category: order, shipping, product, account, other", example="shipping"),
            EntityField("subject", "string", "Ticket subject", example="Package not delivered"),
            EntityField("description", "string", "Issue description"),
            EntityField("priority", "enum", "Priority: low, medium, high, urgent", example="high"),
            EntityField("status", "enum", "Status: open, in_progress, resolved, closed", example="open"),
            EntityField("assigned_to", "string", "Assigned agent", required=False),
        ],
        relationships=[
            EntityRelationship("customer", "belongs_to", "Ticket creator", required=True),
            EntityRelationship("order", "relates_to", "Related order"),
        ],
        business_rules=[
            "Urgent tickets must be responded within 1 hour",
            "Auto-escalate unresponsed tickets after 24 hours",
            "Customer satisfaction survey after resolution",
        ],
        edge_cases=[
            "Duplicate ticket submission",
            "Escalation to supervisor",
            "Ticket reopened after resolution",
            "Multi-order issue",
        ],
        test_scenarios=["create_ticket", "assign_ticket", "resolve_ticket"],
    ),
}


def get_entity(name: str) -> EntityDefinition | None:
    """Get entity definition by name."""
    return ENTITIES.get(name.lower())


def list_entities(category: str | None = None) -> list[EntityDefinition]:
    """List all entities, optionally filtered by category."""
    entities = list(ENTITIES.values())
    if category:
        entities = [e for e in entities if e.category == category]
    return entities


def get_entity_categories() -> list[str]:
    """Get all unique entity categories."""
    return list(set(e.category for e in ENTITIES.values()))