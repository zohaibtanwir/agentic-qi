"""Comprehensive eCommerce knowledge documents for the knowledge base."""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class KnowledgeDocument:
    """Knowledge document structure."""
    id: str
    collection_type: str
    title: str
    content: str
    entity: str
    tags: List[str]
    metadata: Dict[str, Any]

# Business Rules Documents
BUSINESS_RULES_DOCUMENTS = [
    {
        "rule_id": "BR001",
        "name": "Cart Minimum Order Value",
        "entity": "cart",
        "description": "Shopping cart must have minimum order value of $1.00 to proceed to checkout",
        "condition": "When customer attempts to checkout",
        "constraint": "Cart total >= $1.00",
        "severity": "error",
        "validation_logic": """
            if cart.total_amount < 1.00:
                raise ValidationError("Minimum order value is $1.00")
            return True
        """
    },
    {
        "rule_id": "BR002",
        "name": "Cart Item Quantity Limits",
        "entity": "cart",
        "description": "Item quantity must be between 1 and 99",
        "condition": "When adding or updating cart items",
        "constraint": "1 <= quantity <= 99",
        "severity": "error",
        "validation_logic": """
            if item.quantity < 1 or item.quantity > 99:
                raise ValidationError("Quantity must be between 1 and 99")
            return True
        """
    },
    {
        "rule_id": "BR003",
        "name": "Payment Authorization Expiry",
        "entity": "payment",
        "description": "Payment authorizations expire after 7 days",
        "condition": "After payment authorization",
        "constraint": "Authorization valid for 7 days",
        "severity": "warning",
        "validation_logic": """
            if (current_time - authorization.created_at).days >= 7:
                void_authorization(authorization.id)
                return False
            return True
        """
    },
    {
        "rule_id": "BR004",
        "name": "Order Total Payment Match",
        "entity": "order",
        "description": "Order total must match payment amount",
        "condition": "When processing payment for order",
        "constraint": "order.total == payment.amount",
        "severity": "error",
        "validation_logic": """
            if abs(order.total - payment.amount) > 0.01:
                raise ValidationError("Payment amount doesn't match order total")
            return True
        """
    },
    {
        "rule_id": "BR005",
        "name": "Inventory Reservation Timeout",
        "entity": "inventory",
        "description": "Inventory reservations expire after 15 minutes",
        "condition": "When item added to cart",
        "constraint": "Reservation valid for 15 minutes",
        "severity": "warning",
        "validation_logic": """
            if (current_time - reservation.created_at).minutes > 15:
                release_reservation(reservation.id)
                return False
            return True
        """
    },
    {
        "rule_id": "BR006",
        "name": "Shipping Address Required",
        "entity": "order",
        "description": "Physical items require shipping address",
        "condition": "When order contains physical products",
        "constraint": "Shipping address must be complete",
        "severity": "error",
        "validation_logic": """
            if order.has_physical_items and not order.shipping_address:
                raise ValidationError("Shipping address required for physical items")
            return True
        """
    },
    {
        "rule_id": "BR007",
        "name": "Return Window Policy",
        "entity": "return",
        "description": "Items can be returned within 30 days of delivery",
        "condition": "When initiating return",
        "constraint": "Return within 30 days of delivery",
        "severity": "error",
        "validation_logic": """
            if (current_date - delivery_date).days > 30:
                raise ValidationError("Return window has expired")
            return True
        """
    },
    {
        "rule_id": "BR008",
        "name": "Unique Customer Email",
        "entity": "customer",
        "description": "Email addresses must be unique across customers",
        "condition": "When creating or updating customer",
        "constraint": "Email must be unique",
        "severity": "error",
        "validation_logic": """
            if customer_exists_with_email(email):
                raise ValidationError("Email already registered")
            return True
        """
    },
    {
        "rule_id": "BR009",
        "name": "Loyalty Points Minimum",
        "entity": "customer",
        "description": "Minimum 500 points required for redemption",
        "condition": "When redeeming loyalty points",
        "constraint": "Points >= 500",
        "severity": "warning",
        "validation_logic": """
            if points_to_redeem < 500:
                raise ValidationError("Minimum 500 points required for redemption")
            return True
        """
    },
    {
        "rule_id": "BR010",
        "name": "Coupon Single Use",
        "entity": "discount",
        "description": "Single-use coupons can only be used once per customer",
        "condition": "When applying coupon",
        "constraint": "One use per customer",
        "severity": "error",
        "validation_logic": """
            if coupon.single_use and customer_used_coupon(customer_id, coupon_code):
                raise ValidationError("Coupon already used")
            return True
        """
    }
]

