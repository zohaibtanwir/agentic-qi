"""Tests for knowledge retriever."""

import pytest
from unittest.mock import MagicMock, patch
import json

from ecommerce_agent.knowledge.retriever import (
    KnowledgeRetriever,
    RetrievalResult,
    get_retriever,
)


class TestRetrievalResult:
    """Tests for RetrievalResult dataclass."""

    def test_retrieval_result_creation(self):
        """Test creating a RetrievalResult."""
        result = RetrievalResult(
            item_type="entity",
            title="Test Entity",
            content="Test content",
            relevance_score=0.85,
            metadata={"key": "value"},
        )

        assert result.item_type == "entity"
        assert result.title == "Test Entity"
        assert result.content == "Test content"
        assert result.relevance_score == 0.85
        assert result.metadata == {"key": "value"}


class TestKnowledgeRetrieverSearch:
    """Tests for KnowledgeRetriever search functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.fixture
    def retriever(self, mock_client):
        """Create retriever with mocked client."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client', return_value=mock_client):
            return KnowledgeRetriever()

    def test_search_all_categories(self, retriever, mock_client):
        """Test search across all categories."""
        mock_client.search_bm25.return_value = [
            {
                "entity_name": "Order",
                "description": "Order entity",
                "_additional": {"score": 0.9},
            }
        ]

        results = retriever.search("order", max_results=10)

        # Should search all 4 collections
        assert mock_client.search_bm25.call_count == 4
        called_collections = [
            call[1]["class_name"] for call in mock_client.search_bm25.call_args_list
        ]
        assert "EcommerceEntity" in called_collections
        assert "EcommerceWorkflow" in called_collections
        assert "EcommerceRule" in called_collections
        assert "EcommerceEdgeCase" in called_collections

    def test_search_specific_categories(self, retriever, mock_client):
        """Test search with specific categories."""
        mock_client.search_bm25.return_value = []

        retriever.search("order", categories=["entities", "rules"], max_results=5)

        # Should only search specified collections
        assert mock_client.search_bm25.call_count == 2
        called_collections = [
            call[1]["class_name"] for call in mock_client.search_bm25.call_args_list
        ]
        assert "EcommerceEntity" in called_collections
        assert "EcommerceRule" in called_collections
        assert "EcommerceWorkflow" not in called_collections
        assert "EcommerceEdgeCase" not in called_collections

    def test_search_entities_only(self, retriever, mock_client):
        """Test search entities only."""
        mock_client.search_bm25.return_value = []

        retriever.search("cart", categories=["entities"])

        assert mock_client.search_bm25.call_count == 1
        assert mock_client.search_bm25.call_args[1]["class_name"] == "EcommerceEntity"

    def test_search_results_sorted_by_relevance(self, retriever, mock_client):
        """Test that results are sorted by relevance score."""
        # Mock returns different scores for different collections
        def mock_search(class_name, query, limit):
            if class_name == "EcommerceEntity":
                return [{
                    "entity_name": "Entity",
                    "description": "Desc",
                    "_additional": {"score": 0.5}
                }]
            elif class_name == "EcommerceRule":
                return [{
                    "rule_id": "R1",
                    "name": "Rule",
                    "description": "Desc",
                    "_additional": {"score": 0.9}
                }]
            return []

        mock_client.search_bm25.side_effect = mock_search

        results = retriever.search("test", max_results=10)

        # Higher score should be first
        assert len(results) >= 1
        if len(results) >= 2:
            assert results[0].relevance_score >= results[1].relevance_score

    def test_search_respects_max_results(self, retriever, mock_client):
        """Test that max_results is respected."""
        # Each collection returns 5 results
        mock_client.search_bm25.return_value = [
            {
                "entity_name": f"Entity{i}",
                "description": "Desc",
                "_additional": {"score": 0.5}
            }
            for i in range(5)
        ]

        results = retriever.search("test", max_results=3)

        assert len(results) == 3


