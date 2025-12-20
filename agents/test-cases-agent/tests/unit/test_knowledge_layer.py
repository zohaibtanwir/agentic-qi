"""Unit tests for knowledge layer."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from test_cases_agent.knowledge import (
    KnowledgeRetriever,
    WeaviateClient,
    get_knowledge_retriever,
    get_weaviate_client,
)


class TestWeaviateClient:
    """Test Weaviate client."""

    @pytest.fixture
    async def client(self):
        """Create Weaviate client."""
        return WeaviateClient(url="http://localhost:8084")

    @pytest.fixture
    def mock_weaviate(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.url == "http://localhost:8084"
        assert client._client is None
        assert client.timeout == 30

    @pytest.mark.asyncio
    async def test_connect(self, client, mock_weaviate):
        """Test connecting to Weaviate."""
        with patch("weaviate.Client") as mock_client_class:
            mock_client_class.return_value = mock_weaviate
            mock_weaviate.is_ready.return_value = True

            with patch.object(client, "_ensure_schemas", new_callable=AsyncMock):
                await client.connect()

            mock_client_class.assert_called_once()
            assert client._client == mock_weaviate

    @pytest.mark.asyncio
    async def test_store_test_case(self, client, mock_weaviate):
        """Test storing a test case."""
        client._client = mock_weaviate
        mock_weaviate.data_object.create.return_value = "test-uuid-123"

        test_case = {
            "id": "TC001",
            "title": "Test login",
            "description": "Test user login",
            "test_type": "functional",
            "priority": "high",
            "steps": [{"step": 1, "action": "Enter credentials"}],
            "tags": ["login", "auth"],
        }

        result = await client.store_test_case(test_case)

        assert result == "test-uuid-123"
        mock_weaviate.data_object.create.assert_called_once()
        call_args = mock_weaviate.data_object.create.call_args
        assert call_args.kwargs["class_name"] == "TestCases"
        assert call_args.kwargs["data_object"]["test_id"] == "TC001"
        assert call_args.kwargs["data_object"]["title"] == "Test login"

    @pytest.mark.asyncio
    async def test_search_test_cases(self, client, mock_weaviate):
        """Test searching test cases."""
        client._client = mock_weaviate

        # Mock query builder chain
        mock_query = MagicMock()
        mock_weaviate.query.get.return_value = mock_query
        mock_query.with_near_text.return_value = mock_query
        mock_query.with_limit.return_value = mock_query
        mock_query.do.return_value = {
            "data": {
                "Get": {
                    "TestCases": [
                        {
                            "test_id": "TC001",
                            "title": "Test login",
                            "description": "Test user login",
                            "test_type": "functional",
                            "priority": "high",
                            "tags": ["login"],
                        }
                    ]
                }
            }
        }

        results = await client.search_test_cases(
            query="login test",
            limit=5,
        )

        assert len(results) == 1
        assert results[0]["test_id"] == "TC001"
        assert results[0]["title"] == "Test login"
        mock_query.with_near_text.assert_called_with({"concepts": ["login test"]})
        mock_query.with_limit.assert_called_with(5)

    @pytest.mark.asyncio
    async def test_search_patterns(self, client, mock_weaviate):
        """Test searching patterns."""
        client._client = mock_weaviate

        # Mock query builder chain
        mock_query = MagicMock()
        mock_weaviate.query.get.return_value = mock_query
        mock_query.with_near_text.return_value = mock_query
        mock_query.with_limit.return_value = mock_query
        mock_query.do.return_value = {
            "data": {
                "Get": {
                    "TestPatterns": [
                        {
                            "pattern_id": "PAT001",
                            "name": "Login Pattern",
                            "description": "Standard login test pattern",
                            "category": "authentication",
                            "usage_count": 10,
                            "success_rate": 0.9,
                        }
                    ]
                }
            }
        }

        results = await client.search_patterns(
            query="login pattern",
            pattern_type="test",
            limit=3,
        )

        assert len(results) == 1
        assert results[0]["pattern_id"] == "PAT001"
        assert results[0]["name"] == "Login Pattern"
        assert results[0]["success_rate"] == 0.9

    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test disconnecting from Weaviate."""
        client._client = MagicMock()

        await client.disconnect()

        assert client._client is None


