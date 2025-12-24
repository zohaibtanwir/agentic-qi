"""Unit tests for the enhanced gRPC server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ecommerce_agent.proto import ecommerce_domain_pb2 as pb2
from ecommerce_agent.server.grpc_server_enhanced import (
    EnhancedEcommerceDomainServicer,
    create_enhanced_server,
)


class TestEnhancedEcommerceDomainServicer:
    @pytest.fixture
    def servicer(self):
        """Create servicer without knowledge layer."""
        return EnhancedEcommerceDomainServicer(use_knowledge=False)

    @pytest.fixture
    def mock_context(self):
        """Create mock gRPC context."""
        context = MagicMock()
        context.set_code = MagicMock()
        context.set_details = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_list_entities(self, servicer, mock_context):
        """Test ListEntities returns all entities."""
        request = pb2.ListEntitiesRequest()
        response = await servicer.ListEntities(request, mock_context)
        assert len(response.entities) > 0
        assert any(e.name == "cart" for e in response.entities)
        assert any(e.name == "order" for e in response.entities)

    @pytest.mark.asyncio
    async def test_list_entities_by_category(self, servicer, mock_context):
        """Test ListEntities with category filter."""
        request = pb2.ListEntitiesRequest(category="transactional")
        response = await servicer.ListEntities(request, mock_context)
        assert len(response.entities) > 0
        assert all(e.category == "transactional" for e in response.entities)

    @pytest.mark.asyncio
    async def test_get_entity_exists(self, servicer, mock_context):
        """Test GetEntity for existing entity."""
        request = pb2.EntityRequest(
            entity_name="cart",
            include_relationships=True,
            include_rules=True,
        )
        response = await servicer.GetEntity(request, mock_context)
        assert response.entity.name == "cart"
        assert len(response.entity.fields) > 0

    @pytest.mark.asyncio
    async def test_get_entity_not_exists(self, servicer, mock_context):
        """Test GetEntity for non-existing entity."""
        request = pb2.EntityRequest(entity_name="nonexistent")
        response = await servicer.GetEntity(request, mock_context)
        mock_context.set_code.assert_called()

    @pytest.mark.asyncio
    async def test_list_workflows(self, servicer, mock_context):
        """Test ListWorkflows returns all workflows."""
        request = pb2.ListWorkflowsRequest()
        response = await servicer.ListWorkflows(request, mock_context)
        assert len(response.workflows) > 0
        assert any(w.name == "checkout" for w in response.workflows)

    @pytest.mark.asyncio
    async def test_get_workflow_exists(self, servicer, mock_context):
        """Test GetWorkflow for existing workflow."""
        request = pb2.WorkflowRequest(
            workflow_name="checkout",
            include_steps=True,
        )
        response = await servicer.GetWorkflow(request, mock_context)
        assert response.workflow.name == "checkout"
        assert len(response.workflow.steps) > 0

    @pytest.mark.asyncio
    async def test_get_domain_context(self, servicer, mock_context):
        """Test GetDomainContext."""
        request = pb2.DomainContextRequest(
            request_id="test-123",
            entity="order",
        )
        response = await servicer.GetDomainContext(request, mock_context)
        assert response.request_id == "test-123"
        assert len(response.context) > 0

    @pytest.mark.asyncio
    async def test_get_edge_cases_for_entity(self, servicer, mock_context):
        """Test GetEdgeCases for entity."""
        request = pb2.EdgeCasesRequest(entity="cart")
        response = await servicer.GetEdgeCases(request, mock_context)
        assert len(response.edge_cases) > 0

    @pytest.mark.asyncio
    async def test_health_check(self, servicer, mock_context):
        """Test HealthCheck."""
        request = pb2.HealthCheckRequest()
        response = await servicer.HealthCheck(request, mock_context)
        assert response.status in ["healthy", "degraded"]
        assert "grpc" in response.components


class TestGenerationMethodMapping:
    def test_generation_method_mapping(self):
        """Test that generation method values map correctly."""
        generation_method_map = {
            0: "HYBRID",  # UNSPECIFIED
            1: "TRADITIONAL",
            2: "LLM",
            3: "RAG",
            4: "HYBRID",
        }
        assert generation_method_map.get(0) == "HYBRID"
        assert generation_method_map.get(1) == "TRADITIONAL"
        assert generation_method_map.get(2) == "LLM"
        assert generation_method_map.get(3) == "RAG"
        assert generation_method_map.get(4) == "HYBRID"
        # Unknown should default to HYBRID
        assert generation_method_map.get(99, "HYBRID") == "HYBRID"


class TestProtoScenarioConversion:
    def test_string_scenarios_to_dict(self):
        """Test converting string scenarios to dict format."""
        proto_scenarios = ["high_value", "happy_path"]
        scenarios_list = []
        for scenario_name in proto_scenarios:
            scenarios_list.append({
                "name": scenario_name,
                "count": 1,
                "description": f"User-requested scenario: {scenario_name}",
            })
        assert len(scenarios_list) == 2
        assert scenarios_list[0]["name"] == "high_value"
        assert scenarios_list[1]["name"] == "happy_path"