# Edge Cases Documents
EDGE_CASES_DOCUMENTS = [
    {
        "edge_case_id": "EC001",
        "name": "Concurrent Cart Updates",
        "category": "concurrency",
        "entity": "cart",
        "workflow": "cart_management",
        "description": "Multiple sessions updating same cart simultaneously",
        "test_approach": "Simulate concurrent API calls with different session tokens",
        "expected_behavior": "Last write wins with proper versioning",
        "severity": "high",
        "example_data_json": json.dumps({
            "session_1": {"action": "add_item", "product_id": "P123", "quantity": 2},
            "session_2": {"action": "update_quantity", "product_id": "P123", "quantity": 5},
            "timing": "simultaneous"
        })
    },
    {
        "edge_case_id": "EC002",
        "name": "Payment Timeout After Authorization",
        "category": "network",
        "entity": "payment",
        "workflow": "checkout",
        "description": "Network timeout after payment authorized but before confirmation",
        "test_approach": "Simulate network failure after authorization request",
        "expected_behavior": "Idempotent retry with status check",
        "severity": "critical",
        "example_data_json": json.dumps({
            "payment_amount": 150.00,
            "timeout_after": "authorization",
            "retry_count": 3
        })
    },
    {
        "edge_case_id": "EC003",
        "name": "Inventory Oversell Flash Sale",
        "category": "concurrency",
        "entity": "inventory",
        "workflow": "flash_sale",
        "description": "Multiple customers buying last units during high traffic",
        "test_approach": "Load test with 1000 concurrent purchases of 10 items",
        "expected_behavior": "No overselling, graceful sold out messaging",
        "severity": "critical",
        "example_data_json": json.dumps({
            "available_quantity": 10,
            "concurrent_buyers": 1000,
            "requests_per_second": 500
        })
    },
    {
        "edge_case_id": "EC004",
        "name": "Price Change During Checkout",
        "category": "timing",
        "entity": "cart",
        "workflow": "checkout",
        "description": "Product price changes while customer in checkout",
        "test_approach": "Update price after checkout started",
        "expected_behavior": "Honor price at cart addition or notify customer",
        "severity": "high",
        "example_data_json": json.dumps({
            "original_price": 99.99,
            "new_price": 119.99,
            "change_timing": "during_payment"
        })
    },
    {
        "edge_case_id": "EC005",
        "name": "Guest to Account Conversion",
        "category": "data_integrity",
        "entity": "customer",
        "workflow": "account_creation",
        "description": "Guest checkout customer creates account with same email",
        "test_approach": "Create account after guest checkout with same email",
        "expected_behavior": "Merge guest orders with new account",
        "severity": "medium",
        "example_data_json": json.dumps({
            "guest_email": "user@example.com",
            "guest_orders": ["ORD-001", "ORD-002"],
            "action": "create_account"
        })
    },
    {
        "edge_case_id": "EC006",
        "name": "Split Shipment Tracking",
        "category": "complexity",
        "entity": "shipping",
        "workflow": "fulfillment",
        "description": "Single order shipped in multiple packages",
        "test_approach": "Create order with items from different warehouses",
        "expected_behavior": "Consolidated tracking with all packages",
        "severity": "medium",
        "example_data_json": json.dumps({
            "order_id": "ORD-123",
            "packages": [
                {"tracking": "TRACK001", "warehouse": "WH-EAST"},
                {"tracking": "TRACK002", "warehouse": "WH-WEST"}
            ]
        })
    },
    {
        "edge_case_id": "EC007",
        "name": "Partial Refund Complex Order",
        "category": "financial",
        "entity": "payment",
        "workflow": "refund",
        "description": "Partial refund on order with discounts and loyalty points",
        "test_approach": "Return subset of items from discounted order",
        "expected_behavior": "Proportional refund calculation",
        "severity": "high",
        "example_data_json": json.dumps({
            "order_total": 200.00,
            "discount": 20.00,
            "points_used": 1000,
            "items_to_return": ["ITEM-001"],
            "item_value": 50.00
        })
    },
    {
        "edge_case_id": "EC008",
        "name": "Cart Session Expiry During Checkout",
        "category": "timing",
        "entity": "cart",
        "workflow": "checkout",
        "description": "User session expires during payment entry",
        "test_approach": "Expire session after checkout start",
        "expected_behavior": "Preserve cart and allow continuation",
        "severity": "high",
        "example_data_json": json.dumps({
            "session_timeout": 900,
            "checkout_duration": 1200,
            "cart_items": 5
        })
    },
    {
        "edge_case_id": "EC009",
        "name": "International Tax Calculation",
        "category": "compliance",
        "entity": "order",
        "workflow": "international_checkout",
        "description": "Complex tax calculation for international orders",
        "test_approach": "Test various country/state combinations",
        "expected_behavior": "Accurate VAT/GST calculation",
        "severity": "critical",
        "example_data_json": json.dumps({
            "shipping_country": "GB",
            "order_value": 150.00,
            "vat_rate": 0.20,
            "customs_threshold": 135.00
        })
    },
    {
        "edge_case_id": "EC010",
        "name": "Loyalty Points Race Condition",
        "category": "concurrency",
        "entity": "customer",
        "workflow": "loyalty",
        "description": "Points used simultaneously across channels",
        "test_approach": "Concurrent point redemption requests",
        "expected_behavior": "Prevent double spending of points",
        "severity": "high",
        "example_data_json": json.dumps({
            "available_points": 1000,
            "redemption_1": 800,
            "redemption_2": 500,
            "timing": "simultaneous"
        })
    }
]

