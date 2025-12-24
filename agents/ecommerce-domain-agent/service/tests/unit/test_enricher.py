"""Unit tests for the request enricher."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ecommerce_agent.enrichment.enricher import (
    RequestEnricher,
    EnrichmentResult,
    get_enricher,
)


class TestEnrichmentResult:
    def test_enrichment_result_creation(self):
        """Test EnrichmentResult creation."""
        result = EnrichmentResult(
            enriched=True,
            context="Test context",
            hints=["realistic"],
            scenarios=[{"name": "default", "count": 1, "description": "Default"}],
            constraints={},
            metadata={"entity": "order"},
        )
        assert result.enriched is True
        assert result.context == "Test context"
        assert len(result.hints) == 1
        assert len(result.scenarios) == 1
        assert result.error is None


class TestRequestEnricher:
    @pytest.fixture
    def enricher(self):
        """Create enricher without knowledge layer."""
        return RequestEnricher(use_knowledge=False)

    @pytest.mark.asyncio
    async def test_enrich_request_valid_entity(self, enricher):
        """Test enriching request for valid entity."""
        result = await enricher.enrich_request(
            entity="order",
            count=10,
            include_edge_cases=True,
        )
        assert result.enriched is True
        assert result.context is not None
        assert len(result.scenarios) > 0
        assert result.metadata["entity"] == "order"

    @pytest.mark.asyncio
    async def test_enrich_request_with_workflow(self, enricher):
        """Test enriching request with workflow context."""
        result = await enricher.enrich_request(
            entity="order",
            count=10,
            workflow="checkout",
        )
        assert result.enriched is True
        assert result.metadata.get("workflow") == "checkout"

    @pytest.mark.asyncio
    async def test_enrich_request_with_user_context(self, enricher):
        """Test enriching request with user-provided context."""
        result = await enricher.enrich_request(
            entity="cart",
            count=5,
            user_context="Testing holiday promotions",
        )
        assert result.enriched is True
        assert "holiday promotions" in result.context

    @pytest.mark.asyncio
    async def test_enrich_request_with_user_scenarios(self, enricher):
        """Test enriching request with user-provided scenarios."""
        user_scenarios = [
            {"name": "custom_scenario", "count": 5, "description": "Custom test"},
        ]
        result = await enricher.enrich_request(
            entity="payment",
            count=10,
            user_scenarios=user_scenarios,
        )
        assert result.enriched is True
        assert any(s["name"] == "custom_scenario" for s in result.scenarios)

    @pytest.mark.asyncio
    async def test_enrich_request_invalid_entity(self, enricher):
        """Test enriching request for invalid entity."""
        result = await enricher.enrich_request(
            entity="nonexistent_entity",
            count=10,
        )
        # Should still return minimal enrichment on failure
        assert len(result.scenarios) > 0

    def test_validate_enrichment_valid(self, enricher):
        """Test validation of valid enrichment result."""
        result = EnrichmentResult(
            enriched=True,
            context="Test context with enough content",
            hints=["realistic"],
            scenarios=[{"name": "default", "count": 10, "description": "Test"}],
            constraints={},
            metadata={},
        )
        is_valid, errors = enricher.validate_enrichment(result)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_enrichment_no_scenarios(self, enricher):
        """Test validation with no scenarios."""
        result = EnrichmentResult(
            enriched=True,
            context="Test context",
            hints=["realistic"],
            scenarios=[],
            constraints={},
            metadata={},
        )
        is_valid, errors = enricher.validate_enrichment(result)
        assert is_valid is False
        assert "No scenarios provided" in errors

    def test_build_hints_production_like(self, enricher):
        """Test hint building for production-like generation."""
        from ecommerce_agent.context.builder import DomainContext

        context = DomainContext(
            entity_name="order",
            entity_description="Test",
            fields=[],
            relationships=[],
            business_rules=[],
            edge_cases=[],
            test_scenarios=[],
            generation_hints=[],
        )
        hints = enricher._build_hints(context, None, production_like=True)
        assert "production_like" in hints
        assert "realistic_distributions" in hints

    def test_scenarios_have_required_keys(self, enricher):
        """Test that built scenarios have required keys."""
        from ecommerce_agent.context.builder import DomainContext

        context = DomainContext(
            entity_name="cart",
            entity_description="Shopping cart",
            fields=[],
            relationships=[],
            business_rules=[],
            edge_cases=[],
            test_scenarios=["happy_path", "edge_case"],
            generation_hints=[],
        )
        scenarios = enricher._build_scenarios(context, None, 10, True)
        for scenario in scenarios:
            assert "name" in scenario
            assert "count" in scenario
            assert "description" in scenario
