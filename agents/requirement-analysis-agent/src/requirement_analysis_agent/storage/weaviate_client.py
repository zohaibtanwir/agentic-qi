"""Weaviate vector database client for analysis history."""

from typing import Any, Optional

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery, Filter

from requirement_analysis_agent.config import Settings
from requirement_analysis_agent.utils.logging import get_logger


logger = get_logger(__name__)


class WeaviateClient:
    """Client for Weaviate vector database operations."""

    # Collection names
    COLLECTION_ANALYSIS_HISTORY = "RequirementAnalysis"

    def __init__(self, settings: Settings):
        """Initialize Weaviate client.

        Args:
            settings: Application settings with Weaviate config
        """
        self.settings = settings
        self.client: Optional[weaviate.WeaviateClient] = None
        logger.info(
            "weaviate_client_initialized",
            url=settings.weaviate_url,
        )

    async def connect(self) -> None:
        """Connect to Weaviate instance."""
        try:
            # Parse host from URL
            host = self.settings.weaviate_url.replace("http://", "").replace("https://", "")
            if ":" in host:
                host = host.split(":")[0]

            self.client = weaviate.connect_to_local(
                host=host,
                port=8080,
            )
            logger.info("weaviate_connected", url=self.settings.weaviate_url)

            # Ensure schema is created
            await self._ensure_schema()

        except Exception as e:
            logger.error("weaviate_connection_error", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Weaviate instance."""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("weaviate_disconnected")

    async def _ensure_schema(self) -> None:
        """Ensure the analysis history collection exists."""
        if not self.client:
            return

        if not self.client.collections.exists(self.COLLECTION_ANALYSIS_HISTORY):
            await self._create_analysis_collection()

    async def _create_analysis_collection(self) -> None:
        """Create the analysis history collection with schema."""
        if not self.client:
            return

        self.client.collections.create(
            name=self.COLLECTION_ANALYSIS_HISTORY,
            properties=[
                Property(name="request_id", data_type=DataType.TEXT),
                Property(name="title", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="input_type", data_type=DataType.TEXT),
                Property(name="overall_score", data_type=DataType.INT),
                Property(name="overall_grade", data_type=DataType.TEXT),
                Property(name="gaps_count", data_type=DataType.INT),
                Property(name="questions_count", data_type=DataType.INT),
                Property(name="generated_acs_count", data_type=DataType.INT),
                Property(name="ready_for_tests", data_type=DataType.BOOL),
                Property(name="analysis_data", data_type=DataType.TEXT),  # JSON blob
                Property(name="created_at", data_type=DataType.DATE),
                Property(name="llm_provider", data_type=DataType.TEXT),
                Property(name="llm_model", data_type=DataType.TEXT),
            ],
        )
        logger.info("weaviate_collection_created", collection=self.COLLECTION_ANALYSIS_HISTORY)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search for similar analyses.

        Args:
            query: Search query text
            top_k: Number of results to return
            min_score: Minimum relevance score

        Returns:
            List of results with data and metadata
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)

            # Perform BM25 keyword search
            response = collection.query.bm25(
                query=query,
                limit=top_k,
                return_metadata=MetadataQuery(score=True),
            )

            results = []
            for obj in response.objects:
                score = obj.metadata.score if obj.metadata else 0.0
                if score >= min_score:
                    result = {
                        "id": str(obj.uuid),
                        "data": obj.properties,
                        "score": score,
                    }
                    results.append(result)

            logger.info(
                "weaviate_search_complete",
                query_length=len(query),
                results=len(results),
            )

            return results

        except Exception as e:
            logger.error("weaviate_search_error", error=str(e))
            return []

    async def insert(self, data: dict[str, Any]) -> str:
        """Insert an analysis record.

        Args:
            data: Analysis properties to insert

        Returns:
            UUID of inserted object
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)
            uuid = collection.data.insert(properties=data)

            logger.info("weaviate_insert_complete", uuid=str(uuid))
            return str(uuid)

        except Exception as e:
            logger.error("weaviate_insert_error", error=str(e))
            raise

    async def get_by_id(self, uuid: str) -> Optional[dict[str, Any]]:
        """Get an analysis by UUID.

        Args:
            uuid: Object UUID

        Returns:
            Analysis data or None if not found
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)
            obj = collection.query.fetch_object_by_id(uuid)

            if obj:
                return {
                    "id": str(obj.uuid),
                    "data": obj.properties,
                }
            return None

        except Exception as e:
            logger.error("weaviate_get_error", uuid=uuid, error=str(e))
            return None

    async def get_by_request_id(self, request_id: str) -> Optional[dict[str, Any]]:
        """Get an analysis by request ID.

        Args:
            request_id: Analysis request ID

        Returns:
            Analysis data or None if not found
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)

            response = collection.query.fetch_objects(
                filters=Filter.by_property("request_id").equal(request_id),
                limit=1,
            )

            if response.objects:
                obj = response.objects[0]
                return {
                    "id": str(obj.uuid),
                    "data": obj.properties,
                }
            return None

        except Exception as e:
            logger.error("weaviate_get_by_request_id_error", request_id=request_id, error=str(e))
            return None

    async def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent analyses.

        Args:
            limit: Maximum number of results

        Returns:
            List of recent analyses
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)

            response = collection.query.fetch_objects(
                limit=limit,
                return_metadata=MetadataQuery(creation_time=True),
            )

            results = []
            for obj in response.objects:
                results.append({
                    "id": str(obj.uuid),
                    "data": obj.properties,
                    "created_at": obj.metadata.creation_time if obj.metadata else None,
                })

            return results

        except Exception as e:
            logger.error("weaviate_list_error", error=str(e))
            return []

    async def delete(self, uuid: str) -> bool:
        """Delete an analysis by UUID.

        Args:
            uuid: Object UUID

        Returns:
            True if deleted successfully
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)
            collection.data.delete_by_id(uuid)
            logger.info("weaviate_delete_complete", uuid=uuid)
            return True

        except Exception as e:
            logger.error("weaviate_delete_error", uuid=uuid, error=str(e))
            return False

    async def count(self) -> int:
        """Count total analyses.

        Returns:
            Number of analyses stored
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            collection = self.client.collections.get(self.COLLECTION_ANALYSIS_HISTORY)
            response = collection.aggregate.over_all(total_count=True)
            return response.total_count or 0

        except Exception as e:
            logger.error("weaviate_count_error", error=str(e))
            return 0

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.client is not None