class TestKnowledgeRetrieverParsing:
    """Tests for result parsing."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.fixture
    def retriever(self, mock_client):
        """Create retriever with mocked client."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client', return_value=mock_client):
            return KnowledgeRetriever()

    def test_parse_entity_result(self, retriever):
        """Test parsing entity result."""
        item = {
            "entity_name": "Order",
            "description": "Order entity description",
            "category": "transactional",
            "fields_json": json.dumps([{"name": "id", "type": "string"}]),
            "relationships_json": json.dumps([{"target": "Customer"}]),
            "business_rules": ["Rule1"],
            "edge_cases": ["Edge1"],
            "test_scenarios": ["Scenario1"],
            "_additional": {"score": 0.85},
        }

        result = retriever._parse_entity_result(item)

        assert result is not None
        assert result.item_type == "entity"
        assert result.title == "Order"
        assert result.content == "Order entity description"
        assert result.relevance_score == 0.85
        assert result.metadata["category"] == "transactional"
        assert len(result.metadata["fields"]) == 1

    def test_parse_entity_result_missing_fields(self, retriever):
        """Test parsing entity result with missing fields."""
        item = {
            "_additional": {"score": 0.5},
        }

        result = retriever._parse_entity_result(item)

        assert result is not None
        assert result.title == "Unknown Entity"
        assert result.content == ""

    def test_parse_entity_result_invalid_json(self, retriever):
        """Test parsing entity result with invalid JSON."""
        item = {
            "entity_name": "Test",
            "fields_json": "invalid json",
            "_additional": {"score": 0.5},
        }

        result = retriever._parse_entity_result(item)

        # Should return None due to JSON parse error
        assert result is None

    def test_parse_workflow_result(self, retriever):
        """Test parsing workflow result."""
        item = {
            "workflow_name": "Checkout Flow",
            "description": "Complete checkout process",
            "steps_json": json.dumps([{"name": "Add to Cart"}]),
            "involved_entities": ["Cart", "Order"],
            "business_rules": ["Rule1"],
            "edge_cases": ["Edge1"],
            "test_scenarios": ["Scenario1"],
            "_additional": {"score": 0.9},
        }

        result = retriever._parse_workflow_result(item)

        assert result is not None
        assert result.item_type == "workflow"
        assert result.title == "Checkout Flow"
        assert result.relevance_score == 0.9
        assert len(result.metadata["steps"]) == 1

    def test_parse_workflow_result_error(self, retriever):
        """Test parsing workflow result with error."""
        item = {
            "steps_json": "invalid",
            "_additional": {"score": 0.5},
        }

        result = retriever._parse_workflow_result(item)

        assert result is None

    def test_parse_rule_result(self, retriever):
        """Test parsing business rule result."""
        item = {
            "rule_id": "BR001",
            "name": "Minimum Order Value",
            "description": "Cart must have minimum $10",
            "entity": "Cart",
            "condition": "cart.total < 10",
            "constraint": "block checkout",
            "severity": "high",
            "validation_logic": "check total",
            "_additional": {"score": 0.95},
        }

        result = retriever._parse_rule_result(item)

        assert result is not None
        assert result.item_type == "business_rule"
        assert result.title == "BR001: Minimum Order Value"
        assert result.metadata["entity"] == "Cart"
        assert result.metadata["severity"] == "high"

    def test_parse_rule_result_missing_id(self, retriever):
        """Test parsing rule result without ID."""
        item = {
            "name": "Some Rule",
            "_additional": {"score": 0.5},
        }

        result = retriever._parse_rule_result(item)

        assert result is not None
        assert "Unknown" in result.title

    def test_parse_edge_case_result(self, retriever):
        """Test parsing edge case result."""
        item = {
            "edge_case_id": "EC001",
            "name": "Empty Cart Checkout",
            "description": "User tries to checkout with empty cart",
            "category": "validation",
            "entity": "Cart",
            "workflow": "Checkout",
            "test_approach": "Verify error message",
            "expected_behavior": "Show error",
            "severity": "medium",
            "example_data_json": json.dumps({"cart_items": []}),
            "_additional": {"score": 0.8},
        }

        result = retriever._parse_edge_case_result(item)

        assert result is not None
        assert result.item_type == "edge_case"
        assert result.title == "EC001: Empty Cart Checkout"
        assert result.metadata["category"] == "validation"
        assert result.metadata["example_data"] == {"cart_items": []}

    def test_parse_edge_case_result_error(self, retriever):
        """Test parsing edge case result with error."""
        item = {
            "example_data_json": "invalid json",
            "_additional": {"score": 0.5},
        }

        result = retriever._parse_edge_case_result(item)

        assert result is None


