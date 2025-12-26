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
    ) -> tuple[list[dict], int]:
        """Search for similar analyses.

        Args:
            query: Search query (title, description)
            limit: Maximum results

        Returns:
            Tuple of (list of matching analysis summaries, total count)
        """
        results = await self.client.search(query, top_k=limit)

        summaries = []
        for result in results:
            data = result["data"]
            # Truncate title to 100 chars for preview
            title = data.get("title") or ""
            title_preview = title[:100] + "..." if len(title) > 100 else title

            # Handle created_at - Weaviate returns datetime for DATE fields
            created_at = data.get("created_at", "")
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            elif created_at is None:
                created_at = ""

            summaries.append({
                "session_id": data.get("request_id") or "",
                "title": title_preview,
                "quality_score": int(data.get("overall_score") or 0),
                "quality_grade": data.get("overall_grade") or "",
                "gaps_count": int(data.get("gaps_count") or 0),
                "questions_count": int(data.get("questions_count") or 0),
                "generated_acs_count": int(data.get("generated_acs_count") or 0),
                "ready_for_tests": bool(data.get("ready_for_tests", False)),
                "input_type": data.get("input_type") or "",
                "llm_model": data.get("llm_model") or "",
                "created_at": str(created_at),
                "search_score": float(result.get("score") or 0.0),
            })

        return summaries, len(summaries)

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

            # Handle created_at - Weaviate returns datetime for DATE fields
            created_at = data.get("created_at", "")
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            elif created_at is None:
                created_at = ""

            summaries.append({
                "uuid": result["id"],
                "request_id": data.get("request_id") or "",
                "title": data.get("title") or "",
                "overall_score": int(data.get("overall_score") or 0),
                "overall_grade": data.get("overall_grade") or "",
                "input_type": data.get("input_type") or "",
                "gaps_count": int(data.get("gaps_count") or 0),
                "questions_count": int(data.get("questions_count") or 0),
                "ready_for_tests": bool(data.get("ready_for_tests", False)),
                "created_at": str(created_at),
            })

        return summaries

    async def list_with_filters(
        self,
        limit: int = 20,
        offset: int = 0,
        input_type: Optional[str] = None,
        quality_grade: Optional[str] = None,
        ready_status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """List analyses with advanced filters and pagination.

        Args:
            limit: Maximum number of results
            offset: Pagination offset
            input_type: Filter by input type (jira, free_form, transcript)
            quality_grade: Filter by quality grade (A, B, C, D, F)
            ready_status: Filter by ready status (ready, not_ready)
            date_from: Filter by date from (ISO string)
            date_to: Filter by date to (ISO string)

        Returns:
            Tuple of (list of analysis summaries, total count)
        """
        results, total_count = await self.client.list_with_filters(
            limit=limit,
            offset=offset,
            input_type=input_type,
            quality_grade=quality_grade,
            ready_status=ready_status,
            date_from=date_from,
            date_to=date_to,
        )

        summaries = []
        for result in results:
            data = result["data"]
            # Truncate title to 100 chars for preview
            title = data.get("title") or ""
            title_preview = title[:100] + "..." if len(title) > 100 else title

            # Handle created_at - Weaviate returns datetime for DATE fields
            created_at = data.get("created_at", "")
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            elif created_at is None:
                created_at = ""

            summaries.append({
                "session_id": data.get("request_id") or "",
                "title": title_preview,
                "quality_score": int(data.get("overall_score") or 0),
                "quality_grade": data.get("overall_grade") or "",
                "gaps_count": int(data.get("gaps_count") or 0),
                "questions_count": int(data.get("questions_count") or 0),
                "generated_acs_count": int(data.get("generated_acs_count") or 0),
                "ready_for_tests": bool(data.get("ready_for_tests", False)),
                "input_type": data.get("input_type") or "",
                "llm_model": data.get("llm_model") or "",
                "created_at": str(created_at),
            })

        return summaries, total_count

    async def get_full_session(self, session_id: str) -> Optional[dict]:
        """Get full session data including analysis result.

        Args:
            session_id: The session ID (request_id)

        Returns:
            Full session dict or None if not found
        """
        record = await self.client.get_by_request_id(session_id)
        if not record:
            return None

        data = record["data"]
        result = self._deserialize_result(data)

        if not result:
            return None

        # Handle created_at - Weaviate returns datetime for DATE fields
        created_at = data.get("created_at", "")
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
        elif created_at is None:
            created_at = ""

        return {
            "session_id": session_id,
            "analysis_result": result,
            "created_at": str(created_at),
            "updated_at": str(created_at),  # Same as created for now
        }

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