# Test Scenarios Documents
TEST_SCENARIOS_DOCUMENTS = [
    {
        "scenario_id": "TS001",
        "name": "Black Friday Load Test",
        "entity": "order",
        "description": "Simulate Black Friday traffic surge",
        "test_data": {
            "concurrent_users": 100000,
            "orders_per_minute": 50000,
            "duration_hours": 4,
            "traffic_pattern": "surge"
        },
        "success_criteria": {
            "uptime": "99.9%",
            "response_time_p95": "3s",
            "order_loss": "0%",
            "payment_failure": "<1%"
        }
    },
    {
        "scenario_id": "TS002",
        "name": "Cart Abandonment Recovery",
        "entity": "cart",
        "description": "Test cart recovery workflows",
        "test_data": {
            "abandoned_carts": 1000,
            "recovery_emails": [1, 24, 72],  # hours
            "incentive_offered": True,
            "channels": ["email", "push", "retargeting"]
        },
        "success_criteria": {
            "recovery_rate": ">10%",
            "email_open_rate": ">30%",
            "conversion_rate": ">5%"
        }
    },
    {
        "scenario_id": "TS003",
        "name": "International Checkout Flow",
        "entity": "order",
        "description": "Complete international checkout testing",
        "test_data": {
            "countries": ["US", "GB", "DE", "JP", "AU"],
            "currencies": ["USD", "GBP", "EUR", "JPY", "AUD"],
            "payment_methods": ["card", "paypal", "local"],
            "shipping_methods": ["standard", "express", "economy"]
        },
        "success_criteria": {
            "tax_accuracy": "100%",
            "currency_conversion": "accurate",
            "address_validation": "working",
            "customs_forms": "generated"
        }
    },
    {
        "scenario_id": "TS004",
        "name": "Inventory Synchronization",
        "entity": "inventory",
        "description": "Test inventory sync across channels",
        "test_data": {
            "channels": ["web", "mobile", "pos", "marketplace"],
            "update_frequency": "real-time",
            "conflict_resolution": "last-write-wins",
            "buffer_stock": 10
        },
        "success_criteria": {
            "sync_delay": "<1s",
            "accuracy": ">99.9%",
            "oversell_rate": "0%"
        }
    },
    {
        "scenario_id": "TS005",
        "name": "Payment Failure Recovery",
        "entity": "payment",
        "description": "Test payment failure handling",
        "test_data": {
            "failure_types": ["declined", "timeout", "insufficient_funds", "3ds_fail"],
            "retry_strategy": "exponential_backoff",
            "alternative_methods": ["different_card", "paypal", "pay_later"],
            "communication": ["inline_message", "email", "support"]
        },
        "success_criteria": {
            "recovery_rate": ">30%",
            "customer_clarity": "high",
            "support_tickets": "<5%"
        }
    }
]