class TestKnowledgeRetrieverSearchCollection:
    """Tests for _search_collection method."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.fixture
    def retriever(self, mock_client):
        """Create retriever with mocked client."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client', return_value=mock_client):
            return KnowledgeRetriever()

    def test_search_collection_entity(self, retriever, mock_client):
        """Test searching entity collection."""
        mock_client.search_bm25.return_value = [{
            "entity_name": "Cart",
            "description": "Shopping cart",
            "_additional": {"score": 0.9},
        }]

        results = retriever._search_collection("EcommerceEntity", "cart", 5)

        assert len(results) == 1
        assert results[0].item_type == "entity"

    def test_search_collection_workflow(self, retriever, mock_client):
        """Test searching workflow collection."""
        mock_client.search_bm25.return_value = [{
            "workflow_name": "Checkout",
            "description": "Checkout flow",
            "steps_json": "[]",
            "_additional": {"score": 0.8},
        }]

        results = retriever._search_collection("EcommerceWorkflow", "checkout", 5)

        assert len(results) == 1
        assert results[0].item_type == "workflow"

    def test_search_collection_rule(self, retriever, mock_client):
        """Test searching rule collection."""
        mock_client.search_bm25.return_value = [{
            "rule_id": "BR001",
            "name": "Test Rule",
            "description": "Rule desc",
            "_additional": {"score": 0.7},
        }]

        results = retriever._search_collection("EcommerceRule", "test", 5)

        assert len(results) == 1
        assert results[0].item_type == "business_rule"

    def test_search_collection_edge_case(self, retriever, mock_client):
        """Test searching edge case collection."""
        mock_client.search_bm25.return_value = [{
            "edge_case_id": "EC001",
            "name": "Test Edge Case",
            "description": "Edge case desc",
            "example_data_json": "{}",
            "_additional": {"score": 0.6},
        }]

        results = retriever._search_collection("EcommerceEdgeCase", "test", 5)

        assert len(results) == 1
        assert results[0].item_type == "edge_case"

    def test_search_collection_unknown(self, retriever, mock_client):
        """Test searching unknown collection."""
        mock_client.search_bm25.return_value = [{"data": "test"}]

        results = retriever._search_collection("UnknownCollection", "test", 5)

        assert len(results) == 0

    def test_search_collection_error(self, retriever, mock_client):
        """Test search collection handles error."""
        mock_client.search_bm25.side_effect = Exception("Search failed")

        results = retriever._search_collection("EcommerceEntity", "test", 5)

        assert results == []


class TestKnowledgeRetrieverContext:
    """Tests for context retrieval methods."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.fixture
    def retriever(self, mock_client):
        """Create retriever with mocked client."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client', return_value=mock_client):
            return KnowledgeRetriever()

    def test_get_entity_context(self, retriever, mock_client):
        """Test getting entity context."""
        mock_client.search_bm25.return_value = [{"data": "test"}]

        context = retriever.get_entity_context("Order")

        # Should search 4 collections
        assert mock_client.search_bm25.call_count == 4
        assert "entity" in context
        assert "related_workflows" in context
        assert "business_rules" in context
        assert "edge_cases" in context

    def test_get_entity_context_error(self, retriever, mock_client):
        """Test get_entity_context handles error."""
        mock_client.search_bm25.side_effect = Exception("Error")

        context = retriever.get_entity_context("Order")

        assert context["entity"] is None
        assert context["related_workflows"] == []

    def test_get_workflow_context(self, retriever, mock_client):
        """Test getting workflow context."""
        mock_client.search_bm25.return_value = [{
            "workflow_name": "Checkout",
            "involved_entities": ["Cart", "Order"],
        }]

        context = retriever.get_workflow_context("Checkout")

        assert "workflow" in context
        assert context["workflow"] is not None

    def test_get_workflow_context_with_entities(self, retriever, mock_client):
        """Test workflow context retrieves involved entities."""
        call_count = [0]

        def mock_search(class_name, query, limit):
            call_count[0] += 1
            if class_name == "EcommerceWorkflow" and call_count[0] == 1:
                return [{
                    "workflow_name": "Checkout",
                    "involved_entities": ["Cart"],
                }]
            return [{"data": "test"}]

        mock_client.search_bm25.side_effect = mock_search

        context = retriever.get_workflow_context("Checkout")

        assert len(context["involved_entities"]) == 1

    def test_get_workflow_context_error(self, retriever, mock_client):
        """Test get_workflow_context handles error."""
        mock_client.search_bm25.side_effect = Exception("Error")

        context = retriever.get_workflow_context("Checkout")

        assert context["workflow"] is None


