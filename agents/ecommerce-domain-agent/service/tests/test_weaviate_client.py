"""Tests for Weaviate client."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from weaviate.classes import config

from ecommerce_agent.clients.weaviate_client import WeaviateClient, get_weaviate_client


class TestWeaviateClient:
    """Tests for WeaviateClient class."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = MagicMock()
        settings.weaviate_url = "http://localhost:8080"
        settings.weaviate_grpc_port = 50051
        return settings

    @pytest.fixture
    def mock_weaviate_v4_client(self):
        """Mock Weaviate v4 client."""
        client = MagicMock()
        client.is_ready.return_value = True
        client.collections = MagicMock()
        return client

    @pytest.fixture
    def client_with_mock(self, mock_settings, mock_weaviate_v4_client):
        """Create WeaviateClient with mocked dependencies."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.return_value = mock_weaviate_v4_client
                client = WeaviateClient()
                client._client = mock_weaviate_v4_client
                client._connected = True
                return client

    def test_init(self, mock_settings):
        """Test WeaviateClient initialization."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            client = WeaviateClient()
            assert client._client is None
            assert client._connected is False

    def test_connect_success(self, mock_settings, mock_weaviate_v4_client):
        """Test successful connection to Weaviate."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.return_value = mock_weaviate_v4_client
                client = WeaviateClient()
                client._connect()

                assert client._connected is True
                mock_weaviate.connect_to_local.assert_called_once_with(
                    host="localhost",
                    port=8080,
                    grpc_port=50051,
                    skip_init_checks=False
                )

    def test_connect_with_default_port(self, mock_weaviate_v4_client):
        """Test connection when URL has no port."""
        mock_settings = MagicMock()
        mock_settings.weaviate_url = "http://weaviate"
        mock_settings.weaviate_grpc_port = 50051

        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.return_value = mock_weaviate_v4_client
                client = WeaviateClient()
                client._connect()

                mock_weaviate.connect_to_local.assert_called_once_with(
                    host="weaviate",
                    port=8080,  # Default port
                    grpc_port=50051,
                    skip_init_checks=False
                )

    def test_connect_failure_not_ready(self, mock_settings):
        """Test connection failure when Weaviate is not ready."""
        mock_client = MagicMock()
        mock_client.is_ready.return_value = False

        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.return_value = mock_client
                client = WeaviateClient()

                with pytest.raises(ConnectionError):
                    client._connect()

    def test_connect_failure_exception(self, mock_settings):
        """Test connection failure with exception."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.side_effect = Exception("Connection failed")
                client = WeaviateClient()

                with pytest.raises(Exception):
                    client._connect()

    def test_is_connected_true(self, client_with_mock):
        """Test is_connected returns True when connected."""
        assert client_with_mock.is_connected() is True

    def test_is_connected_false_no_client(self, mock_settings):
        """Test is_connected returns False when not connected."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.side_effect = Exception("Connection failed")
                client = WeaviateClient()
                assert client.is_connected() is False

    def test_is_connected_exception(self, client_with_mock):
        """Test is_connected handles exception gracefully."""
        client_with_mock._client.is_ready.side_effect = Exception("Error")
        assert client_with_mock.is_connected() is False

    def test_client_property_triggers_connect(self, mock_settings, mock_weaviate_v4_client):
        """Test that accessing client property triggers connection."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings', return_value=mock_settings):
            with patch('ecommerce_agent.clients.weaviate_client.weaviate') as mock_weaviate:
                mock_weaviate.connect_to_local.return_value = mock_weaviate_v4_client
                client = WeaviateClient()
                _ = client.client
                mock_weaviate.connect_to_local.assert_called_once()


