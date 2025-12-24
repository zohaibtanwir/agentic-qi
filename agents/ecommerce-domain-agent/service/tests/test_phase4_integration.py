"""Tests for Phase 4: Test Data Integration."""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import asdict

from ecommerce_agent.context.builder import (
    DomainContext,
    DomainContextBuilder,
    get_context_builder,
)
from ecommerce_agent.enrichment.enricher import (
    RequestEnricher,
    EnrichmentResult,
    get_enricher,
)
from ecommerce_agent.orchestrator.generator import (
    GenerationOrchestrator,
    GenerationRequest,
    GenerationResult,
    get_orchestrator,
)
from ecommerce_agent.clients.test_data_client import TestDataAgentClient


# ========== Context Builder Tests ==========

class TestDomainContextBuilder:
    """Tests for DomainContextBuilder."""

    @pytest.mark.asyncio
    async def test_build_context_basic(self):
        """Test basic context building."""
        builder = DomainContextBuilder(use_knowledge=False)

        context = await builder.build_context(
            entity="cart",
            workflow=None,
            scenario=None,
            include_edge_cases=True,
        )

        assert context is not None
        assert context.entity_name == "cart"
        assert context.entity_description
        assert len(context.fields) > 0
        assert len(context.business_rules) > 0
        assert len(context.edge_cases) > 0
        assert context.natural_language_context

    @pytest.mark.asyncio
    async def test_build_context_with_workflow(self):
        """Test context building with workflow."""
        builder = DomainContextBuilder(use_knowledge=False)

        context = await builder.build_context(
            entity="cart",
            workflow="checkout",
            include_edge_cases=True,
        )

        assert context.workflow_context == "checkout"
        assert context.workflow_steps is not None
        assert len(context.workflow_steps) > 0

    @pytest.mark.asyncio
    async def test_build_context_with_scenario(self):
        """Test context building with scenario hints."""
        builder = DomainContextBuilder(use_knowledge=False)

        # Test happy path scenario
        context = await builder.build_context(
            entity="cart",
            scenario="happy_path",
        )
        assert "realistic" in context.generation_hints
        assert "valid" in context.generation_hints

        # Test edge case scenario
        context = await builder.build_context(
            entity="cart",
            scenario="edge_cases",
        )
        assert "edge_case" in context.generation_hints

        # Test error scenario
        context = await builder.build_context(
            entity="cart",
            scenario="error_conditions",
        )
        assert "invalid" in context.generation_hints

    @pytest.mark.asyncio
    async def test_build_context_unknown_entity(self):
        """Test context building with unknown entity."""
        builder = DomainContextBuilder(use_knowledge=False)

        context = await builder.build_context(
            entity="unknown_entity",
        )

        assert context.entity_name == "unknown_entity"
        assert "Unknown entity" in context.entity_description
        assert len(context.fields) == 0
        assert len(context.business_rules) == 0

    def test_extract_scenarios_from_context(self):
        """Test scenario extraction from context."""
        builder = DomainContextBuilder(use_knowledge=False)

        context = DomainContext(
            entity_name="cart",
            entity_description="Shopping cart",
            fields=[],
            relationships=[],
            business_rules=[],
            edge_cases=["Empty cart: Cart with no items"],
            test_scenarios=["happy_path", "empty_cart", "max_items"],
        )

        # Test default extraction
        scenarios = builder.extract_scenarios_from_context(context)
        assert len(scenarios) > 0
        assert scenarios[0]["name"] == "happy_path"

        # Test with requested scenarios
        scenarios = builder.extract_scenarios_from_context(
            context,
            requested_scenarios=["custom_scenario"],
        )
        assert scenarios[0]["name"] == "custom_scenario"

    def test_build_constraints(self):
        """Test constraint building from context."""
        builder = DomainContextBuilder(use_knowledge=False)

        context = DomainContext(
            entity_name="cart",
            entity_description="Cart",
            fields=[
                {"name": "quantity", "type": "integer"},
                {"name": "total", "type": "decimal"},
                {"name": "status", "type": "enum", "description": "Status: pending, completed"},
            ],
            relationships=[],
            business_rules=["Quantity must be between 1-99", "Total must be >= $1.00"],
            edge_cases=[],
            test_scenarios=[],
        )

        constraints = builder._build_constraints(context)

        assert "quantity" in constraints
        assert constraints["quantity"]["min"] == 1
        assert constraints["quantity"]["max"] == 99

        assert "total" in constraints
        assert constraints["total"]["min"] == 1.00

        assert "status" in constraints
        assert "enum_values" in constraints["status"]

    def test_get_context_builder(self):
        """Test getting context builder instance."""
        builder = get_context_builder(use_knowledge=False)
        assert builder is not None
        assert isinstance(builder, DomainContextBuilder)


