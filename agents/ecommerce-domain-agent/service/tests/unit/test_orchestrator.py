"""Unit tests for the generation orchestrator."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ecommerce_agent.orchestrator.generator import (
    GenerationRequest,
    GenerationResult,
    GenerationOrchestrator,
    get_orchestrator,
)
from ecommerce_agent.enrichment.enricher import EnrichmentResult


class TestGenerationRequest:
    def test_default_values(self):
        """Test GenerationRequest default values."""
        request = GenerationRequest(entity="order")
        assert request.entity == "order"
        assert request.count == 10
        assert request.workflow is None
        assert request.scenario is None
        assert request.output_format == "JSON"
        assert request.include_edge_cases is True
        assert request.production_like is True
        assert request.use_cache is True
        assert request.generation_method == "HYBRID"

    def test_custom_values(self):
        """Test GenerationRequest with custom values."""
        request = GenerationRequest(
            entity="cart",
            count=5,
            workflow="checkout",
            generation_method="LLM",
            production_like=False,
        )
        assert request.entity == "cart"
        assert request.count == 5
        assert request.workflow == "checkout"
        assert request.generation_method == "LLM"
        assert request.production_like is False


class TestGenerationResult:
    def test_result_creation(self):
        """Test GenerationResult creation."""
        result = GenerationResult(
            request_id="test-123",
            success=True,
            data='[{"id": 1}]',
            record_count=1,
            entity="order",
        )
        assert result.request_id == "test-123"
        assert result.success is True
        assert result.record_count == 1
        assert result.generated_at is not None


class TestGenerationOrchestrator:
    def test_validate_request_valid(self):
        """Test validation of valid request."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)
        request = GenerationRequest(entity="order", count=10)
        is_valid, errors = orchestrator.validate_request(request)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_request_missing_entity(self):
        """Test validation with missing entity."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)
        request = GenerationRequest(entity="", count=10)
        is_valid, errors = orchestrator.validate_request(request)
        assert is_valid is False
        assert "Entity is required" in errors

    def test_validate_request_invalid_count(self):
        """Test validation with invalid count."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)
        request = GenerationRequest(entity="order", count=0)
        is_valid, errors = orchestrator.validate_request(request)
        assert is_valid is False
        assert "Count must be positive" in errors

    def test_validate_request_count_too_high(self):
        """Test validation with count too high."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)
        request = GenerationRequest(entity="order", count=15000)
        is_valid, errors = orchestrator.validate_request(request)
        assert is_valid is False
        assert "Count cannot exceed 10000" in errors

    def test_validate_request_invalid_format(self):
        """Test validation with invalid output format."""
        orchestrator = GenerationOrchestrator(use_knowledge=False, store_patterns=False)
        request = GenerationRequest(entity="order", count=10, output_format="XML")
        is_valid, errors = orchestrator.validate_request(request)
        assert is_valid is False
        assert any("Output format" in e for e in errors)


class TestSchemaBuilder:
    def test_determine_generation_strategy_predefined(self):
        """Test strategy for predefined entities."""
        from ecommerce_agent.orchestrator.schema_builder import get_schema_builder

        builder = get_schema_builder()
        strategy, schema = builder.determine_generation_strategy("user")
        assert strategy == "predefined"
        assert schema is None

    def test_determine_generation_strategy_custom(self):
        """Test strategy for domain entities."""
        from ecommerce_agent.orchestrator.schema_builder import get_schema_builder

        builder = get_schema_builder()
        strategy, schema = builder.determine_generation_strategy("order")
        assert strategy == "custom"
        assert schema is not None
        assert schema["name"] == "order"
        assert "fields" in schema

    def test_build_schema_has_metadata(self):
        """Test that built schema has metadata."""
        from ecommerce_agent.orchestrator.schema_builder import get_schema_builder

        builder = get_schema_builder()
        schema = builder.build_schema_from_entity("cart")
        assert "metadata" in schema
        assert schema["metadata"]["domain"] == "ecommerce"
        assert "test_scenarios" in schema["metadata"]
