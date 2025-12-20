from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class EdgeCase:
    """Definition of an edge case scenario."""

    id: str
    name: str
    description: str
    category: str  # concurrency, network, boundary, etc.
    entity: Optional[str]
    workflow: Optional[str]
    test_approach: str
    expected_behavior: str
    severity: str  # critical, high, medium, low
    example_data: Dict[str, str] = None


EDGE_CASES: List[EdgeCase] = [
    # Concurrency Edge Cases
    EdgeCase(
        id="EC001",
        name="concurrent_cart_update",
        category="concurrency",
        entity="cart",
        workflow=None,
        description="Two sessions update the same cart simultaneously",
        test_approach="Race condition testing with parallel requests",
        expected_behavior="Last write wins or optimistic locking prevents conflict",
        severity="high",
        example_data={"session1": "add_item", "session2": "remove_item"},
    ),
    EdgeCase(
        id="EC002",
        name="inventory_oversell",
        category="concurrency",
        entity="order",
        workflow="checkout",
        description="Multiple orders for last item in stock",
        test_approach="Parallel checkout requests for low-stock item",
        expected_behavior="Only one order succeeds, others fail gracefully",
        severity="critical",
        example_data={"inventory": "1", "concurrent_orders": "3"},
    ),
    # Network Edge Cases
    EdgeCase(
        id="EC003",
        name="payment_timeout_after_success",
        category="network",
        entity="payment",
        workflow="checkout",
        description="Payment succeeds but response times out",
        test_approach="Inject network delay after payment gateway success",
        expected_behavior="Idempotent retry or reconciliation job resolves",
        severity="critical",
        example_data={"payment_status": "success", "network": "timeout"},
    ),
    EdgeCase(
        id="EC004",
        name="partial_shipment_tracking",
        category="network",
        entity="shipment",
        workflow=None,
        description="Tracking update fails for split shipment",
        test_approach="Simulate carrier API failure for one shipment",
        expected_behavior="Graceful degradation with partial tracking info",
        severity="medium",
    ),
    # Boundary Edge Cases
    EdgeCase(
        id="EC005",
        name="max_cart_items",
        category="boundary",
        entity="cart",
        workflow=None,
        description="Cart reaches maximum item limit",
        test_approach="Add items until limit reached, then attempt one more",
        expected_behavior="Graceful error message, prevent additional items",
        severity="low",
        example_data={"item_count": "100", "attempt": "101"},
    ),
    EdgeCase(
        id="EC006",
        name="zero_value_order",
        category="boundary",
        entity="order",
        workflow="checkout",
        description="Order with 100% discount or gift card",
        test_approach="Apply discount/gift card equal to order total",
        expected_behavior="Order completes without payment processing",
        severity="medium",
        example_data={"order_total": "$100", "discount": "$100"},
    ),
    # Data Integrity Edge Cases
    EdgeCase(
        id="EC007",
        name="price_change_during_checkout",
        category="data_integrity",
        entity="cart",
        workflow="checkout",
        description="Product price changes while user is checking out",
        test_approach="Update price after cart creation but before payment",
        expected_behavior="User notified of price change, must confirm",
        severity="high",
        example_data={"original_price": "$50", "new_price": "$60"},
    ),
    EdgeCase(
        id="EC008",
        name="deleted_product_in_cart",
        category="data_integrity",
        entity="cart",
        workflow=None,
        description="Product deleted while in active cart",
        test_approach="Delete product from catalog with active cart references",
        expected_behavior="Cart shows item unavailable, prevents checkout",
        severity="medium",
    ),
    # Payment Edge Cases
    EdgeCase(
        id="EC009",
        name="duplicate_payment_submission",
        category="payment",
        entity="payment",
        workflow="checkout",
        description="User double-clicks submit payment",
        test_approach="Send identical payment requests within milliseconds",
        expected_behavior="Idempotency key prevents duplicate charges",
        severity="critical",
        example_data={"request_count": "2", "time_between": "100ms"},
    ),
    EdgeCase(
        id="EC010",
        name="expired_card_retry",
        category="payment",
        entity="payment",
        workflow="checkout",
        description="Payment with expired card, then valid card",
        test_approach="Submit expired card, handle error, submit valid card",
        expected_behavior="Graceful error handling, successful retry",
        severity="medium",
    ),
]


def get_edge_case(edge_case_id: str) -> Optional[EdgeCase]:
    """Get edge case by ID."""
    for edge_case in EDGE_CASES:
        if edge_case.id == edge_case_id:
            return edge_case
    return None


def get_edge_cases_for_entity(entity: str) -> List[EdgeCase]:
    """Get all edge cases for a specific entity."""
    return [ec for ec in EDGE_CASES if ec.entity == entity]


def get_edge_cases_for_workflow(workflow: str) -> List[EdgeCase]:
    """Get all edge cases for a specific workflow."""
    return [ec for ec in EDGE_CASES if ec.workflow == workflow]


def get_edge_cases_by_category(category: str) -> List[EdgeCase]:
    """Get all edge cases in a specific category."""
    return [ec for ec in EDGE_CASES if ec.category == category]


def get_edge_cases_by_severity(severity: str) -> List[EdgeCase]:
    """Get all edge cases with a specific severity."""
    return [ec for ec in EDGE_CASES if ec.severity == severity]