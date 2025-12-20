from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class BusinessRule:
    """A business rule definition."""

    id: str
    name: str
    entity: str
    description: str
    condition: str  # When this rule applies
    constraint: str  # What the rule enforces
    severity: Severity
    validation_logic: str = ""  # Pseudo-code or description of validation


BUSINESS_RULES: list[BusinessRule] = [
    # Cart Rules
    BusinessRule(
        id="BR001",
        name="cart_item_quantity_limit",
        entity="cart_item",
        description="Limit quantity per item in cart",
        condition="Always",
        constraint="Quantity per item must be between 1 and 99",
        severity=Severity.ERROR,
        validation_logic="1 <= item.quantity <= 99",
    ),
    BusinessRule(
        id="BR002",
        name="cart_total_minimum",
        entity="cart",
        description="Minimum cart total for checkout",
        condition="At checkout",
        constraint="Cart total must be >= $1.00 for payment processing",
        severity=Severity.ERROR,
        validation_logic="cart.total >= 1.00",
    ),
    BusinessRule(
        id="BR003",
        name="cart_item_limit",
        entity="cart",
        description="Maximum items in cart",
        condition="When adding items",
        constraint="Cart cannot exceed 100 unique items",
        severity=Severity.ERROR,
        validation_logic="len(cart.items) <= 100",
    ),
    # Order Rules
    BusinessRule(
        id="BR004",
        name="payment_amount_match",
        entity="payment",
        description="Payment amount must match order",
        condition="At payment creation",
        constraint="Payment amount must match order total exactly",
        severity=Severity.ERROR,
        validation_logic="payment.amount == order.total",
    ),
    BusinessRule(
        id="BR005",
        name="shipping_address_required",
        entity="order",
        description="Shipping address required for physical items",
        condition="At order creation",
        constraint="Orders with physical items must have shipping address",
        severity=Severity.ERROR,
        validation_logic="has_physical_items implies shipping_address is not None",
    ),
    BusinessRule(
        id="BR006",
        name="cancel_before_ship",
        entity="order",
        description="Cannot cancel shipped orders",
        condition="At cancellation request",
        constraint="Order can only be cancelled before shipping",
        severity=Severity.ERROR,
        validation_logic="order.status not in ['shipped', 'delivered']",
    ),
    # Payment Rules
    BusinessRule(
        id="BR007",
        name="card_expiry_future",
        entity="payment",
        description="Card must not be expired",
        condition="At payment with card",
        constraint="Card expiry must be in the future",
        severity=Severity.ERROR,
        validation_logic="card.expiry_date > current_date",
    ),
    BusinessRule(
        id="BR008",
        name="cvv_required",
        entity="payment",
        description="CVV required for card payments",
        condition="At payment with card",
        constraint="CVV must be provided for card payments",
        severity=Severity.ERROR,
        validation_logic="payment.method == 'card' implies cvv is not None",
    ),
    # Return Rules
    BusinessRule(
        id="BR009",
        name="return_window",
        entity="return",
        description="Return window enforcement",
        condition="At return request",
        constraint="Return must be within 30 days of delivery",
        severity=Severity.ERROR,
        validation_logic="(current_date - delivery_date).days <= 30",
    ),
    BusinessRule(
        id="BR010",
        name="refund_amount_limit",
        entity="return",
        description="Refund cannot exceed order total",
        condition="At refund processing",
        constraint="Refund amount must not exceed original order total",
        severity=Severity.ERROR,
        validation_logic="refund.amount <= order.total",
    ),
]


def get_business_rule(rule_id: str) -> BusinessRule | None:
    """Get business rule by ID."""
    for rule in BUSINESS_RULES:
        if rule.id == rule_id:
            return rule
    return None


def get_rules_for_entity(entity: str) -> list[BusinessRule]:
    """Get all business rules for a specific entity."""
    return [rule for rule in BUSINESS_RULES if rule.entity == entity]


def get_rules_by_severity(severity: Severity) -> list[BusinessRule]:
    """Get all business rules with a specific severity."""
    return [rule for rule in BUSINESS_RULES if rule.severity == severity]