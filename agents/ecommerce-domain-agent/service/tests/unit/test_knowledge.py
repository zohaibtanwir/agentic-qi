"""Unit tests for knowledge layer."""

import pytest
import json
from unittest.mock import MagicMock, patch, call

from ecommerce_agent.knowledge.collections import (
    COLLECTION_SCHEMAS,
    get_collection_names,
    get_collection_schema,
)
from ecommerce_agent.knowledge.indexer import KnowledgeIndexer
from ecommerce_agent.knowledge.retriever import KnowledgeRetriever, RetrievalResult


class TestCollections:
    def test_collection_schemas_exist(self):
        """Test that collection schemas are defined."""
        assert len(COLLECTION_SCHEMAS) > 0
        assert any(s["class"] == "EcommerceEntity" for s in COLLECTION_SCHEMAS)
        assert any(s["class"] == "EcommerceWorkflow" for s in COLLECTION_SCHEMAS)

    def test_get_collection_names(self):
        """Test getting collection names."""
        names = get_collection_names()
        assert "EcommerceEntity" in names
        assert "EcommerceWorkflow" in names
        assert "EcommerceRule" in names
        assert "EcommerceEdgeCase" in names

    def test_get_collection_schema(self):
        """Test getting a specific collection schema."""
        schema = get_collection_schema("EcommerceEntity")
        assert schema is not None
        assert schema["class"] == "EcommerceEntity"
        assert "properties" in schema

    def test_get_collection_schema_not_found(self):
        """Test getting non-existent collection schema."""
        schema = get_collection_schema("NonExistent")
        assert schema is None


class TestKnowledgeIndexer:
    @patch("ecommerce_agent.knowledge.indexer.get_weaviate_client")
    def test_initialize_collections(self, mock_get_client):
        """Test initializing collections."""
        mock_client = MagicMock()
        mock_client.class_exists.return_value = False
        mock_client.create_class.return_value = True
        mock_get_client.return_value = mock_client

        indexer = KnowledgeIndexer()
        result = indexer.initialize_collections()

        assert result is True
        assert mock_client.create_class.call_count == len(COLLECTION_SCHEMAS)

    @patch("ecommerce_agent.knowledge.indexer.get_weaviate_client")
    def test_index_entities(self, mock_get_client):
        """Test indexing entities."""
        mock_client = MagicMock()
        mock_client.batch_add_objects.return_value = True
        mock_get_client.return_value = mock_client

        indexer = KnowledgeIndexer()
        count = indexer.index_entities()

        assert count > 0
        mock_client.batch_add_objects.assert_called_once()
        call_args = mock_client.batch_add_objects.call_args
        assert call_args[0][0] == "EcommerceEntity"
        assert len(call_args[0][1]) > 0

    @patch("ecommerce_agent.knowledge.indexer.get_weaviate_client")
    def test_index_workflows(self, mock_get_client):
        """Test indexing workflows."""
        mock_client = MagicMock()
        mock_client.batch_add_objects.return_value = True
        mock_get_client.return_value = mock_client

        indexer = KnowledgeIndexer()
        count = indexer.index_workflows()

        assert count > 0
        mock_client.batch_add_objects.assert_called_once()
        call_args = mock_client.batch_add_objects.call_args
        assert call_args[0][0] == "EcommerceWorkflow"

    @patch("ecommerce_agent.knowledge.indexer.get_weaviate_client")
    def test_index_all(self, mock_get_client):
        """Test indexing all knowledge."""
        mock_client = MagicMock()
        mock_client.class_exists.return_value = True
        mock_client.batch_add_objects.return_value = True
        mock_get_client.return_value = mock_client

        indexer = KnowledgeIndexer()
        results = indexer.index_all()

        assert results["entities"] > 0
        assert results["workflows"] > 0
        assert results["business_rules"] > 0
        assert results["edge_cases"] > 0


class TestKnowledgeRetriever:
    @patch("ecommerce_agent.knowledge.retriever.get_weaviate_client")
    def test_search_with_results(self, mock_get_client):
        """Test search with mock results."""
        mock_client = MagicMock()
        mock_client.search_bm25.return_value = [
            {
                "entity_name": "cart",
                "description": "Shopping cart",
                "category": "transactional",
                "fields_json": "[]",
                "relationships_json": "[]",
                "_additional": {"score": 0.9},
            }
        ]
        mock_get_client.return_value = mock_client

        retriever = KnowledgeRetriever()
        results = retriever.search("cart", categories=["entities"])

        assert len(results) > 0
        assert results[0].item_type == "entity"
        assert results[0].title == "cart"
        assert results[0].relevance_score == 0.9

    @patch("ecommerce_agent.knowledge.retriever.get_weaviate_client")
    def test_get_entity_context(self, mock_get_client):
        """Test getting entity context."""
        mock_client = MagicMock()
        mock_client.search_bm25.return_value = [
            {
                "entity_name": "cart",
                "description": "Shopping cart",
                "_additional": {"score": 0.9},
            }
        ]
        mock_get_client.return_value = mock_client

        retriever = KnowledgeRetriever()
        context = retriever.get_entity_context("cart")

        assert context["entity"] is not None
        assert isinstance(context["related_workflows"], list)
        assert isinstance(context["business_rules"], list)
        assert isinstance(context["edge_cases"], list)

    @patch("ecommerce_agent.knowledge.retriever.get_weaviate_client")
    def test_summarize_knowledge(self, mock_get_client):
        """Test knowledge summarization."""
        mock_client = MagicMock()
        mock_client.search_bm25.return_value = []
        mock_get_client.return_value = mock_client

        retriever = KnowledgeRetriever()
        summary = retriever.summarize_knowledge("test query")

        assert isinstance(summary, str)

    def test_retrieval_result_dataclass(self):
        """Test RetrievalResult dataclass."""
        result = RetrievalResult(
            item_type="entity",
            title="Test Entity",
            content="Test content",
            relevance_score=0.95,
            metadata={"key": "value"},
        )

        assert result.item_type == "entity"
        assert result.title == "Test Entity"
        assert result.relevance_score == 0.95
        assert result.metadata["key"] == "value"


class TestWeaviateClient:
    @patch("ecommerce_agent.clients.weaviate_client.weaviate.Client")
    def test_client_initialization(self, mock_weaviate_client):
        """Test Weaviate client initialization."""
        from ecommerce_agent.clients.weaviate_client import WeaviateClient

        mock_instance = MagicMock()
        mock_instance.is_ready.return_value = True
        mock_weaviate_client.return_value = mock_instance

        client = WeaviateClient()
        assert client.client is not None

    @patch("ecommerce_agent.clients.weaviate_client.weaviate.Client")
    def test_health_check(self, mock_weaviate_client):
        """Test Weaviate health check."""
        from ecommerce_agent.clients.weaviate_client import WeaviateClient

        mock_instance = MagicMock()
        mock_instance.is_ready.return_value = True
        mock_instance.schema.get.return_value = {"classes": []}
        mock_weaviate_client.return_value = mock_instance

        client = WeaviateClient()
        client._client = mock_instance
        client._connected = True

        health = client.health_check()
        assert health["ready"] is True
        assert health["connected"] is True