class TestKnowledgeRetriever:
    """Test Knowledge Retriever."""

    @pytest.fixture
    async def retriever(self):
        """Create Knowledge Retriever."""
        mock_weaviate = AsyncMock()
        return KnowledgeRetriever(weaviate_client=mock_weaviate)

    @pytest.mark.asyncio
    async def test_find_similar_test_cases(self, retriever):
        """Test finding similar test cases."""
        mock_test_cases = [
            {
                "test_id": "TC001",
                "title": "Test login",
                "coverage_score": 0.8,
            },
            {
                "test_id": "TC002",
                "title": "Test logout",
                "coverage_score": 0.7,
            },
        ]

        retriever.weaviate.search_test_cases = AsyncMock(return_value=mock_test_cases)

        results = await retriever.find_similar_test_cases(
            context="User authentication flow",
            entity_type="user",
            test_type="functional",
            limit=5,
        )

        assert len(results) == 2
        assert results[0]["test_id"] == "TC001"
        retriever.weaviate.search_test_cases.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_test_patterns(self, retriever):
        """Test getting test patterns."""
        mock_patterns = [
            {
                "pattern_id": "PAT001",
                "name": "Login Pattern",
                "success_rate": 0.9,
            },
            {
                "pattern_id": "PAT002",
                "name": "Validation Pattern",
                "success_rate": 0.8,
            },
        ]

        retriever.weaviate.search_patterns = AsyncMock(return_value=mock_patterns)

        results = await retriever.get_test_patterns(
            requirement="User must be able to login",
            domain="authentication",
            limit=3,
        )

        assert len(results) == 2
        # Should be sorted by success rate
        assert results[0]["success_rate"] == 0.9
        assert results[1]["success_rate"] == 0.8

    @pytest.mark.asyncio
    async def test_get_coverage_strategy(self, retriever):
        """Test getting coverage strategy."""
        mock_pattern = {
            "coverage_strategy": "comprehensive",
            "test_types_required": ["functional", "edge_case"],
            "minimum_test_count": 5,
            "priority_distribution": {"high": 40, "medium": 40, "low": 20},
            "edge_cases": ["null_input", "special_chars"],
            "validation_rules": ["required_fields", "data_types"],
        }

        retriever.weaviate.search_patterns = AsyncMock(return_value=[mock_pattern])

        result = await retriever.get_coverage_strategy(
            requirement_type="user_story",
            complexity="medium",
        )

        assert result["strategy"] == "comprehensive"
        assert "functional" in result["test_types"]
        assert result["min_tests"] == 5
        assert "null_input" in result["edge_cases"]

    @pytest.mark.asyncio
    async def test_get_coverage_strategy_default(self, retriever):
        """Test getting default coverage strategy."""
        retriever.weaviate.search_patterns = AsyncMock(return_value=[])

        result = await retriever.get_coverage_strategy(
            requirement_type="user_story",
            complexity="low",
        )

        # Should return default strategy for low complexity
        assert result["strategy"] == "basic"
        assert result["test_types"] == ["functional"]
        assert result["min_tests"] == 2

    @pytest.mark.asyncio
    async def test_learn_from_test_case(self, retriever):
        """Test learning from test case."""
        retriever.weaviate.store_test_case = AsyncMock(return_value="test-uuid")
        retriever.weaviate.update_pattern_usage = AsyncMock()

        test_case = {
            "id": "TC001",
            "title": "Test login",
            "pattern_id": "PAT001",
        }

        feedback = {
            "coverage_score": 0.9,
            "complexity_score": 0.5,
            "success": True,
        }

        result = await retriever.learn_from_test_case(test_case, feedback)

        assert result is True
        retriever.weaviate.store_test_case.assert_called_once()
        stored_case = retriever.weaviate.store_test_case.call_args[0][0]
        assert stored_case["coverage_score"] == 0.9
        assert stored_case["complexity_score"] == 0.5

        # Should update pattern usage
        retriever.weaviate.update_pattern_usage.assert_called_with(
            pattern_id="PAT001",
            pattern_type="test",
            success=True,
        )

    @pytest.mark.asyncio
    async def test_suggest_edge_cases(self, retriever):
        """Test suggesting edge cases."""
        mock_test_cases = [
            {
                "test_id": "TC001",
                "domain_context": {
                    "edge_cases": ["empty_input", "null_values"],
                },
            },
            {
                "test_id": "TC002",
                "domain_context": {
                    "edge_cases": ["special_chars", "null_values"],
                },
            },
        ]

        retriever.find_similar_test_cases = AsyncMock(return_value=mock_test_cases)

        results = await retriever.suggest_edge_cases(
            entity_type="order",
            context="Order checkout",
            limit=5,
        )

        assert len(results) > 0
        # Should include both extracted and common edge cases
        retriever.find_similar_test_cases.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_test_gaps(self, retriever):
        """Test analyzing test gaps."""
        requirements = ["REQ001", "REQ002", "REQ003"]
        existing_tests = [
            {
                "id": "TC001",
                "requirements": ["REQ001"],
                "test_type": "functional",
            },
            {
                "id": "TC002",
                "requirements": ["REQ002"],
                "test_type": "functional",
            },
        ]

        mock_patterns = [
            {
                "name": "Pattern for REQ003",
                "template": {},
            }
        ]

        retriever.get_test_patterns = AsyncMock(return_value=mock_patterns)

        result = await retriever.analyze_test_gaps(requirements, existing_tests)

        assert "REQ003" in result["uncovered_requirements"]
        assert result["coverage_percentage"] == pytest.approx(66.67, 0.01)
        assert "edge_case" in result["missing_test_types"]
        assert len(result["suggested_tests"]) > 0


def test_singleton_weaviate_client():
    """Test singleton Weaviate client."""
    client1 = get_weaviate_client()
    client2 = get_weaviate_client()
    assert client1 is client2


def test_singleton_knowledge_retriever():
    """Test singleton Knowledge Retriever."""
    retriever1 = get_knowledge_retriever()
    retriever2 = get_knowledge_retriever()
    assert retriever1 is retriever2