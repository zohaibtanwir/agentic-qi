"""Tests for Knowledge API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ecommerce_agent.server.knowledge_api import (
    router,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeSearchResponse,
    KnowledgeStatsResponse,
    search_knowledge,
    get_knowledge_stats,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def app():
    """Create a test FastAPI app with the router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_weaviate_client():
    """Create a mock Weaviate client."""
    mock_client = MagicMock()
    mock_client.is_connected.return_value = True
    return mock_client


# =============================================================================
# Tests for Pydantic Models
# =============================================================================

class TestKnowledgeSearchRequest:
    """Tests for KnowledgeSearchRequest model."""

    def test_create_request_with_defaults(self):
        """Test creating a request with default values."""
        request = KnowledgeSearchRequest(query="test query")
        assert request.query == "test query"
        assert request.limit == 10
        assert request.collections is None

    def test_create_request_with_custom_values(self):
        """Test creating a request with custom values."""
        request = KnowledgeSearchRequest(
            query="cart items",
            limit=5,
            collections=["EcommerceRule", "EcommerceEdgeCase"]
        )
        assert request.query == "cart items"
        assert request.limit == 5
        assert len(request.collections) == 2

    def test_request_validation(self):
        """Test that query is required."""
        with pytest.raises(Exception):
            KnowledgeSearchRequest()


class TestKnowledgeSearchResult:
    """Tests for KnowledgeSearchResult model."""

    def test_create_result_minimal(self):
        """Test creating a result with minimal fields."""
        result = KnowledgeSearchResult(
            title="Test Title",
            type="Business Rule",
            content="Test content",
            relevance=0.95
        )
        assert result.title == "Test Title"
        assert result.type == "Business Rule"
        assert result.content == "Test content"
        assert result.relevance == 0.95
        assert result.metadata == {}

    def test_create_result_with_metadata(self):
        """Test creating a result with metadata."""
        result = KnowledgeSearchResult(
            title="Test Title",
            type="Edge Case",
            content="Test content",
            relevance=0.85,
            metadata={"collection": "EcommerceEdgeCase", "id": "123"}
        )
        assert result.metadata["collection"] == "EcommerceEdgeCase"
        assert result.metadata["id"] == "123"


class TestKnowledgeSearchResponse:
    """Tests for KnowledgeSearchResponse model."""

    def test_create_response(self):
        """Test creating a response."""
        results = [
            KnowledgeSearchResult(
                title="Result 1",
                type="Business Rule",
                content="Content 1",
                relevance=0.9
            ),
            KnowledgeSearchResult(
                title="Result 2",
                type="Edge Case",
                content="Content 2",
                relevance=0.8
            ),
        ]
        response = KnowledgeSearchResponse(
            query="test",
            results=results,
            total_results=2
        )
        assert response.query == "test"
        assert len(response.results) == 2
        assert response.total_results == 2

    def test_create_empty_response(self):
        """Test creating an empty response."""
        response = KnowledgeSearchResponse(
            query="no results",
            results=[],
            total_results=0
        )
        assert len(response.results) == 0
        assert response.total_results == 0


class TestKnowledgeStatsResponse:
    """Tests for KnowledgeStatsResponse model."""

    def test_create_stats(self):
        """Test creating stats response."""
        stats = KnowledgeStatsResponse(
            collections_count=4,
            documents_count=31,
            edge_cases_count=10,
            business_rules_count=10,
            connected=True
        )
        assert stats.collections_count == 4
        assert stats.documents_count == 31
        assert stats.edge_cases_count == 10
        assert stats.business_rules_count == 10
        assert stats.connected is True

    def test_create_disconnected_stats(self):
        """Test creating stats when disconnected."""
        stats = KnowledgeStatsResponse(
            collections_count=0,
            documents_count=0,
            edge_cases_count=0,
            business_rules_count=0,
            connected=False
        )
        assert stats.connected is False


