"""Weaviate client for vector database operations."""

import json
from typing import Any, Dict, List, Optional
import weaviate
from weaviate import WeaviateClient as WeaviateV4Client
from weaviate.classes import config
import httpx

from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class WeaviateClient:
    """Client for interacting with Weaviate vector database."""

    def __init__(self):
        """Initialize Weaviate client."""
        self.settings = get_settings()
        self._client: Optional[WeaviateV4Client] = None
        self._connected = False

    @property
    def client(self) -> WeaviateV4Client:
        """Get or create Weaviate client."""
        if not self._client:
            self._connect()
        return self._client

    def _connect(self) -> None:
        """Connect to Weaviate instance."""
        try:
            # Parse URL to get host and port
            url = self.settings.weaviate_url.replace("http://", "").replace("https://", "")
            if ":" in url:
                host, port = url.split(":")
                port = int(port)
            else:
                host = url
                port = 8080  # Default Weaviate port

            # Use configured gRPC port from settings
            grpc_port = self.settings.weaviate_grpc_port

            # For local development with Docker - use v4 API
            self._client = weaviate.connect_to_local(
                host=host,
                port=port,
                grpc_port=grpc_port,
                skip_init_checks=False,
            )

            # Test connection
            if self._client.is_ready():
                self._connected = True
                logger.info("Connected to Weaviate", url=self.settings.weaviate_url)
            else:
                raise ConnectionError("Weaviate is not ready")

        except Exception as e:
            logger.error("Failed to connect to Weaviate", error=str(e))
            raise

    def is_connected(self) -> bool:
        """Check if connected to Weaviate."""
        if not self._client:
            try:
                self._connect()  # Trigger connection if not connected
            except:
                return False
        try:
            return self._client.is_ready()
        except:
            return False

    def create_class(self, class_config: Dict[str, Any]) -> bool:
        """Create a Weaviate class (collection)."""
        try:
            class_name = class_config.get("class")

            # Check if collection already exists
            if self.client.collections.exists(class_name):
                logger.debug("Collection already exists", class_name=class_name)
                return True

            # Create collection with v4 API
            # Convert old schema to v4 config
            properties = []
            for prop in class_config.get("properties", []):
                prop_config = config.Property(
                    name=prop["name"],
                    data_type=self._convert_data_type(prop["dataType"][0]) if prop.get("dataType") else config.DataType.TEXT
                )
                properties.append(prop_config)

            self.client.collections.create(
                name=class_name,
                properties=properties if properties else None
            )

            logger.info("Created Weaviate collection", class_name=class_name)
            return True
        except Exception as e:
            if "already exists" in str(e):
                logger.debug("Collection already exists", class_name=class_config.get("class"))
                return True
            logger.error("Failed to create collection", error=str(e))
            return False

    def _convert_data_type(self, old_type: str):
        """Convert old data type to v4 DataType."""
        type_mapping = {
            "string": config.DataType.TEXT,
            "text": config.DataType.TEXT,
            "int": config.DataType.INT,
            "number": config.DataType.NUMBER,
            "boolean": config.DataType.BOOL,
            "date": config.DataType.DATE,
        }
        return type_mapping.get(old_type.lower(), config.DataType.TEXT)

    def delete_class(self, class_name: str) -> bool:
        """Delete a Weaviate class (collection)."""
        try:
            self.client.collections.delete(class_name)
            logger.info("Deleted Weaviate collection", class_name=class_name)
            return True
        except Exception as e:
            logger.error("Failed to delete collection", class_name=class_name, error=str(e))
            return False

    def class_exists(self, class_name: str) -> bool:
        """Check if a class (collection) exists."""
        try:
            return self.client.collections.exists(class_name)
        except Exception as e:
            logger.error("Failed to check collection existence", error=str(e))
            return False

    def add_object(
        self,
        class_name: str,
        properties: Dict[str, Any],
        uuid: Optional[str] = None,
    ) -> Optional[str]:
        """Add an object to Weaviate."""
        try:
            collection = self.client.collections.get(class_name)

            if uuid:
                # v4 API: insert with UUID
                result = collection.data.insert(
                    properties=properties,
                    uuid=uuid
                )
            else:
                # v4 API: insert without UUID (auto-generate)
                result = collection.data.insert(
                    properties=properties
                )

            logger.debug("Added object to Weaviate", class_name=class_name, uuid=str(result))
            return str(result)
        except Exception as e:
            logger.error("Failed to add object", class_name=class_name, error=str(e))
            return None

    def batch_add_objects(
        self,
        class_name: str,
        objects: List[Dict[str, Any]],
    ) -> bool:
        """Add multiple objects in batch."""
        try:
            collection = self.client.collections.get(class_name)

            # v4 API: Use batch insert
            with collection.batch.dynamic() as batch:
                for obj in objects:
                    batch.add_object(properties=obj)

            logger.info(
                "Batch added objects",
                class_name=class_name,
                count=len(objects),
            )
            return True
        except Exception as e:
            logger.error("Failed to batch add objects", error=str(e))
            return False

    def search_similar(
        self,
        class_name: str,
        query: str,
        limit: int = 10,
        where_filter: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar objects using text query."""
        try:
            collection = self.client.collections.get(class_name)

            # v4 API: Use near_text query
            from weaviate.classes.query import MetadataQuery

            response = collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            # Convert response to list of dicts
            results = []
            for obj in response.objects:
                result_dict = {
                    **obj.properties,
                    "_additional": {
                        "id": str(obj.uuid),
                        "distance": obj.metadata.distance if hasattr(obj.metadata, 'distance') else None
                    }
                }
                results.append(result_dict)

            return results

        except Exception as e:
            logger.error("Failed to search similar", error=str(e))
            return []

    def search_bm25(
        self,
        class_name: str,
        query: str,
        limit: int = 10,
        properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search using BM25 keyword search."""
        try:
            collection = self.client.collections.get(class_name)

            # v4 API: Use bm25 query
            from weaviate.classes.query import MetadataQuery

            response = collection.query.bm25(
                query=query,
                query_properties=properties,
                limit=limit,
                return_metadata=MetadataQuery(score=True)
            )

            # Convert response to list of dicts
            results = []
            for obj in response.objects:
                result_dict = {
                    **obj.properties,
                    "_additional": {
                        "id": str(obj.uuid),
                        "score": obj.metadata.score if hasattr(obj.metadata, 'score') else None
                    }
                }
                results.append(result_dict)

            return results

        except Exception as e:
            logger.error("Failed to BM25 search", error=str(e))
            return []

    def get_object(
        self,
        class_name: str,
        uuid: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a specific object by UUID."""
        try:
            collection = self.client.collections.get(class_name)
            result = collection.query.fetch_object_by_id(uuid)

            if result:
                return {
                    **result.properties,
                    "id": str(result.uuid)
                }
            return None
        except Exception as e:
            logger.error("Failed to get object", uuid=uuid, error=str(e))
            return None

    def update_object(
        self,
        class_name: str,
        uuid: str,
        properties: Dict[str, Any],
    ) -> bool:
        """Update an object's properties."""
        try:
            collection = self.client.collections.get(class_name)
            collection.data.update(
                uuid=uuid,
                properties=properties,
            )
            logger.debug("Updated object", class_name=class_name, uuid=uuid)
            return True
        except Exception as e:
            logger.error("Failed to update object", uuid=uuid, error=str(e))
            return False

    def delete_object(self, class_name: str, uuid: str) -> bool:
        """Delete an object."""
        try:
            collection = self.client.collections.get(class_name)
            collection.data.delete_by_id(uuid)
            logger.debug("Deleted object", class_name=class_name, uuid=uuid)
            return True
        except Exception as e:
            logger.error("Failed to delete object", uuid=uuid, error=str(e))
            return False

    def get_schema(self) -> Dict[str, Any]:
        """Get the current Weaviate schema."""
        try:
            # v4 API: Get all collections
            collections = self.client.collections.list_all()

            # Convert to old schema format for compatibility
            classes = []
            for name, collection in collections.items():
                class_dict = {
                    "class": name,
                    "properties": []
                }

                # Get collection config if available
                try:
                    config = collection.config.get()
                    if hasattr(config, 'properties'):
                        for prop in config.properties:
                            class_dict["properties"].append({
                                "name": prop.name,
                                "dataType": [str(prop.data_type)]
                            })
                except:
                    pass

                classes.append(class_dict)

            return {"classes": classes}
        except Exception as e:
            logger.error("Failed to get schema", error=str(e))
            return {"classes": []}

    def health_check(self) -> Dict[str, Any]:
        """Check Weaviate health status."""
        try:
            is_ready = self.client.is_ready()
            schema = self.get_schema()

            return {
                "connected": self._connected,
                "ready": is_ready,
                "url": self.settings.weaviate_url,
                "classes_count": len(schema.get("classes", [])),
            }
        except Exception as e:
            return {
                "connected": False,
                "ready": False,
                "error": str(e),
            }

    def close(self) -> None:
        """Close the client connection."""
        if self._client:
            try:
                self._client.close()
                self._connected = False
                logger.info("Closed Weaviate connection")
            except Exception as e:
                logger.error("Failed to close connection", error=str(e))


# Singleton instance
_weaviate_client: Optional[WeaviateClient] = None


def get_weaviate_client() -> WeaviateClient:
    """Get singleton Weaviate client instance."""
    global _weaviate_client
    if not _weaviate_client:
        _weaviate_client = WeaviateClient()
    return _weaviate_client