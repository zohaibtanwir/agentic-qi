from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    order: int
    name: str
    description: str
    entity: str
    action: str  # create, update, validate, delete, notify
    validations: list[str] = field(default_factory=list)
    possible_outcomes: list[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""

    name: str
    description: str
    steps: list[WorkflowStep]
    involved_entities: list[str]
    business_rules: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)
    test_scenarios: list[str] = field(default_factory=list)


WORKFLOWS: dict[str, WorkflowDefinition] = {
    "checkout": WorkflowDefinition(
        name="checkout",
        description="Complete purchase flow from cart to order confirmation",
        steps=[
            WorkflowStep(
                order=1,
                name="cart_validation",
                description="Validate cart contents and availability",
                entity="cart",
                action="validate",
                validations=["items_exist", "items_in_stock", "prices_current"],
                possible_outcomes=["valid", "items_unavailable", "price_changed"],
            ),
            WorkflowStep(
                order=2,
                name="inventory_reservation",
                description="Reserve inventory for cart items",
                entity="product",
                action="update",
                validations=["sufficient_stock"],
                possible_outcomes=["reserved", "insufficient_stock"],
            ),
            WorkflowStep(
                order=3,
                name="pricing_calculation",
                description="Calculate final pricing with tax and shipping",
                entity="cart",
                action="update",
                validations=["tax_calculated", "shipping_calculated"],
                possible_outcomes=["calculated", "tax_error", "shipping_unavailable"],
            ),
            WorkflowStep(
                order=4,
                name="payment_processing",
                description="Process payment through gateway",
                entity="payment",
                action="create",
                validations=["card_valid", "amount_matches", "fraud_check"],
                possible_outcomes=["authorized", "declined", "fraud_detected", "timeout"],
            ),
            WorkflowStep(
                order=5,
                name="order_creation",
                description="Create order from cart and payment",
                entity="order",
                action="create",
                validations=["payment_authorized", "inventory_reserved"],
                possible_outcomes=["created", "creation_failed"],
            ),
        ],
        involved_entities=["cart", "product", "customer", "payment", "order", "shipment"],
        business_rules=[
            "Cart must have at least 1 item",
            "All items must be in stock",
            "Payment must be authorized before order creation",
            "Inventory reservation expires after 15 minutes",
        ],
        edge_cases=[
            "Concurrent checkout for same cart",
            "Price change during checkout",
            "Inventory depleted during checkout",
            "Payment timeout after authorization",
            "Network failure after payment",
        ],
        test_scenarios=[
            "happy_path",
            "payment_declined",
            "inventory_conflict",
            "address_validation_failure",
            "express_checkout",
        ],
    ),
    "return_flow": WorkflowDefinition(
        name="return_flow",
        description="Customer return and refund process",
        steps=[
            WorkflowStep(
                order=1,
                name="return_request",
                description="Customer initiates return request",
                entity="return",
                action="create",
                validations=["within_return_window", "item_returnable"],
                possible_outcomes=["created", "outside_window", "non_returnable"],
            ),
            WorkflowStep(
                order=2,
                name="return_approval",
                description="Review and approve return request",
                entity="return",
                action="update",
                validations=["reason_valid", "not_fraudulent"],
                possible_outcomes=["approved", "denied", "pending_review"],
            ),
            WorkflowStep(
                order=3,
                name="refund_processing",
                description="Process refund to original payment method",
                entity="payment",
                action="create",
                validations=["amount_calculated", "method_available"],
                possible_outcomes=["refunded", "refund_failed"],
            ),
        ],
        involved_entities=["order", "return", "shipment", "product", "payment"],
        business_rules=[
            "Returns must be within 30 days of delivery",
            "Items must be in original condition",
            "Refund to original payment method",
        ],
        edge_cases=[
            "Return of partial order",
            "Return with damaged item",
            "Refund to expired card",
            "Return after return window with exception",
        ],
        test_scenarios=[
            "full_refund",
            "partial_refund",
            "denied_return",
            "exchange_request",
            "store_credit",
        ],
    ),
}


def get_workflow(name: str) -> WorkflowDefinition | None:
    """Get workflow definition by name."""
    return WORKFLOWS.get(name.lower())


def list_workflows() -> list[WorkflowDefinition]:
    """List all workflows."""
    return list(WORKFLOWS.values())


def get_workflows_for_entity(entity: str) -> list[WorkflowDefinition]:
    """Get all workflows involving a specific entity."""
    return [w for w in WORKFLOWS.values() if entity in w.involved_entities]