# =============================================================================
# Tests for Search Knowledge Endpoint
# =============================================================================

class TestSearchKnowledgeEndpoint:
    """Tests for the /api/knowledge/search endpoint."""

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_success(self, mock_get_client, client):
        """Test successful knowledge search."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "rule_id": "BR001",
                "name": "Cart Minimum Items",
                "description": "Cart must have at least 1 item",
                "_additional": {"score": 0.95, "id": "uuid-123"}
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "cart items"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "cart items"
        assert len(data["results"]) >= 1
        assert data["total_results"] >= 1

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_with_custom_limit(self, mock_get_client, client):
        """Test search with custom limit."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "limit": 5}
        )

        assert response.status_code == 200
        # Verify the limit was passed to the search
        mock_client.search_bm25.assert_called()

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_with_custom_collections(self, mock_get_client, client):
        """Test search with specific collections."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={
                "query": "test",
                "collections": ["EcommerceRule"]
            }
        )

        assert response.status_code == 200
        # Should only search the specified collection
        mock_client.search_bm25.assert_called_once_with(
            class_name="EcommerceRule",
            query="test",
            limit=10
        )

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_not_connected(self, mock_get_client, client):
        """Test search when Weaviate is not connected."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = False
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test"}
        )

        assert response.status_code == 503
        assert "not available" in response.json()["detail"]

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_handles_collection_error(self, mock_get_client, client):
        """Test search handles errors from individual collections gracefully."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        # First collection raises an error, second returns results
        mock_client.search_bm25.side_effect = [
            Exception("Collection error"),
            [{"rule_id": "BR001", "name": "Test", "description": "Test", "_additional": {"score": 0.9}}],
            [],
            []
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test"}
        )

        assert response.status_code == 200
        # Should still return results from successful collections
        data = response.json()
        assert data["query"] == "test"

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_result_types(self, mock_get_client, client):
        """Test that different collection types are labeled correctly."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True

        def search_side_effect(class_name, query, limit):
            if class_name == "EcommerceRule":
                return [{"rule_id": "BR001", "name": "Rule", "description": "Desc", "_additional": {"score": 0.9}}]
            elif class_name == "EcommerceEdgeCase":
                return [{"edge_case_id": "EC001", "name": "Case", "description": "Desc", "_additional": {"score": 0.8}}]
            elif class_name == "EcommerceEntity":
                return [{"entity_name": "Cart", "description": "Desc", "_additional": {"score": 0.7}}]
            elif class_name == "EcommerceWorkflow":
                return [{"workflow_name": "Checkout", "description": "Desc", "_additional": {"score": 0.6}}]
            return []

        mock_client.search_bm25.side_effect = search_side_effect
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test"}
        )

        assert response.status_code == 200
        data = response.json()
        types = [r["type"] for r in data["results"]]
        assert "Business Rule" in types
        assert "Edge Case" in types
        assert "Entity" in types
        assert "Workflow" in types

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_results_sorted_by_relevance(self, mock_get_client, client):
        """Test that results are sorted by relevance score."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True

        def search_side_effect(class_name, query, limit):
            if class_name == "EcommerceRule":
                return [{"rule_id": "BR001", "name": "Low", "description": "Low score", "_additional": {"score": 0.3}}]
            elif class_name == "EcommerceEdgeCase":
                return [{"edge_case_id": "EC001", "name": "High", "description": "High score", "_additional": {"score": 0.9}}]
            return []

        mock_client.search_bm25.side_effect = search_side_effect
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "collections": ["EcommerceRule", "EcommerceEdgeCase"]}
        )

        assert response.status_code == 200
        data = response.json()
        # First result should have higher relevance
        if len(data["results"]) >= 2:
            assert data["results"][0]["relevance"] >= data["results"][1]["relevance"]

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_total_limit_applied(self, mock_get_client, client):
        """Test that total results are limited."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True

        # Return many results from each collection
        mock_client.search_bm25.return_value = [
            {"rule_id": f"BR{i:03d}", "name": f"Rule {i}", "description": "Desc", "_additional": {"score": 0.5}}
            for i in range(20)
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "limit": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] <= 5

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_search_general_exception(self, mock_get_client, client):
        """Test search handles general exceptions."""
        mock_get_client.side_effect = Exception("Connection failed")

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test"}
        )

        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()