# ========== Request Enricher Tests ==========

class TestRequestEnricher:
    """Tests for RequestEnricher."""

    @pytest.mark.asyncio
    async def test_enrich_request_basic(self):
        """Test basic request enrichment."""
        enricher = RequestEnricher(use_knowledge=False)

        result = await enricher.enrich_request(
            entity="cart",
            count=10,
        )

        assert result.enriched is True
        assert result.context
        assert len(result.hints) > 0
        assert len(result.scenarios) > 0
        assert result.error is None

    @pytest.mark.asyncio
    async def test_enrich_request_with_workflow(self):
        """Test enrichment with workflow."""
        enricher = RequestEnricher(use_knowledge=False)

        result = await enricher.enrich_request(
            entity="cart",
            workflow="checkout",
            count=5,
        )

        assert result.enriched is True
        assert "checkout" in result.metadata.get("workflow", "")

    @pytest.mark.asyncio
    async def test_enrich_request_production_like(self):
        """Test production-like enrichment."""
        enricher = RequestEnricher(use_knowledge=False)

        result = await enricher.enrich_request(
            entity="cart",
            production_like=True,
        )

        assert "production_like" in result.hints
        assert "realistic_distributions" in result.hints

    @pytest.mark.asyncio
    async def test_enrich_request_with_user_scenarios(self):
        """Test enrichment with user-provided scenarios."""
        enricher = RequestEnricher(use_knowledge=False)

        user_scenarios = [
            {
                "name": "custom_scenario",
                "count": 5,
                "description": "Custom test",
                "overrides": {"custom_field": "value"},
            }
        ]

        result = await enricher.enrich_request(
            entity="cart",
            count=10,
            user_scenarios=user_scenarios,
        )

        assert len(result.scenarios) > 0
        assert result.scenarios[0]["name"] == "custom_scenario"
        assert result.scenarios[0]["overrides"]["custom_field"] == "value"

    @pytest.mark.asyncio
    async def test_enrich_batch(self):
        """Test batch enrichment."""
        enricher = RequestEnricher(use_knowledge=False)

        requests = [
            {"entity": "cart", "count": 5},
            {"entity": "order", "count": 10, "workflow": "checkout"},
        ]

        results = await enricher.enrich_batch(requests)

        assert len(results) == 2
        assert all(r.enriched for r in results)

    def test_validate_enrichment(self):
        """Test enrichment validation."""
        enricher = RequestEnricher(use_knowledge=False)

        # Valid enrichment
        valid_result = EnrichmentResult(
            enriched=True,
            context="Generate test data for cart",
            hints=["realistic"],
            scenarios=[{"name": "default", "count": 10}],
            constraints={},
            metadata={},
        )

        is_valid, errors = enricher.validate_enrichment(valid_result)
        assert is_valid is True
        assert len(errors) == 0

        # Invalid enrichment - no context
        invalid_result = EnrichmentResult(
            enriched=True,
            context="",
            hints=[],
            scenarios=[],
            constraints={},
            metadata={},
        )

        is_valid, errors = enricher.validate_enrichment(invalid_result)
        assert is_valid is False
        assert len(errors) > 0

    def test_get_enricher(self):
        """Test getting enricher instance."""
        enricher = get_enricher(use_knowledge=False)
        assert enricher is not None
        assert isinstance(enricher, RequestEnricher)