# Best Practices Documents
BEST_PRACTICES_DOCUMENTS = [
    {
        "practice_id": "BP001",
        "title": "Implement Idempotent Payment Processing",
        "category": "payment",
        "description": """
        Always use idempotency keys for payment operations to prevent duplicate charges.

        Implementation:
        - Generate unique idempotency key for each payment request
        - Store key with payment status
        - Return cached result for duplicate requests
        - Expire keys after 24 hours

        Benefits:
        - Prevents double charging
        - Safe retry on network failures
        - Better customer experience
        """,
        "entities": ["payment", "order"],
        "impact": "critical"
    },
    {
        "practice_id": "BP002",
        "title": "Use Optimistic Locking for Inventory",
        "category": "inventory",
        "description": """
        Implement optimistic locking with version numbers for inventory updates.

        Implementation:
        - Add version field to inventory records
        - Include version in update queries
        - Retry on version mismatch
        - Use Redis for high-speed operations

        Benefits:
        - Prevents overselling
        - Better concurrency handling
        - Scalable solution
        """,
        "entities": ["inventory", "cart"],
        "impact": "high"
    },
    {
        "practice_id": "BP003",
        "title": "Implement Progressive Cart Save",
        "category": "cart",
        "description": """
        Automatically save cart changes to reduce abandonment.

        Implementation:
        - Save on every cart modification
        - Sync across devices
        - Persist for logged-in users
        - 30-day retention for guests

        Benefits:
        - Reduced cart abandonment
        - Better user experience
        - Cross-device shopping
        """,
        "entities": ["cart", "customer"],
        "impact": "high"
    },
    {
        "practice_id": "BP004",
        "title": "Multi-Channel Order Tracking",
        "category": "shipping",
        "description": """
        Provide unified tracking across all shipments.

        Implementation:
        - Aggregate tracking from all carriers
        - Real-time status updates
        - Proactive delay notifications
        - Visual delivery timeline

        Benefits:
        - Reduced support inquiries
        - Better customer satisfaction
        - Proactive communication
        """,
        "entities": ["shipping", "order"],
        "impact": "medium"
    },
    {
        "practice_id": "BP005",
        "title": "Implement Smart Search with Typo Tolerance",
        "category": "search",
        "description": """
        Use elasticsearch with fuzzy matching for product search.

        Implementation:
        - Fuzzy matching for typos
        - Synonym handling
        - Faceted search
        - Personalized results
        - Search analytics

        Benefits:
        - Better product discovery
        - Higher conversion rates
        - Improved user experience
        """,
        "entities": ["product", "search"],
        "impact": "high"
    }
]

# Performance Patterns Documents
PERFORMANCE_PATTERNS_DOCUMENTS = [
    {
        "pattern_id": "PERF001",
        "title": "Database Connection Pooling",
        "category": "database",
        "description": """
        Optimize database connections with proper pooling.

        Configuration:
        - Min connections: 10
        - Max connections: 100
        - Idle timeout: 30s
        - Connection lifetime: 1 hour

        Monitoring:
        - Track active connections
        - Monitor wait times
        - Alert on pool exhaustion
        """,
        "impact_metrics": {
            "latency_reduction": "40%",
            "throughput_increase": "3x",
            "resource_usage": "-60%"
        }
    },
    {
        "pattern_id": "PERF002",
        "title": "Redis Caching Strategy",
        "category": "caching",
        "description": """
        Implement multi-layer caching with Redis.

        Cache Layers:
        - L1: Application memory (1min TTL)
        - L2: Redis (5min TTL)
        - L3: Database

        Cache Keys:
        - Product: product:{id}
        - Cart: cart:{user_id}
        - Session: session:{token}

        Invalidation:
        - Write-through for critical data
        - TTL-based for read-heavy data
        """,
        "impact_metrics": {
            "cache_hit_rate": "85%",
            "response_time": "-70%",
            "database_load": "-80%"
        }
    },
    {
        "pattern_id": "PERF003",
        "title": "Async Order Processing",
        "category": "architecture",
        "description": """
        Process orders asynchronously for better scalability.

        Implementation:
        - Queue orders after payment
        - Process in background workers
        - Send real-time updates
        - Handle failures gracefully

        Queue Configuration:
        - Workers: 10-50 (auto-scale)
        - Retry: 3 times with backoff
        - DLQ for failed orders
        """,
        "impact_metrics": {
            "checkout_speed": "5x faster",
            "scalability": "10x orders",
            "reliability": "99.99%"
        }
    }
]