class TestSearchResultFormatting:
    """Tests for search result formatting."""

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_rule_formatting(self, mock_get_client, client):
        """Test business rule result formatting."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "rule_id": "BR001",
                "name": "Cart Minimum",
                "description": "Cart must have items",
                "_additional": {"score": 0.9, "id": "uuid-1"}
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "cart", "collections": ["EcommerceRule"]}
        )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert "BR001" in result["title"]
        assert "Cart Minimum" in result["title"]
        assert result["type"] == "Business Rule"
        assert result["content"] == "Cart must have items"

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_edge_case_formatting(self, mock_get_client, client):
        """Test edge case result formatting."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "edge_case_id": "EC001",
                "name": "Concurrent Updates",
                "description": "Handle concurrent cart updates",
                "_additional": {"score": 0.85, "id": "uuid-2"}
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "concurrent", "collections": ["EcommerceEdgeCase"]}
        )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert "EC001" in result["title"]
        assert "Concurrent Updates" in result["title"]
        assert result["type"] == "Edge Case"

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_entity_formatting(self, mock_get_client, client):
        """Test entity result formatting."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "entity_name": "Shopping Cart",
                "description": "Shopping cart entity",
                "_additional": {"score": 0.8, "id": "uuid-3"}
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "cart", "collections": ["EcommerceEntity"]}
        )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert result["title"] == "Shopping Cart"
        assert result["type"] == "Entity"

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_workflow_formatting(self, mock_get_client, client):
        """Test workflow result formatting."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "workflow_name": "Checkout Flow",
                "description": "Checkout process workflow",
                "_additional": {"score": 0.75, "id": "uuid-4"}
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "checkout", "collections": ["EcommerceWorkflow"]}
        )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert result["title"] == "Checkout Flow"
        assert result["type"] == "Workflow"

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_missing_fields_use_defaults(self, mock_get_client, client):
        """Test handling of missing fields in results."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "_additional": {"score": 0.5}
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "collections": ["EcommerceRule"]}
        )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert "Unknown" in result["title"]

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_default_score(self, mock_get_client, client):
        """Test default score when not provided."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = [
            {
                "rule_id": "BR001",
                "name": "Test Rule",
                "description": "Description"
            }
        ]
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "collections": ["EcommerceRule"]}
        )

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert result["relevance"] == 0.5  # Default score


# =============================================================================
# Tests for Knowledge Stats Endpoint
# =============================================================================