class TestWeaviateClientDataTypeConversion:
    """Tests for data type conversion."""

    @pytest.fixture
    def client(self):
        """Create client without connecting."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings') as mock:
            mock.return_value = MagicMock(
                weaviate_url="http://localhost:8080",
                weaviate_grpc_port=50051
            )
            return WeaviateClient()

    def test_convert_string_type(self, client):
        """Test converting string type."""
        assert client._convert_data_type("string") == config.DataType.TEXT

    def test_convert_text_type(self, client):
        """Test converting text type."""
        assert client._convert_data_type("text") == config.DataType.TEXT

    def test_convert_int_type(self, client):
        """Test converting int type."""
        assert client._convert_data_type("int") == config.DataType.INT

    def test_convert_number_type(self, client):
        """Test converting number type."""
        assert client._convert_data_type("number") == config.DataType.NUMBER

    def test_convert_boolean_type(self, client):
        """Test converting boolean type."""
        assert client._convert_data_type("boolean") == config.DataType.BOOL

    def test_convert_date_type(self, client):
        """Test converting date type."""
        assert client._convert_data_type("date") == config.DataType.DATE

    def test_convert_unknown_type_defaults_to_text(self, client):
        """Test unknown type defaults to TEXT."""
        assert client._convert_data_type("unknown") == config.DataType.TEXT

    def test_convert_case_insensitive(self, client):
        """Test conversion is case insensitive."""
        assert client._convert_data_type("STRING") == config.DataType.TEXT
        assert client._convert_data_type("Int") == config.DataType.INT


class TestWeaviateClientCollectionOperations:
    """Tests for collection operations."""

    @pytest.fixture
    def client_with_mock(self):
        """Create client with mocked Weaviate."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                weaviate_url="http://localhost:8080",
                weaviate_grpc_port=50051
            )
            client = WeaviateClient()
            client._client = MagicMock()
            client._connected = True
            return client

    def test_create_class_new_collection(self, client_with_mock):
        """Test creating a new collection."""
        client_with_mock._client.collections.exists.return_value = False

        result = client_with_mock.create_class({
            "class": "TestClass",
            "properties": [
                {"name": "title", "dataType": ["string"]},
                {"name": "count", "dataType": ["int"]}
            ]
        })

        assert result is True
        client_with_mock._client.collections.create.assert_called_once()

    def test_create_class_already_exists(self, client_with_mock):
        """Test creating collection that already exists."""
        client_with_mock._client.collections.exists.return_value = True

        result = client_with_mock.create_class({"class": "TestClass"})

        assert result is True
        client_with_mock._client.collections.create.assert_not_called()

    def test_create_class_error_already_exists_in_exception(self, client_with_mock):
        """Test create_class handles 'already exists' exception."""
        client_with_mock._client.collections.exists.return_value = False
        client_with_mock._client.collections.create.side_effect = Exception("Collection already exists")

        result = client_with_mock.create_class({"class": "TestClass"})

        assert result is True

    def test_create_class_error(self, client_with_mock):
        """Test create_class handles general error."""
        client_with_mock._client.collections.exists.return_value = False
        client_with_mock._client.collections.create.side_effect = Exception("General error")

        result = client_with_mock.create_class({"class": "TestClass"})

        assert result is False

    def test_delete_class_success(self, client_with_mock):
        """Test deleting a collection."""
        result = client_with_mock.delete_class("TestClass")

        assert result is True
        client_with_mock._client.collections.delete.assert_called_once_with("TestClass")

    def test_delete_class_error(self, client_with_mock):
        """Test delete_class handles error."""
        client_with_mock._client.collections.delete.side_effect = Exception("Delete failed")

        result = client_with_mock.delete_class("TestClass")

        assert result is False

    def test_class_exists_true(self, client_with_mock):
        """Test class_exists returns True when class exists."""
        client_with_mock._client.collections.exists.return_value = True

        assert client_with_mock.class_exists("TestClass") is True

    def test_class_exists_false(self, client_with_mock):
        """Test class_exists returns False when class doesn't exist."""
        client_with_mock._client.collections.exists.return_value = False

        assert client_with_mock.class_exists("TestClass") is False

    def test_class_exists_error(self, client_with_mock):
        """Test class_exists handles error."""
        client_with_mock._client.collections.exists.side_effect = Exception("Error")

        assert client_with_mock.class_exists("TestClass") is False