# Security Patterns Documents
SECURITY_PATTERNS_DOCUMENTS = [
    {
        "pattern_id": "SEC001",
        "title": "PCI-Compliant Payment Handling",
        "category": "payment_security",
        "description": """
        Never store credit card data directly.

        Implementation:
        - Use tokenization service
        - TLS 1.2+ for all connections
        - Network segmentation
        - Regular security scans
        - Audit logging

        Compliance:
        - PCI-DSS Level 1
        - Quarterly scans
        - Annual audit
        """,
        "severity": "critical",
        "compliance": ["PCI-DSS", "GDPR"]
    },
    {
        "pattern_id": "SEC002",
        "title": "API Rate Limiting",
        "category": "api_security",
        "description": """
        Implement rate limiting to prevent abuse.

        Limits:
        - Guest: 100 req/min
        - Authenticated: 1000 req/min
        - Cart operations: 10 req/min
        - Checkout: 5 req/hour

        Response:
        - 429 Too Many Requests
        - Retry-After header
        - Progressive penalties
        """,
        "severity": "high",
        "compliance": []
    },
    {
        "pattern_id": "SEC003",
        "title": "SQL Injection Prevention",
        "category": "data_security",
        "description": """
        Prevent SQL injection attacks.

        Prevention:
        - Use parameterized queries
        - Input validation
        - Escape special characters
        - Least privilege DB users
        - WAF rules

        Testing:
        - Automated security scans
        - Penetration testing
        - Code review
        """,
        "severity": "critical",
        "compliance": ["OWASP"]
    }
]

def get_all_knowledge_documents():
    """Get all knowledge documents for indexing."""
    documents = []

    # Add business rules
    for rule in BUSINESS_RULES_DOCUMENTS:
        documents.append({
            "type": "business_rule",
            "data": rule
        })

    # Add edge cases
    for edge_case in EDGE_CASES_DOCUMENTS:
        documents.append({
            "type": "edge_case",
            "data": edge_case
        })

    # Add test scenarios
    for scenario in TEST_SCENARIOS_DOCUMENTS:
        documents.append({
            "type": "test_scenario",
            "data": scenario
        })

    # Add best practices
    for practice in BEST_PRACTICES_DOCUMENTS:
        documents.append({
            "type": "best_practice",
            "data": practice
        })

    # Add performance patterns
    for pattern in PERFORMANCE_PATTERNS_DOCUMENTS:
        documents.append({
            "type": "performance_pattern",
            "data": pattern
        })

    # Add security patterns
    for pattern in SECURITY_PATTERNS_DOCUMENTS:
        documents.append({
            "type": "security_pattern",
            "data": pattern
        })

    return documents

def get_documents_by_entity(entity_name: str):
    """Get all documents related to a specific entity."""
    related_docs = []

    for rule in BUSINESS_RULES_DOCUMENTS:
        if rule.get("entity") == entity_name:
            related_docs.append({"type": "business_rule", "data": rule})

    for edge_case in EDGE_CASES_DOCUMENTS:
        if edge_case.get("entity") == entity_name:
            related_docs.append({"type": "edge_case", "data": edge_case})

    for scenario in TEST_SCENARIOS_DOCUMENTS:
        if scenario.get("entity") == entity_name:
            related_docs.append({"type": "test_scenario", "data": scenario})

    return related_docs

def get_edge_cases_by_category(category: str):
    """Get edge cases by category."""
    return [
        {"type": "edge_case", "data": ec}
        for ec in EDGE_CASES_DOCUMENTS
        if ec.get("category") == category
    ]

def get_critical_items():
    """Get all critical severity items."""
    critical_items = []

    # Critical edge cases
    for edge_case in EDGE_CASES_DOCUMENTS:
        if edge_case.get("severity") == "critical":
            critical_items.append({"type": "edge_case", "data": edge_case})

    # Critical security patterns
    for pattern in SECURITY_PATTERNS_DOCUMENTS:
        if pattern.get("severity") == "critical":
            critical_items.append({"type": "security_pattern", "data": pattern})

    return critical_items