class TestKnowledgeStatsEndpoint:
    """Tests for the /api/knowledge/stats endpoint."""

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_stats_success(self, mock_get_client, client):
        """Test successful stats retrieval."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.side_effect = [
            [{"id": i} for i in range(10)],  # Rules
            [{"id": i} for i in range(10)],  # Edge cases
        ]
        mock_client.get_schema.return_value = {
            "classes": [
                {"class": "EcommerceRule"},
                {"class": "EcommerceEdgeCase"},
                {"class": "EcommerceEntity"},
                {"class": "EcommerceWorkflow"},
            ]
        }
        mock_get_client.return_value = mock_client

        response = client.get("/api/knowledge/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["collections_count"] == 4
        assert data["business_rules_count"] == 10
        assert data["edge_cases_count"] == 10
        assert data["documents_count"] == 20

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_stats_not_connected(self, mock_get_client, client):
        """Test stats when Weaviate is not connected."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = False
        mock_get_client.return_value = mock_client

        response = client.get("/api/knowledge/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False
        assert data["collections_count"] == 0
        assert data["documents_count"] == 0

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_stats_handles_search_error(self, mock_get_client, client):
        """Test stats handles search errors gracefully."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.side_effect = Exception("Search failed")
        mock_client.get_schema.return_value = {"classes": []}
        mock_get_client.return_value = mock_client

        response = client.get("/api/knowledge/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        # Counts should be 0 due to error
        assert data["business_rules_count"] == 0

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_stats_handles_schema_error(self, mock_get_client, client):
        """Test stats handles schema errors gracefully."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_client.get_schema.side_effect = Exception("Schema error")
        mock_get_client.return_value = mock_client

        response = client.get("/api/knowledge/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_stats_general_exception(self, mock_get_client, client):
        """Test stats handles general exceptions."""
        mock_get_client.side_effect = Exception("Connection failed")

        response = client.get("/api/knowledge/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False


# =============================================================================
# Tests for Router Configuration
# =============================================================================

class TestRouterConfiguration:
    """Tests for API router configuration."""

    def test_router_prefix(self):
        """Test router has correct prefix."""
        assert router.prefix == "/api/knowledge"

    def test_router_tags(self):
        """Test router has correct tags."""
        assert "knowledge" in router.tags

    def test_search_endpoint_exists(self, app, client):
        """Test search endpoint is registered."""
        # Just check that the endpoint responds
        response = client.post("/api/knowledge/search", json={"query": "test"})
        # Will fail due to Weaviate not connected, but endpoint exists
        assert response.status_code in [200, 500, 503]

    def test_stats_endpoint_exists(self, app, client):
        """Test stats endpoint is registered."""
        response = client.get("/api/knowledge/stats")
        assert response.status_code in [200, 500]


# =============================================================================
# Async Function Tests
# =============================================================================

class TestAsyncFunctions:
    """Tests for async function behavior."""

    @pytest.mark.asyncio
    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    async def test_search_knowledge_async(self, mock_get_client):
        """Test search_knowledge can be awaited."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        request = KnowledgeSearchRequest(query="test")
        response = await search_knowledge(request)

        assert isinstance(response, KnowledgeSearchResponse)
        assert response.query == "test"

    @pytest.mark.asyncio
    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    async def test_get_knowledge_stats_async(self, mock_get_client):
        """Test get_knowledge_stats can be awaited."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_client.get_schema.return_value = {"classes": []}
        mock_get_client.return_value = mock_client

        response = await get_knowledge_stats()

        assert isinstance(response, KnowledgeStatsResponse)
        assert response.connected is True


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_empty_query(self, mock_get_client, client):
        """Test handling of empty query string."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": ""}
        )

        # Empty query might be valid or rejected
        assert response.status_code in [200, 422]

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_very_long_query(self, mock_get_client, client):
        """Test handling of very long query string."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        long_query = "test " * 1000
        response = client.post(
            "/api/knowledge/search",
            json={"query": long_query}
        )

        assert response.status_code in [200, 422]

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_special_characters_in_query(self, mock_get_client, client):
        """Test handling of special characters in query."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test & query | special \"characters\""}
        )

        assert response.status_code == 200

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_limit_zero(self, mock_get_client, client):
        """Test handling of zero limit."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "limit": 0}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_negative_limit(self, mock_get_client, client):
        """Test handling of negative limit."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "limit": -1}
        )

        # May be rejected by validation or handled
        assert response.status_code in [200, 422]

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_invalid_collection_name(self, mock_get_client, client):
        """Test handling of invalid collection names."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.side_effect = Exception("Collection not found")
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "collections": ["InvalidCollection"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0

    @patch("ecommerce_agent.server.knowledge_api.get_weaviate_client")
    def test_empty_collections_list(self, mock_get_client, client):
        """Test handling of empty collections list falls back to defaults."""
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/knowledge/search",
            json={"query": "test", "collections": []}
        )

        assert response.status_code == 200
        # Empty collections falls back to default collections (4 calls)
        assert mock_client.search_bm25.call_count == 4
