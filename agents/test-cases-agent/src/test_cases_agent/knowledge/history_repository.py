"""Repository for managing test case generation history.

This module provides a clean interface for storing, retrieving, and managing
test case generation history in Weaviate.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from test_cases_agent.knowledge.weaviate_client import get_weaviate_client, WeaviateClient
from test_cases_agent.utils.logging import get_logger

logger = get_logger(__name__)


class HistorySession:
    """Represents a test case generation history session."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        user_story: str = "",
        acceptance_criteria: Optional[List[str]] = None,
        domain: str = "",
        test_types: Optional[List[str]] = None,
        coverage_level: str = "standard",
        generated_test_cases: Optional[List[Dict[str, Any]]] = None,
        test_case_count: int = 0,
        generation_method: str = "llm",
        model_used: str = "",
        generation_time_ms: int = 0,
        status: str = "success",
        error_message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        weaviate_id: str = "",
    ):
        self.session_id = session_id or str(uuid4())
        self.user_story = user_story
        self.acceptance_criteria = acceptance_criteria or []
        self.domain = domain
        self.test_types = test_types or []
        self.coverage_level = coverage_level
        self.generated_test_cases = generated_test_cases or []
        self.test_case_count = test_case_count
        self.generation_method = generation_method
        self.model_used = model_used
        self.generation_time_ms = generation_time_ms
        self.status = status
        self.error_message = error_message
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at or self.created_at
        self.weaviate_id = weaviate_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "user_story": self.user_story,
            "acceptance_criteria": self.acceptance_criteria,
            "domain": self.domain,
            "test_types": self.test_types,
            "coverage_level": self.coverage_level,
            "generated_test_cases": self.generated_test_cases,
            "test_case_count": self.test_case_count,
            "generation_method": self.generation_method,
            "model_used": self.model_used,
            "generation_time_ms": self.generation_time_ms,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistorySession":
        """Create from dictionary."""
        return cls(
            session_id=data.get("session_id"),
            user_story=data.get("user_story", ""),
            acceptance_criteria=data.get("acceptance_criteria", []),
            domain=data.get("domain", ""),
            test_types=data.get("test_types", []),
            coverage_level=data.get("coverage_level", "standard"),
            generated_test_cases=data.get("generated_test_cases", []),
            test_case_count=data.get("test_case_count", 0),
            generation_method=data.get("generation_method", "llm"),
            model_used=data.get("model_used", ""),
            generation_time_ms=data.get("generation_time_ms", 0),
            status=data.get("status", "success"),
            error_message=data.get("error_message", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            weaviate_id=data.get("weaviate_id", ""),
        )

    def get_preview(self) -> str:
        """Get a short preview of the user story for display."""
        max_length = 100
        if len(self.user_story) <= max_length:
            return self.user_story
        return self.user_story[:max_length] + "..."


class HistoryRepository:
    """Repository for managing test case generation history."""

    def __init__(self, client: Optional[WeaviateClient] = None):
        """
        Initialize the repository.

        Args:
            client: Optional Weaviate client instance. If not provided,
                   uses the singleton instance.
        """
        self._client = client

    @property
    def client(self) -> WeaviateClient:
        """Get the Weaviate client."""
        if self._client is None:
            self._client = get_weaviate_client()
        return self._client

    async def save(self, session: HistorySession) -> str:
        """
        Save a history session.

        Args:
            session: The history session to save.

        Returns:
            The Weaviate UUID of the saved session.
        """
        try:
            result = await self.client.store_test_case_history(session.to_dict())
            logger.info(f"Saved history session: {session.session_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to save history session: {e}")
            raise

    async def get(self, session_id: str) -> Optional[HistorySession]:
        """
        Get a history session by ID.

        Args:
            session_id: The session ID to retrieve.

        Returns:
            The history session, or None if not found.
        """
        try:
            data = await self.client.get_test_case_history(session_id)
            if data:
                return HistorySession.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get history session: {e}")
            raise

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        domain: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[HistorySession]:
        """
        List history sessions.

        Args:
            limit: Maximum number of sessions to return.
            offset: Number of sessions to skip.
            domain: Optional filter by domain.
            status: Optional filter by status.

        Returns:
            List of history sessions.
        """
        try:
            data_list = await self.client.list_test_case_history(
                limit=limit,
                offset=offset,
                domain=domain,
                status=status,
            )
            return [HistorySession.from_dict(data) for data in data_list]
        except Exception as e:
            logger.error(f"Failed to list history sessions: {e}")
            # Return empty list instead of raising - allows UI to work without Weaviate
            return []

    async def delete(self, session_id: str) -> bool:
        """
        Delete a history session.

        Args:
            session_id: The session ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        try:
            result = await self.client.delete_test_case_history(session_id)
            if result:
                logger.info(f"Deleted history session: {session_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete history session: {e}")
            raise

    async def count(
        self,
        domain: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Count history sessions.

        Args:
            domain: Optional filter by domain.
            status: Optional filter by status.

        Returns:
            Total count of sessions.
        """
        try:
            return await self.client.count_test_case_history(
                domain=domain,
                status=status,
            )
        except Exception as e:
            logger.error(f"Failed to count history sessions: {e}")
            return 0

    async def create_from_generation(
        self,
        user_story: str,
        acceptance_criteria: List[str],
        test_cases: List[Dict[str, Any]],
        domain: str = "",
        test_types: Optional[List[str]] = None,
        coverage_level: str = "standard",
        generation_method: str = "llm",
        model_used: str = "",
        generation_time_ms: int = 0,
        status: str = "success",
        error_message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HistorySession:
        """
        Create and save a history session from a generation result.

        This is a convenience method for creating history entries after
        test case generation.

        Args:
            user_story: The original user story input.
            acceptance_criteria: The acceptance criteria.
            test_cases: The generated test cases.
            domain: The domain context.
            test_types: Types of tests generated.
            coverage_level: Coverage level used.
            generation_method: Method used for generation.
            model_used: LLM model used.
            generation_time_ms: Time taken in milliseconds.
            status: Generation status.
            error_message: Error message if failed.
            metadata: Additional metadata.

        Returns:
            The created and saved history session.
        """
        session = HistorySession(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            domain=domain,
            test_types=test_types or [],
            coverage_level=coverage_level,
            generated_test_cases=test_cases,
            test_case_count=len(test_cases),
            generation_method=generation_method,
            model_used=model_used,
            generation_time_ms=generation_time_ms,
            status=status,
            error_message=error_message,
            metadata=metadata or {},
        )

        await self.save(session)
        return session


# Singleton instance
_history_repository_instance: Optional[HistoryRepository] = None


def get_history_repository() -> HistoryRepository:
    """
    Get singleton HistoryRepository instance.

    Returns:
        HistoryRepository instance.
    """
    global _history_repository_instance
    if _history_repository_instance is None:
        _history_repository_instance = HistoryRepository()
    return _history_repository_instance


__all__ = [
    "HistorySession",
    "HistoryRepository",
    "get_history_repository",
]