class TestKnowledgeRetrieverPatterns:
    """Tests for pattern retrieval."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.fixture
    def retriever(self, mock_client):
        """Create retriever with mocked client."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client', return_value=mock_client):
            return KnowledgeRetriever()

    def test_find_test_patterns(self, retriever, mock_client):
        """Test finding test patterns."""
        mock_client.search_bm25.return_value = [{
            "entity": "Order",
            "scenario": "happy_path",
            "context": "Standard order",
            "data_json": json.dumps({"order_id": "123"}),
            "quality_score": 0.95,
            "usage_count": 10,
        }]

        patterns = retriever.find_test_patterns("Order", scenario="happy_path")

        assert len(patterns) == 1
        assert patterns[0]["entity"] == "Order"
        assert patterns[0]["data"]["order_id"] == "123"

    def test_find_test_patterns_no_scenario(self, retriever, mock_client):
        """Test finding patterns without scenario."""
        mock_client.search_bm25.return_value = []

        retriever.find_test_patterns("Order")

        call_kwargs = mock_client.search_bm25.call_args[1]
        assert call_kwargs["query"] == "Order"

    def test_find_test_patterns_with_scenario(self, retriever, mock_client):
        """Test finding patterns with scenario."""
        mock_client.search_bm25.return_value = []

        retriever.find_test_patterns("Order", scenario="edge_case")

        call_kwargs = mock_client.search_bm25.call_args[1]
        assert "Order" in call_kwargs["query"]
        assert "edge_case" in call_kwargs["query"]

    def test_find_test_patterns_error(self, retriever, mock_client):
        """Test find_test_patterns handles error."""
        mock_client.search_bm25.side_effect = Exception("Error")

        patterns = retriever.find_test_patterns("Order")

        assert patterns == []


class TestKnowledgeRetrieverSummary:
    """Tests for knowledge summary."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Weaviate client."""
        return MagicMock()

    @pytest.fixture
    def retriever(self, mock_client):
        """Create retriever with mocked client."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client', return_value=mock_client):
            return KnowledgeRetriever()

    def test_summarize_knowledge_with_results(self, retriever, mock_client):
        """Test summarizing knowledge with results."""
        mock_client.search_bm25.return_value = [{
            "entity_name": "Order",
            "description": "Order entity for managing purchases",
            "_additional": {"score": 0.9},
        }]

        summary = retriever.summarize_knowledge("order")

        assert "Found" in summary
        assert "Order" in summary
        assert "entity" in summary

    def test_summarize_knowledge_no_results(self, retriever, mock_client):
        """Test summarizing knowledge with no results."""
        mock_client.search_bm25.return_value = []

        summary = retriever.summarize_knowledge("nonexistent")

        assert "No relevant knowledge found" in summary

    def test_summarize_knowledge_error(self, retriever, mock_client):
        """Test summarize_knowledge handles search errors gracefully."""
        mock_client.search_bm25.side_effect = Exception("Error")

        summary = retriever.summarize_knowledge("test")

        # When all searches fail, returns no results message
        assert "No relevant knowledge found" in summary


class TestGetRetriever:
    """Tests for get_retriever function."""

    def test_get_retriever_returns_instance(self):
        """Test get_retriever returns a KnowledgeRetriever instance."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client'):
            retriever = get_retriever()

            assert isinstance(retriever, KnowledgeRetriever)

    def test_get_retriever_creates_new_instance(self):
        """Test get_retriever creates new instances."""
        with patch('ecommerce_agent.knowledge.retriever.get_weaviate_client'):
            retriever1 = get_retriever()
            retriever2 = get_retriever()

            # Each call creates a new instance (not singleton)
            assert retriever1 is not retriever2
