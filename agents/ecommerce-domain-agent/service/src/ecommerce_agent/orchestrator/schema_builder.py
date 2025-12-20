"""Schema builder for custom test data generation."""

from typing import Any, Dict, List, Optional
from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

# Test Data Agent's predefined entities
# These can be called directly without providing a schema
TEST_DATA_AGENT_PREDEFINED = {
    # Personal data
    "user", "person", "customer_profile",
    # Contact information
    "email", "phone", "address",
    # Payment methods
    "credit_card", "bank_account", "payment_method",
    # Business entities
    "company", "merchant", "vendor",
    # Products
    "product", "sku", "item",
    # Geographic
    "location", "store", "warehouse",
    # Temporal
    "date", "timestamp", "schedule",
    # Financial
    "transaction", "invoice", "receipt"
}

# Our domain-specific entities that need custom schemas
DOMAIN_ENTITIES = {
    # Shopping & Cart
    "cart", "shopping_cart", "cart_item", "saved_cart",
    # Orders
    "order", "order_item", "order_status", "order_history",
    # Payments
    "payment", "payment_transaction", "refund", "payment_authorization",
    # Inventory
    "inventory", "stock", "inventory_adjustment", "stock_alert",
    # Customer
    "customer", "customer_segment", "loyalty_member", "customer_preferences",
    # Shipping & Fulfillment
    "shipping", "shipment", "tracking", "delivery", "fulfillment",
    # Promotions & Discounts
    "discount", "coupon", "promotion", "price_adjustment", "deal",
    # Product Management
    "category", "brand", "product_variant", "product_bundle",
    # Reviews & Ratings
    "review", "rating", "product_feedback", "merchant_review",
    # Wishlist & Favorites
    "wishlist", "favorites", "save_for_later", "gift_registry",
    # Returns & Exchanges
    "return", "exchange", "rma", "return_label",
    # Analytics & Events
    "analytics_event", "page_view", "click_event", "conversion",
    # Communication
    "notification", "email_campaign", "sms_alert", "push_notification",
    # Subscription
    "subscription", "recurring_order", "subscription_plan",
    # Gift Cards & Store Credit
    "gift_card", "store_credit", "reward_points", "voucher",
    # Search & Recommendations
    "search_query", "recommendation", "personalization", "trending_item",
    # Fraud & Security
    "fraud_check", "security_event", "risk_assessment", "blocked_transaction",
    # Support
    "support_ticket", "chat_session", "complaint", "inquiry"
}


class SchemaBuilder:
    """Builds custom schemas for Test Data Agent from domain entities."""

    def build_schema_from_entity(self, entity_name: str) -> Dict[str, Any]:
        """
        Build a custom schema from a domain entity.

        Args:
            entity_name: Name of the domain entity

        Returns:
            Schema compatible with Test Data Agent's custom schema format
        """
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found in domain")

        # Build schema in Test Data Agent format
        schema = {
            "name": entity.name,
            "description": entity.description,
            "fields": []
        }

        # Convert domain fields to schema fields
        for field in entity.fields:
            schema_field = {
                "name": field.name,
                "type": self._map_field_type(field.type),
                "required": field.required,
                "description": field.description,
            }

            # Add constraints from validations
            if field.validations:
                constraints = {}
                for validation in field.validations:
                    if "min" in validation.lower():
                        constraints["min"] = self._extract_number(validation)
                    elif "max" in validation.lower():
                        constraints["max"] = self._extract_number(validation)
                    elif "enum" in validation.lower():
                        constraints["enum"] = self._extract_enum_values(validation)
                    elif "pattern" in validation.lower():
                        constraints["pattern"] = self._extract_pattern(validation)

                if constraints:
                    schema_field["constraints"] = constraints

            # Add example if available
            if field.example:
                schema_field["example"] = field.example

            schema["fields"].append(schema_field)

        # Add relationships as reference fields
        for relationship in entity.relationships:
            schema["fields"].append({
                "name": f"{relationship.target}_id",
                "type": "string",
                "required": relationship.required,
                "description": f"Reference to {relationship.target}",
                "format": "uuid"
            })

        # Add metadata for Test Data Agent
        schema["metadata"] = {
            "domain": "ecommerce",
            "category": entity.category,
            "business_rules": [rule for rule in entity.business_rules],
            "test_scenarios": entity.test_scenarios
        }

        logger.info(
            "Built custom schema",
            entity=entity_name,
            field_count=len(schema["fields"])
        )

        return schema

    def _map_field_type(self, domain_type: str) -> str:
        """Map domain field type to Test Data Agent type."""
        type_mapping = {
            "string": "string",
            "integer": "integer",
            "decimal": "number",
            "boolean": "boolean",
            "datetime": "datetime",
            "date": "date",
            "enum": "string",
            "array": "array",
            "json": "object",
            "object": "object"  # Support object type directly
        }
        return type_mapping.get(domain_type, "string")

    def _extract_number(self, validation: str) -> float:
        """Extract numeric value from validation string."""
        import re
        match = re.search(r'\d+\.?\d*', validation)
        return float(match.group()) if match else 0

    def _extract_enum_values(self, validation: str) -> List[str]:
        """Extract enum values from validation string."""
        # Example: "enum: pending, active, completed"
        if ":" in validation:
            values_part = validation.split(":")[-1]
            return [v.strip() for v in values_part.split(",")]
        return []

    def _extract_pattern(self, validation: str) -> str:
        """Extract regex pattern from validation string."""
        # Example: "pattern: ^[A-Z]{2}\d{6}$"
        if ":" in validation:
            return validation.split(":")[-1].strip()
        return ".*"

    def determine_generation_strategy(
        self,
        entity_name: str
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Determine whether to use predefined or custom schema.

        Args:
            entity_name: Name of the entity to generate

        Returns:
            Tuple of (strategy, schema) where:
            - strategy is "predefined" or "custom"
            - schema is None for predefined, or the custom schema dict
        """
        # Check if it's a Test Data Agent predefined entity
        if entity_name.lower() in TEST_DATA_AGENT_PREDEFINED:
            logger.info(
                "Using predefined entity",
                entity=entity_name
            )
            return ("predefined", None)

        # Check if it's a domain entity we know about
        if entity_name.lower() in DOMAIN_ENTITIES:
            logger.info(
                "Building custom schema for domain entity",
                entity=entity_name
            )
            schema = self.build_schema_from_entity(entity_name)
            return ("custom", schema)

        # Unknown entity - try to build custom schema anyway
        logger.warning(
            "Unknown entity, attempting custom schema",
            entity=entity_name
        )
        try:
            schema = self.build_schema_from_entity(entity_name)
            return ("custom", schema)
        except ValueError:
            # Entity not found in domain
            logger.error(
                "Entity not found in domain",
                entity=entity_name
            )
            raise ValueError(
                f"Entity '{entity_name}' is not a predefined Test Data Agent "
                f"entity and not found in domain model"
            )


def get_schema_builder() -> SchemaBuilder:
    """Get a schema builder instance."""
    return SchemaBuilder()