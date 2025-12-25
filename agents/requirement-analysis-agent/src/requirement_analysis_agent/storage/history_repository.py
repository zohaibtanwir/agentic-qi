"""History Repository - Persists and retrieves analysis results."""

import json
from datetime import datetime, timezone
from typing import Optional

from requirement_analysis_agent.models import AnalysisResult
from requirement_analysis_agent.storage.weaviate_client import WeaviateClient
from requirement_analysis_agent.utils.logging import get_logger


logger = get_logger(__name__)


class HistoryRepository:
    """Repository for persisting and retrieving analysis history."""

    def __init__(self, weaviate_client: WeaviateClient):
        """Initialize repository.

        Args:
            weaviate_client: Weaviate client instance
        """
        self.client = weaviate_client

    async def save(self, result: AnalysisResult) -> str:
        """Save an analysis result.

        Args:
            result: Analysis result to save

        Returns:
            UUID of saved record
        """
        # Serialize the full result to JSON
        analysis_json = result.model_dump_json()

        # Create storage record with searchable fields
        record = {
            "request_id": result.request_id,
            "title": result.extracted_requirement.title,
            "description": result.extracted_requirement.description,
            "input_type": result.extracted_requirement.input_type.value,
            "overall_score": result.quality_score.overall_score,
            "overall_grade": result.quality_score.overall_grade.value,
            "gaps_count": len(result.gaps),
            "questions_count": len(result.questions),
            "generated_acs_count": len(result.generated_acs),
            "ready_for_tests": result.ready_for_test_generation,
            "analysis_data": analysis_json,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "llm_provider": result.metadata.llm_provider,
            "llm_model": result.metadata.llm_model,
        }

        uuid = await self.client.insert(record)
        logger.info(
            "analysis_saved",
            request_id=result.request_id,
            uuid=uuid,
        )

        return uuid

    async def get_by_request_id(self, request_id: str) -> Optional[AnalysisResult]:
        """Retrieve an analysis by request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            AnalysisResult or None if not found
        """
        record = await self.client.get_by_request_id(request_id)
        if not record:
            return None

        return self._deserialize_result(record["data"])

    async def get_by_uuid(self, uuid: str) -> Optional[AnalysisResult]:
        """Retrieve an analysis by UUID.

        Args:
            uuid: The storage UUID

        Returns:
            AnalysisResult or None if not found
        """
        record = await self.client.get_by_id(uuid)
        if not record:
            return None

        return self._deserialize_result(record["data"])

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search for similar analyses.

        Args:
            query: Search query (title, description)
            limit: Maximum results

        Returns:
            List of matching analysis summaries
        """
        results = await self.client.search(query, top_k=limit)

        summaries = []
        for result in results:
            data = result["data"]
            summaries.append({
                "uuid": result["id"],
                "request_id": data.get("request_id"),
                "title": data.get("title"),
                "overall_score": data.get("overall_score"),
                "overall_grade": data.get("overall_grade"),
                "gaps_count": data.get("gaps_count"),
                "ready_for_tests": data.get("ready_for_tests"),
                "created_at": data.get("created_at"),
                "score": result.get("score"),
            })

        return summaries

    async def list_recent(self, limit: int = 20) -> list[dict]:
        """List recent analyses.

        Args:
            limit: Maximum results

        Returns:
            List of recent analysis summaries
        """
        results = await self.client.list_recent(limit)

        summaries = []
        for result in results:
            data = result["data"]
            summaries.append({
                "uuid": result["id"],
                "request_id": data.get("request_id"),
                "title": data.get("title"),
                "overall_score": data.get("overall_score"),
                "overall_grade": data.get("overall_grade"),
                "input_type": data.get("input_type"),
                "gaps_count": data.get("gaps_count"),
                "questions_count": data.get("questions_count"),
                "ready_for_tests": data.get("ready_for_tests"),
                "created_at": data.get("created_at"),
            })

        return summaries

    async def delete(self, request_id: str) -> bool:
        """Delete an analysis by request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            True if deleted successfully
        """
        record = await self.client.get_by_request_id(request_id)
        if not record:
            return False

        return await self.client.delete(record["id"])

    async def count(self) -> int:
        """Count total analyses.

        Returns:
            Number of analyses stored
        """
        return await self.client.count()

    def _deserialize_result(self, data: dict) -> Optional[AnalysisResult]:
        """Deserialize analysis data to AnalysisResult.

        Args:
            data: Storage record data

        Returns:
            AnalysisResult or None if deserialization fails
        """
        try:
            analysis_json = data.get("analysis_data")
            if not analysis_json:
                return None

            return AnalysisResult.model_validate_json(analysis_json)

        except Exception as e:
            logger.error("analysis_deserialize_error", error=str(e))
            return None