class TestWeaviateClientObjectOperations:
    """Tests for object operations."""

    @pytest.fixture
    def client_with_mock(self):
        """Create client with mocked Weaviate."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                weaviate_url="http://localhost:8080",
                weaviate_grpc_port=50051
            )
            client = WeaviateClient()
            client._client = MagicMock()
            client._connected = True
            return client

    def test_add_object_without_uuid(self, client_with_mock):
        """Test adding object without UUID."""
        mock_collection = MagicMock()
        mock_collection.data.insert.return_value = "generated-uuid"
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.add_object("TestClass", {"title": "Test"})

        assert result == "generated-uuid"
        mock_collection.data.insert.assert_called_once_with(properties={"title": "Test"})

    def test_add_object_with_uuid(self, client_with_mock):
        """Test adding object with UUID."""
        mock_collection = MagicMock()
        mock_collection.data.insert.return_value = "my-uuid"
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.add_object("TestClass", {"title": "Test"}, uuid="my-uuid")

        assert result == "my-uuid"
        mock_collection.data.insert.assert_called_once_with(properties={"title": "Test"}, uuid="my-uuid")

    def test_add_object_error(self, client_with_mock):
        """Test add_object handles error."""
        mock_collection = MagicMock()
        mock_collection.data.insert.side_effect = Exception("Insert failed")
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.add_object("TestClass", {"title": "Test"})

        assert result is None

    def test_batch_add_objects_success(self, client_with_mock):
        """Test batch adding objects."""
        mock_collection = MagicMock()
        mock_batch = MagicMock()
        mock_collection.batch.dynamic.return_value.__enter__ = MagicMock(return_value=mock_batch)
        mock_collection.batch.dynamic.return_value.__exit__ = MagicMock(return_value=None)
        client_with_mock._client.collections.get.return_value = mock_collection

        objects = [{"title": "Test1"}, {"title": "Test2"}]
        result = client_with_mock.batch_add_objects("TestClass", objects)

        assert result is True

    def test_batch_add_objects_error(self, client_with_mock):
        """Test batch_add_objects handles error."""
        client_with_mock._client.collections.get.side_effect = Exception("Batch failed")

        result = client_with_mock.batch_add_objects("TestClass", [{"title": "Test"}])

        assert result is False

    def test_get_object_found(self, client_with_mock):
        """Test getting an object that exists."""
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.properties = {"title": "Test"}
        mock_result.uuid = "test-uuid"
        mock_collection.query.fetch_object_by_id.return_value = mock_result
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.get_object("TestClass", "test-uuid")

        assert result == {"title": "Test", "id": "test-uuid"}

    def test_get_object_not_found(self, client_with_mock):
        """Test getting an object that doesn't exist."""
        mock_collection = MagicMock()
        mock_collection.query.fetch_object_by_id.return_value = None
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.get_object("TestClass", "test-uuid")

        assert result is None

    def test_get_object_error(self, client_with_mock):
        """Test get_object handles error."""
        client_with_mock._client.collections.get.side_effect = Exception("Error")

        result = client_with_mock.get_object("TestClass", "test-uuid")

        assert result is None

    def test_update_object_success(self, client_with_mock):
        """Test updating an object."""
        mock_collection = MagicMock()
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.update_object("TestClass", "test-uuid", {"title": "Updated"})

        assert result is True
        mock_collection.data.update.assert_called_once_with(uuid="test-uuid", properties={"title": "Updated"})

    def test_update_object_error(self, client_with_mock):
        """Test update_object handles error."""
        mock_collection = MagicMock()
        mock_collection.data.update.side_effect = Exception("Update failed")
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.update_object("TestClass", "test-uuid", {"title": "Updated"})

        assert result is False

    def test_delete_object_success(self, client_with_mock):
        """Test deleting an object."""
        mock_collection = MagicMock()
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.delete_object("TestClass", "test-uuid")

        assert result is True
        mock_collection.data.delete_by_id.assert_called_once_with("test-uuid")

    def test_delete_object_error(self, client_with_mock):
        """Test delete_object handles error."""
        mock_collection = MagicMock()
        mock_collection.data.delete_by_id.side_effect = Exception("Delete failed")
        client_with_mock._client.collections.get.return_value = mock_collection

        result = client_with_mock.delete_object("TestClass", "test-uuid")

        assert result is False


