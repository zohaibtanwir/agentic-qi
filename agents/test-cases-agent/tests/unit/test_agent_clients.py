"""Unit tests for agent clients."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import grpc
import pytest

from test_cases_agent.clients import (
    DomainAgentClient,
    TestDataAgentClient,
    get_domain_agent_client,
    get_test_data_agent_client,
)
from test_cases_agent.proto import ecommerce_domain_pb2, test_data_pb2


class TestDomainAgentClient:
    """Test Domain Agent client."""

    @pytest.fixture
    async def client(self):
        """Create Domain Agent client."""
        return DomainAgentClient(host="localhost", port=9002)

    @pytest.fixture
    def mock_stub(self):
        """Create mock gRPC stub."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.host == "localhost"
        assert client.port == 9002
        assert client.address == "localhost:9002"
        assert client._channel is None
        assert client._stub is None

    @pytest.mark.asyncio
    async def test_connect(self, client, mock_stub):
        """Test connecting to Domain Agent."""
        with patch("grpc.aio.insecure_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch.object(client, "health_check", new_callable=AsyncMock) as mock_health:
                mock_health.return_value = True

                await client.connect()

                mock_channel.assert_called_once()
                mock_health.assert_called_once()
                assert client._channel is not None

    @pytest.mark.asyncio
    async def test_health_check(self, client, mock_stub):
        """Test health check."""
        client._stub = mock_stub
        mock_response = ecommerce_domain_pb2.HealthCheckResponse(
            status="SERVING"
        )
        mock_stub.HealthCheck.return_value = mock_response

        result = await client.health_check()

        assert result is True
        mock_stub.HealthCheck.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_domain_context(self, client, mock_stub):
        """Test getting domain context."""
        client._stub = mock_stub

        # Create mock business rules
        mock_rule1 = ecommerce_domain_pb2.BusinessRule(
            id="BR001",
            name="Rule 1",
            description="Rule 1 description",
        )
        mock_rule2 = ecommerce_domain_pb2.BusinessRule(
            id="BR002",
            name="Rule 2",
            description="Rule 2 description",
        )

        mock_response = ecommerce_domain_pb2.DomainContextResponse(
            request_id="test-123",
            context="Order entity",
            rules=[mock_rule1, mock_rule2],
            edge_cases=["Edge case 1"],
        )
        mock_stub.GetDomainContext.return_value = mock_response

        result = await client.get_domain_context(
            entity_type="order",
            scenario="checkout",
        )

        assert result["entity_type"] == "order"
        assert result["description"] == "Order entity"
        assert "Rule 1 description" in result["business_rules"]
        assert "Rule 2 description" in result["business_rules"]
        assert "Edge case 1" in result["edge_cases"]

    @pytest.mark.asyncio
    async def test_get_entity(self, client, mock_stub):
        """Test getting entity information."""
        client._stub = mock_stub

        # Create mock business rule
        mock_rule = ecommerce_domain_pb2.BusinessRule(
            id="BR001",
            name="Stock Rule",
            description="Stock must be positive",
        )

        # Create mock entity
        mock_entity = ecommerce_domain_pb2.Entity(
            name="product",
            description="Product entity",
            rules=[mock_rule],
        )

        mock_response = ecommerce_domain_pb2.EntityResponse(
            entity=mock_entity
        )
        mock_stub.GetEntity.return_value = mock_response

        result = await client.get_entity("product")

        assert result["entity_type"] == "product"
        assert result["description"] == "Product entity"
        assert "Stock must be positive" in result["business_rules"]

    @pytest.mark.asyncio
    async def test_get_workflow(self, client, mock_stub):
        """Test getting workflow information."""
        client._stub = mock_stub

        # Create mock workflow
        mock_workflow = ecommerce_domain_pb2.Workflow(
            name="checkout",
            description="Checkout workflow",
            involved_entities=["cart", "order", "payment"],
        )

        mock_response = ecommerce_domain_pb2.WorkflowResponse(
            workflow=mock_workflow
        )
        mock_stub.GetWorkflow.return_value = mock_response

        result = await client.get_workflow("checkout")

        assert result["workflow_name"] == "checkout"
        assert result["description"] == "Checkout workflow"
        assert "cart" in result["entities_involved"]

    @pytest.mark.asyncio
    async def test_get_edge_cases(self, client, mock_stub):
        """Test getting edge cases."""
        client._stub = mock_stub

        # Create mock edge case
        mock_edge_case = ecommerce_domain_pb2.EdgeCase(
            id="EC001",
            entity="order",
            description="Empty cart checkout",
            severity="HIGH",
        )

        mock_response = ecommerce_domain_pb2.EdgeCasesResponse(
            edge_cases=[mock_edge_case]
        )
        mock_stub.GetEdgeCases.return_value = mock_response

        result = await client.get_edge_cases(entity_type="order")

        assert len(result) == 1
        assert result[0]["id"] == "EC001"
        assert result[0]["entity_type"] == "order"
        assert result[0]["severity"] == "HIGH"

    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test disconnecting from Domain Agent."""
        mock_channel = AsyncMock()
        client._channel = mock_channel
        client._stub = MagicMock()

        await client.disconnect()

        mock_channel.close.assert_called_once()
        assert client._channel is None
        assert client._stub is None


class TestTestDataAgentClient:
    """Test Test Data Agent client."""

    @pytest.fixture
    async def client(self):
        """Create Test Data Agent client."""
        return TestDataAgentClient(host="localhost", port=9001)

    @pytest.fixture
    def mock_stub(self):
        """Create mock gRPC stub."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.host == "localhost"
        assert client.port == 9001
        assert client.address == "localhost:9001"
        assert client._channel is None
        assert client._stub is None

    @pytest.mark.asyncio
    async def test_connect(self, client, mock_stub):
        """Test connecting to Test Data Agent."""
        with patch("grpc.aio.insecure_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch.object(client, "health_check", new_callable=AsyncMock) as mock_health:
                mock_health.return_value = True

                await client.connect()

                mock_channel.assert_called_once()
                mock_health.assert_called_once()
                assert client._channel is not None

    @pytest.mark.asyncio
    async def test_generate_data(self, client, mock_stub):
        """Test generating data."""
        client._stub = mock_stub

        mock_metadata = test_data_pb2.GenerationMetadata(
            generation_path="llm",
            llm_tokens_used=100,
            coherence_score=0.95,
        )

        mock_response = test_data_pb2.GenerateResponse(
            success=True,
            data='[{"id": 1, "name": "Test"}]',
            record_count=1,
            metadata=mock_metadata,
        )
        mock_stub.GenerateData.return_value = mock_response

        result = await client.generate_data(
            entity="customer",
            count=1,
            context="Test context",
        )

        assert result["success"] is True
        assert result["record_count"] == 1
        assert result["data"] == [{"id": 1, "name": "Test"}]
        assert result["metadata"]["generation_path"] == "llm"
        assert result["metadata"]["tokens_used"] == 100

    @pytest.mark.asyncio
    async def test_get_schemas(self, client, mock_stub):
        """Test getting schemas."""
        client._stub = mock_stub

        mock_field = test_data_pb2.SchemaField(
            name="id",
            type="integer",
            required=True,
            description="Unique identifier",
        )

        mock_schema = test_data_pb2.Schema(
            name="CustomerSchema",
            domain="customer",
            description="Customer schema",
            fields=[mock_field],
        )

        mock_response = test_data_pb2.GetSchemasResponse(
            schemas=[mock_schema]
        )
        mock_stub.GetSchemas.return_value = mock_response

        result = await client.get_schemas(entity_type="customer")

        assert len(result) == 1
        assert result[0]["name"] == "CustomerSchema"
        assert result[0]["entity_type"] == "customer"
        assert len(result[0]["fields"]) == 1
        assert result[0]["fields"][0]["name"] == "id"
        assert result[0]["fields"][0]["required"] is True

    @pytest.mark.asyncio
    async def test_validate_data(self, client, mock_stub):
        """Test validating data - not yet implemented."""
        client._stub = mock_stub

        with pytest.raises(NotImplementedError, match="ValidateData RPC is not implemented"):
            await client.validate_data(
                data='{"id": 1, "name": "Test"}',
                schema_name="CustomerSchema",
            )

    @pytest.mark.asyncio
    async def test_transform_data(self, client, mock_stub):
        """Test transforming data - not yet implemented."""
        client._stub = mock_stub

        with pytest.raises(NotImplementedError, match="TransformData RPC is not implemented"):
            await client.transform_data(
                data='{"id": 1, "name": "Test"}',
                source_format="json",
                target_format="csv",
            )

    @pytest.mark.asyncio
    async def test_error_handling(self, client, mock_stub):
        """Test error handling."""
        from tenacity import RetryError

        client._stub = mock_stub

        # Create a custom RpcError subclass for testing
        class TestRpcError(grpc.RpcError):
            def code(self):
                return "INTERNAL"

            def details(self):
                return "Internal error"

        mock_stub.GenerateData.side_effect = TestRpcError()

        # The @retry decorator will retry 3 times then raise RetryError
        with pytest.raises(RetryError):
            await client.generate_data("customer", 1)


def test_singleton_domain_client():
    """Test singleton Domain Agent client."""
    client1 = get_domain_agent_client()
    client2 = get_domain_agent_client()
    assert client1 is client2


def test_singleton_test_data_client():
    """Test singleton Test Data Agent client."""
    client1 = get_test_data_agent_client()
    client2 = get_test_data_agent_client()
    assert client1 is client2