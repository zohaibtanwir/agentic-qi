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