class TestWeaviateClientSearchOperations:
    """Tests for search operations."""

    @pytest.fixture
    def client_with_mock(self):
        """Create client with mocked Weaviate."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                weaviate_url="http://localhost:8080",
                weaviate_grpc_port=50051
            )
            client = WeaviateClient()
            client._client = MagicMock()
            client._connected = True
            return client

    def test_search_similar_success(self, client_with_mock):
        """Test similar search returns results."""
        mock_collection = MagicMock()
        mock_obj = MagicMock()
        mock_obj.properties = {"title": "Test Result"}
        mock_obj.uuid = "result-uuid"
        mock_obj.metadata.distance = 0.1
        mock_response = MagicMock()
        mock_response.objects = [mock_obj]
        mock_collection.query.near_text.return_value = mock_response
        client_with_mock._client.collections.get.return_value = mock_collection

        results = client_with_mock.search_similar("TestClass", "test query", limit=5)

        assert len(results) == 1
        assert results[0]["title"] == "Test Result"
        assert results[0]["_additional"]["id"] == "result-uuid"
        assert results[0]["_additional"]["distance"] == 0.1

    def test_search_similar_empty(self, client_with_mock):
        """Test similar search returns empty list when no results."""
        mock_collection = MagicMock()
        mock_response = MagicMock()
        mock_response.objects = []
        mock_collection.query.near_text.return_value = mock_response
        client_with_mock._client.collections.get.return_value = mock_collection

        results = client_with_mock.search_similar("TestClass", "test query")

        assert results == []

    def test_search_similar_error(self, client_with_mock):
        """Test search_similar handles error."""
        client_with_mock._client.collections.get.side_effect = Exception("Search failed")

        results = client_with_mock.search_similar("TestClass", "test query")

        assert results == []

    def test_search_bm25_success(self, client_with_mock):
        """Test BM25 search returns results."""
        mock_collection = MagicMock()
        mock_obj = MagicMock()
        mock_obj.properties = {"title": "Test Result"}
        mock_obj.uuid = "result-uuid"
        mock_obj.metadata.score = 0.9
        mock_response = MagicMock()
        mock_response.objects = [mock_obj]
        mock_collection.query.bm25.return_value = mock_response
        client_with_mock._client.collections.get.return_value = mock_collection

        results = client_with_mock.search_bm25("TestClass", "test query", limit=5)

        assert len(results) == 1
        assert results[0]["title"] == "Test Result"
        assert results[0]["_additional"]["score"] == 0.9

    def test_search_bm25_with_properties(self, client_with_mock):
        """Test BM25 search with specific properties."""
        mock_collection = MagicMock()
        mock_response = MagicMock()
        mock_response.objects = []
        mock_collection.query.bm25.return_value = mock_response
        client_with_mock._client.collections.get.return_value = mock_collection

        client_with_mock.search_bm25("TestClass", "test", properties=["title", "content"])

        mock_collection.query.bm25.assert_called_once()
        call_kwargs = mock_collection.query.bm25.call_args[1]
        assert call_kwargs["query_properties"] == ["title", "content"]

    def test_search_bm25_error(self, client_with_mock):
        """Test search_bm25 handles error."""
        client_with_mock._client.collections.get.side_effect = Exception("Search failed")

        results = client_with_mock.search_bm25("TestClass", "test query")

        assert results == []


class TestWeaviateClientSchemaAndHealth:
    """Tests for schema and health operations."""

    @pytest.fixture
    def client_with_mock(self):
        """Create client with mocked Weaviate."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                weaviate_url="http://localhost:8080",
                weaviate_grpc_port=50051
            )
            client = WeaviateClient()
            client._client = MagicMock()
            client._connected = True
            return client

    def test_get_schema_success(self, client_with_mock):
        """Test getting schema."""
        mock_collection = MagicMock()
        mock_config = MagicMock()
        mock_prop = MagicMock()
        mock_prop.name = "title"
        mock_prop.data_type = "text"
        mock_config.properties = [mock_prop]
        mock_collection.config.get.return_value = mock_config

        client_with_mock._client.collections.list_all.return_value = {"TestClass": mock_collection}

        schema = client_with_mock.get_schema()

        assert "classes" in schema
        assert len(schema["classes"]) == 1
        assert schema["classes"][0]["class"] == "TestClass"

    def test_get_schema_error(self, client_with_mock):
        """Test get_schema handles error."""
        client_with_mock._client.collections.list_all.side_effect = Exception("Schema error")

        schema = client_with_mock.get_schema()

        assert schema == {"classes": []}

    def test_health_check_healthy(self, client_with_mock):
        """Test health check when healthy."""
        client_with_mock._client.is_ready.return_value = True
        client_with_mock._client.collections.list_all.return_value = {}

        health = client_with_mock.health_check()

        assert health["connected"] is True
        assert health["ready"] is True
        assert health["url"] == "http://localhost:8080"

    def test_health_check_error(self, client_with_mock):
        """Test health check handles error."""
        client_with_mock._client.is_ready.side_effect = Exception("Health check failed")

        health = client_with_mock.health_check()

        assert health["connected"] is False
        assert health["ready"] is False
        assert "error" in health

    def test_close_success(self, client_with_mock):
        """Test closing connection."""
        client_with_mock.close()

        client_with_mock._client.close.assert_called_once()
        assert client_with_mock._connected is False

    def test_close_no_client(self):
        """Test close when no client exists."""
        with patch('ecommerce_agent.clients.weaviate_client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                weaviate_url="http://localhost:8080",
                weaviate_grpc_port=50051
            )
            client = WeaviateClient()
            client.close()  # Should not raise

    def test_close_error(self, client_with_mock):
        """Test close handles error gracefully."""
        client_with_mock._client.close.side_effect = Exception("Close failed")

        client_with_mock.close()  # Should not raise


class TestGetWeaviateClient:
    """Tests for singleton getter."""

    def test_get_weaviate_client_singleton(self):
        """Test that get_weaviate_client returns singleton."""
        import ecommerce_agent.clients.weaviate_client as module

        # Reset singleton
        module._weaviate_client = None

        with patch.object(WeaviateClient, '__init__', return_value=None):
            client1 = get_weaviate_client()
            client2 = get_weaviate_client()

            assert client1 is client2

        # Clean up
        module._weaviate_client = None