# ========== Generation Orchestrator Tests ==========

class TestGenerationOrchestrator:
    """Tests for GenerationOrchestrator."""

    @pytest.mark.asyncio
    async def test_generate_basic(self):
        """Test basic generation orchestration."""
        with patch('ecommerce_agent.orchestrator.generator.get_test_data_client') as mock_client:
            # Mock Test Data Agent client
            mock_tda = AsyncMock()
            mock_tda.generate_data = AsyncMock(return_value={
                "request_id": "test-123",
                "success": True,
                "data": json.dumps([{"id": 1, "name": "test"}]),
                "record_count": 1,
            })
            mock_client.return_value = mock_tda

            orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

            request = GenerationRequest(
                entity="cart",
                count=1,
            )

            result = await orchestrator.generate(request, request_id="test-123")

            assert result.success is True
            assert result.request_id == "test-123"
            assert result.record_count == 1
            assert result.data

    @pytest.mark.asyncio
    async def test_generate_with_workflow(self):
        """Test generation with workflow."""
        with patch('ecommerce_agent.orchestrator.generator.get_test_data_client') as mock_client:
            mock_tda = AsyncMock()
            mock_tda.generate_data = AsyncMock(return_value={
                "success": True,
                "data": "[]",
                "record_count": 0,
            })
            mock_client.return_value = mock_tda

            orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

            request = GenerationRequest(
                entity="cart",
                workflow="checkout",
                count=5,
            )

            result = await orchestrator.generate(request)

            assert result.workflow == "checkout"

    @pytest.mark.asyncio
    async def test_generate_failure(self):
        """Test generation failure handling."""
        with patch('ecommerce_agent.orchestrator.generator.get_test_data_client') as mock_client:
            mock_tda = AsyncMock()
            mock_tda.generate_data = AsyncMock(return_value={
                "success": False,
                "error": "Test error",
                "data": "",
                "record_count": 0,
            })
            mock_client.return_value = mock_tda

            orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

            request = GenerationRequest(entity="cart")
            result = await orchestrator.generate(request)

            assert result.success is False
            assert result.error == "Test error"

    def test_validate_request(self):
        """Test request validation."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

        # Valid request
        valid_request = GenerationRequest(
            entity="cart",
            count=10,
            output_format="JSON",
        )
        is_valid, errors = orchestrator.validate_request(valid_request)
        assert is_valid is True
        assert len(errors) == 0

        # Invalid - no entity
        invalid_request = GenerationRequest(
            entity="",
            count=10,
        )
        is_valid, errors = orchestrator.validate_request(invalid_request)
        assert is_valid is False
        assert "Entity is required" in errors

        # Invalid - negative count
        invalid_request = GenerationRequest(
            entity="cart",
            count=-5,
        )
        is_valid, errors = orchestrator.validate_request(invalid_request)
        assert is_valid is False
        assert "Count must be positive" in errors

        # Invalid - count too large
        invalid_request = GenerationRequest(
            entity="cart",
            count=50000,
        )
        is_valid, errors = orchestrator.validate_request(invalid_request)
        assert is_valid is False
        assert "Count cannot exceed 10000" in errors

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

        result = GenerationResult(
            request_id="test",
            success=True,
            data='[{"id": 1}]',
            record_count=1,
            entity="cart",
            metadata={"json_valid": True},
            enrichment_metadata={"business_rules_count": 5, "edge_cases_count": 3},
            generation_metadata={"coherence_score": 0.85},
        )

        score = orchestrator._calculate_quality_score(result)
        assert score > 0.5
        assert score <= 1.0

    @pytest.mark.asyncio
    async def test_generate_batch(self):
        """Test batch generation."""
        with patch('ecommerce_agent.orchestrator.generator.get_test_data_client') as mock_client:
            mock_tda = AsyncMock()
            mock_tda.generate_data = AsyncMock(return_value={
                "success": True,
                "data": "[]",
                "record_count": 0,
            })
            mock_client.return_value = mock_tda

            orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

            requests = [
                GenerationRequest(entity="cart", count=5),
                GenerationRequest(entity="order", count=10),
            ]

            results = await orchestrator.generate_batch(requests)

            assert len(results) == 2
            assert all(isinstance(r, GenerationResult) for r in results)

    def test_get_orchestrator(self):
        """Test getting orchestrator instance."""
        orchestrator = get_orchestrator(use_knowledge=False, store_patterns=False)
        assert orchestrator is not None
        assert isinstance(orchestrator, GenerationOrchestrator)


# ========== Test Data Client Tests ==========

class TestTestDataAgentClient:
    """Tests for TestDataAgentClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = TestDataAgentClient()
        assert client is not None
        assert client.target

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        client = TestDataAgentClient()

        # Mock the connection and stub
        with patch.object(client, 'connect') as mock_connect:
            mock_connect.return_value = None  # Skip actual connection

            with patch.object(client, '_stub') as mock_stub:
                mock_response = MagicMock()
                mock_response.status = "healthy"
                mock_response.components = {"test": "healthy"}

                mock_stub.HealthCheck = AsyncMock(return_value=mock_response)
                client._stub = mock_stub  # Set the stub

                result = await client.health_check()

                assert result["status"] == "healthy"
                assert "components" in result

