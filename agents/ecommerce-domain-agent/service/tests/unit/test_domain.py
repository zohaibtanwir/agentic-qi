import pytest
from ecommerce_agent.domain.entities import get_entity, list_entities, get_entity_categories
from ecommerce_agent.domain.workflows import get_workflow, list_workflows, get_workflows_for_entity
from ecommerce_agent.domain.business_rules import (
    get_business_rule,
    get_rules_for_entity,
    Severity,
)
from ecommerce_agent.domain.edge_cases import (
    get_edge_case,
    get_edge_cases_for_entity,
    get_edge_cases_by_severity,
)


class TestEntities:
    def test_get_entity_exists(self):
        """Test getting an existing entity."""
        cart = get_entity("cart")
        assert cart is not None
        assert cart.name == "cart"
        assert cart.description == "Shopping cart containing items before checkout"

    def test_get_entity_not_exists(self):
        """Test getting a non-existing entity."""
        entity = get_entity("nonexistent")
        assert entity is None

    def test_list_entities(self):
        """Test listing all entities."""
        entities = list_entities()
        assert len(entities) > 0
        assert any(e.name == "cart" for e in entities)

    def test_list_entities_by_category(self):
        """Test filtering entities by category."""
        transactional = list_entities("transactional")
        assert all(e.category == "transactional" for e in transactional)

    def test_get_entity_categories(self):
        """Test getting unique categories."""
        categories = get_entity_categories()
        assert "transactional" in categories
        assert "financial" in categories


class TestWorkflows:
    def test_get_workflow_exists(self):
        """Test getting an existing workflow."""
        checkout = get_workflow("checkout")
        assert checkout is not None
        assert checkout.name == "checkout"
        assert len(checkout.steps) > 0

    def test_get_workflow_not_exists(self):
        """Test getting a non-existing workflow."""
        workflow = get_workflow("nonexistent")
        assert workflow is None

    def test_list_workflows(self):
        """Test listing all workflows."""
        workflows = list_workflows()
        assert len(workflows) > 0
        assert any(w.name == "checkout" for w in workflows)

    def test_get_workflows_for_entity(self):
        """Test getting workflows for a specific entity."""
        cart_workflows = get_workflows_for_entity("cart")
        assert len(cart_workflows) > 0
        assert any(w.name == "checkout" for w in cart_workflows)


class TestBusinessRules:
    def test_get_business_rule_exists(self):
        """Test getting an existing business rule."""
        rule = get_business_rule("BR001")
        assert rule is not None
        assert rule.name == "cart_item_quantity_limit"

    def test_get_business_rule_not_exists(self):
        """Test getting a non-existing business rule."""
        rule = get_business_rule("BR999")
        assert rule is None

    def test_get_rules_for_entity(self):
        """Test getting rules for a specific entity."""
        cart_rules = get_rules_for_entity("cart")
        assert len(cart_rules) > 0
        assert any(r.entity == "cart" for r in cart_rules)


class TestEdgeCases:
    def test_get_edge_case_exists(self):
        """Test getting an existing edge case."""
        edge_case = get_edge_case("EC001")
        assert edge_case is not None
        assert edge_case.name == "concurrent_cart_update"

    def test_get_edge_case_not_exists(self):
        """Test getting a non-existing edge case."""
        edge_case = get_edge_case("EC999")
        assert edge_case is None

    def test_get_edge_cases_for_entity(self):
        """Test getting edge cases for a specific entity."""
        cart_edges = get_edge_cases_for_entity("cart")
        assert len(cart_edges) > 0

    def test_get_edge_cases_by_severity(self):
        """Test getting edge cases by severity."""
        critical = get_edge_cases_by_severity("critical")
        assert all(ec.severity == "critical" for ec in critical)