# NOTE: test_map_output_format and test_build_constraints were removed
# as these methods were inlined into generate_data during refactoring.
# The functionality is covered by the generate_data integration tests.


# ========== Integration Tests ==========

class TestPhase4Integration:
    """End-to-end integration tests for Phase 4."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test full generation pipeline from request to result."""
        with patch('ecommerce_agent.orchestrator.generator.get_test_data_client') as mock_client:
            # Mock successful generation
            mock_tda = AsyncMock()
            mock_tda.generate_data = AsyncMock(return_value={
                "request_id": "integration-test",
                "success": True,
                "data": json.dumps([
                    {"id": 1, "items": 3, "total": 99.99},
                    {"id": 2, "items": 1, "total": 19.99},
                ]),
                "record_count": 2,
                "metadata": {
                    "generation_time_ms": 150,
                    "coherence_score": 0.92,
                },
            })
            mock_client.return_value = mock_tda

            # Create orchestrator
            orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)

            # Create request
            request = GenerationRequest(
                entity="cart",
                count=2,
                workflow="checkout",
                scenario="happy_path",
                context="Generate realistic shopping carts",
                production_like=True,
                include_edge_cases=False,
            )

            # Generate
            result = await orchestrator.generate(request, request_id="integration-test")

            # Verify result
            assert result.success is True
            assert result.request_id == "integration-test"
            assert result.record_count == 2
            assert result.entity == "cart"
            assert result.workflow == "checkout"
            assert result.scenario == "happy_path"

            # Verify data structure
            data = json.loads(result.data)
            assert len(data) == 2
            assert data[0]["id"] == 1
            assert data[0]["total"] == 99.99

    @pytest.mark.asyncio
    async def test_context_enrichment_flow(self):
        """Test that context is properly enriched through the pipeline."""
        enricher = RequestEnricher(use_knowledge=False)

        result = await enricher.enrich_request(
            entity="order",
            count=5,
            workflow="checkout",
            scenario="edge_cases",
            user_context="Test edge cases for order processing",
            production_like=True,
        )

        # Verify enrichment
        assert result.enriched is True

        # Check context includes domain knowledge
        assert "order" in result.context.lower()
        assert "User Context:" in result.context
        assert "Test edge cases" in result.context

        # Check hints are appropriate
        assert "edge_case" in result.hints or "boundary" in result.hints
        assert "production_like" in result.hints

        # Check scenarios
        assert len(result.scenarios) > 0

        # Check metadata
        assert result.metadata["entity"] == "order"
        assert result.metadata["workflow"] == "checkout"
        assert result.metadata["scenario"] == "edge_cases"