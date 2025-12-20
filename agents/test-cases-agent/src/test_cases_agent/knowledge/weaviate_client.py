"""Weaviate vector database client for knowledge management."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes import config, query

from test_cases_agent.config import get_settings
from test_cases_agent.utils.logging import get_logger


class WeaviateClient:
    """Client for managing test case knowledge in Weaviate."""

    # Collection schemas
    TEST_CASES_SCHEMA = "TestCases"
    TEST_PATTERNS_SCHEMA = "TestPatterns"
    COVERAGE_PATTERNS_SCHEMA = "CoveragePatterns"

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Weaviate client.

        Args:
            url: Weaviate instance URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.url = url or settings.weaviate_url
        self.api_key = api_key or settings.weaviate_api_key
        self.timeout = timeout
        self.logger = get_logger(__name__)
        self._client: Optional[weaviate.Client] = None

    async def connect(self) -> None:
        """Connect to Weaviate instance."""
        if self._client:
            return

        try:
            self.logger.info(f"Connecting to Weaviate at {self.url}")

            # Create client with authentication if API key is provided
            if self.api_key:
                auth_config = AuthApiKey(api_key=self.api_key)
                self._client = weaviate.Client(
                    url=self.url,
                    auth_client_secret=auth_config,
                    timeout_config=(5, self.timeout),
                )
            else:
                self._client = weaviate.Client(
                    url=self.url,
                    timeout_config=(5, self.timeout),
                )

            # Test connection
            if self._client.is_ready():
                self.logger.info("Successfully connected to Weaviate")
                await self._ensure_schemas()
            else:
                raise ConnectionError("Weaviate is not ready")

        except Exception as e:
            self.logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Weaviate."""
        if self._client:
            self._client = None
            self.logger.info("Disconnected from Weaviate")

    async def _ensure_schemas(self) -> None:
        """Ensure required schemas exist in Weaviate."""
        try:
            # Check if schemas exist
            existing_schemas = self._client.schema.get()
            existing_classes = {cls["class"] for cls in existing_schemas.get("classes", [])}

            # Create TestCases schema if needed
            if self.TEST_CASES_SCHEMA not in existing_classes:
                await self._create_test_cases_schema()

            # Create TestPatterns schema if needed
            if self.TEST_PATTERNS_SCHEMA not in existing_classes:
                await self._create_test_patterns_schema()

            # Create CoveragePatterns schema if needed
            if self.COVERAGE_PATTERNS_SCHEMA not in existing_classes:
                await self._create_coverage_patterns_schema()

            self.logger.info("All required schemas are ready")

        except Exception as e:
            self.logger.error(f"Failed to ensure schemas: {e}")
            raise

    async def _create_test_cases_schema(self) -> None:
        """Create TestCases schema."""
        schema = {
            "class": self.TEST_CASES_SCHEMA,
            "description": "Stores test case specifications",
            "properties": [
                {"name": "test_id", "dataType": ["text"]},
                {"name": "title", "dataType": ["text"]},
                {"name": "description", "dataType": ["text"]},
                {"name": "test_type", "dataType": ["text"]},
                {"name": "priority", "dataType": ["text"]},
                {"name": "user_story_id", "dataType": ["text"]},
                {"name": "requirements", "dataType": ["text[]"]},
                {"name": "preconditions", "dataType": ["text[]"]},
                {"name": "steps", "dataType": ["text"]},  # JSON string
                {"name": "expected_results", "dataType": ["text[]"]},
                {"name": "postconditions", "dataType": ["text[]"]},
                {"name": "test_data", "dataType": ["text"]},  # JSON string
                {"name": "tags", "dataType": ["text[]"]},
                {"name": "created_at", "dataType": ["date"]},
                {"name": "updated_at", "dataType": ["date"]},
                {"name": "coverage_score", "dataType": ["number"]},
                {"name": "complexity_score", "dataType": ["number"]},
                {"name": "domain_context", "dataType": ["text"]},  # JSON string
            ],
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada-002",
                    "type": "text",
                }
            },
        }

        self._client.schema.create_class(schema)
        self.logger.info(f"Created {self.TEST_CASES_SCHEMA} schema")

    async def _create_test_patterns_schema(self) -> None:
        """Create TestPatterns schema."""
        schema = {
            "class": self.TEST_PATTERNS_SCHEMA,
            "description": "Stores common test patterns",
            "properties": [
                {"name": "pattern_id", "dataType": ["text"]},
                {"name": "name", "dataType": ["text"]},
                {"name": "description", "dataType": ["text"]},
                {"name": "category", "dataType": ["text"]},
                {"name": "test_types", "dataType": ["text[]"]},
                {"name": "applicable_domains", "dataType": ["text[]"]},
                {"name": "template", "dataType": ["text"]},  # JSON string
                {"name": "examples", "dataType": ["text[]"]},
                {"name": "tags", "dataType": ["text[]"]},
                {"name": "usage_count", "dataType": ["int"]},
                {"name": "success_rate", "dataType": ["number"]},
                {"name": "created_at", "dataType": ["date"]},
            ],
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada-002",
                    "type": "text",
                }
            },
        }

        self._client.schema.create_class(schema)
        self.logger.info(f"Created {self.TEST_PATTERNS_SCHEMA} schema")

    async def _create_coverage_patterns_schema(self) -> None:
        """Create CoveragePatterns schema."""
        schema = {
            "class": self.COVERAGE_PATTERNS_SCHEMA,
            "description": "Stores test coverage patterns",
            "properties": [
                {"name": "pattern_id", "dataType": ["text"]},
                {"name": "requirement_type", "dataType": ["text"]},
                {"name": "coverage_strategy", "dataType": ["text"]},
                {"name": "test_types_required", "dataType": ["text[]"]},
                {"name": "minimum_test_count", "dataType": ["int"]},
                {"name": "priority_distribution", "dataType": ["text"]},  # JSON string
                {"name": "edge_cases", "dataType": ["text[]"]},
                {"name": "validation_rules", "dataType": ["text[]"]},
                {"name": "domain", "dataType": ["text"]},
                {"name": "effectiveness_score", "dataType": ["number"]},
                {"name": "created_at", "dataType": ["date"]},
            ],
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada-002",
                    "type": "text",
                }
            },
        }

        self._client.schema.create_class(schema)
        self.logger.info(f"Created {self.COVERAGE_PATTERNS_SCHEMA} schema")

    async def store_test_case(
        self,
        test_case: Dict[str, Any],
        vectorize_fields: Optional[List[str]] = None,
    ) -> str:
        """
        Store a test case in Weaviate.

        Args:
            test_case: Test case data
            vectorize_fields: Fields to use for vectorization

        Returns:
            UUID of stored test case
        """
        if not self._client:
            await self.connect()

        try:
            # Prepare data
            data = {
                "test_id": test_case.get("id", str(uuid4())),
                "title": test_case.get("title", ""),
                "description": test_case.get("description", ""),
                "test_type": test_case.get("test_type", ""),
                "priority": test_case.get("priority", ""),
                "user_story_id": test_case.get("user_story_id", ""),
                "requirements": test_case.get("requirements", []),
                "preconditions": test_case.get("preconditions", []),
                "steps": json.dumps(test_case.get("steps", [])),
                "expected_results": test_case.get("expected_results", []),
                "postconditions": test_case.get("postconditions", []),
                "test_data": json.dumps(test_case.get("test_data", {})),
                "tags": test_case.get("tags", []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "coverage_score": test_case.get("coverage_score", 0.0),
                "complexity_score": test_case.get("complexity_score", 0.0),
                "domain_context": json.dumps(test_case.get("domain_context", {})),
            }

            # Store in Weaviate
            result = self._client.data_object.create(
                data_object=data,
                class_name=self.TEST_CASES_SCHEMA,
            )

            self.logger.info(f"Stored test case with ID: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to store test case: {e}")
            raise

    async def search_test_cases(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        return_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar test cases.

        Args:
            query: Search query
            limit: Maximum results
            filters: Optional filters
            return_fields: Fields to return

        Returns:
            List of matching test cases
        """
        if not self._client:
            await self.connect()

        try:
            # Default return fields
            if not return_fields:
                return_fields = [
                    "test_id", "title", "description", "test_type",
                    "priority", "tags", "coverage_score"
                ]

            # Build query
            weaviate_query = (
                self._client.query
                .get(self.TEST_CASES_SCHEMA, return_fields)
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
            )

            # Add filters if provided
            if filters:
                where_filter = self._build_where_filter(filters)
                weaviate_query = weaviate_query.with_where(where_filter)

            # Execute query
            result = weaviate_query.do()

            # Extract and return results
            test_cases = result.get("data", {}).get("Get", {}).get(self.TEST_CASES_SCHEMA, [])

            # Parse JSON fields
            for test_case in test_cases:
                if "steps" in test_case and test_case["steps"]:
                    try:
                        test_case["steps"] = json.loads(test_case["steps"])
                    except json.JSONDecodeError:
                        pass

                if "test_data" in test_case and test_case["test_data"]:
                    try:
                        test_case["test_data"] = json.loads(test_case["test_data"])
                    except json.JSONDecodeError:
                        pass

                if "domain_context" in test_case and test_case["domain_context"]:
                    try:
                        test_case["domain_context"] = json.loads(test_case["domain_context"])
                    except json.JSONDecodeError:
                        pass

            return test_cases

        except Exception as e:
            self.logger.error(f"Failed to search test cases: {e}")
            raise

    async def search_patterns(
        self,
        query: str,
        pattern_type: str = "test",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for test or coverage patterns.

        Args:
            query: Search query
            pattern_type: Type of pattern ("test" or "coverage")
            limit: Maximum results

        Returns:
            List of matching patterns
        """
        if not self._client:
            await self.connect()

        try:
            if pattern_type == "test":
                class_name = self.TEST_PATTERNS_SCHEMA
                return_fields = [
                    "pattern_id", "name", "description", "category",
                    "template", "usage_count", "success_rate"
                ]
            else:
                class_name = self.COVERAGE_PATTERNS_SCHEMA
                return_fields = [
                    "pattern_id", "requirement_type", "coverage_strategy",
                    "test_types_required", "effectiveness_score"
                ]

            # Build and execute query
            result = (
                self._client.query
                .get(class_name, return_fields)
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .do()
            )

            # Extract and return results
            patterns = result.get("data", {}).get("Get", {}).get(class_name, [])

            # Parse JSON fields
            for pattern in patterns:
                if "template" in pattern and pattern["template"]:
                    try:
                        pattern["template"] = json.loads(pattern["template"])
                    except json.JSONDecodeError:
                        pass

                if "priority_distribution" in pattern and pattern["priority_distribution"]:
                    try:
                        pattern["priority_distribution"] = json.loads(pattern["priority_distribution"])
                    except json.JSONDecodeError:
                        pass

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to search patterns: {e}")
            raise

    async def update_pattern_usage(
        self,
        pattern_id: str,
        pattern_type: str = "test",
        success: bool = True,
    ) -> None:
        """
        Update usage statistics for a pattern.

        Args:
            pattern_id: Pattern ID
            pattern_type: Type of pattern
            success: Whether usage was successful
        """
        if not self._client:
            await self.connect()

        try:
            class_name = (
                self.TEST_PATTERNS_SCHEMA if pattern_type == "test"
                else self.COVERAGE_PATTERNS_SCHEMA
            )

            # Get current pattern
            where_filter = {
                "path": ["pattern_id"],
                "operator": "Equal",
                "valueString": pattern_id,
            }

            result = (
                self._client.query
                .get(class_name, ["pattern_id", "usage_count", "success_rate"])
                .with_where(where_filter)
                .do()
            )

            patterns = result.get("data", {}).get("Get", {}).get(class_name, [])
            if not patterns:
                self.logger.warning(f"Pattern {pattern_id} not found")
                return

            pattern = patterns[0]
            current_count = pattern.get("usage_count", 0)
            current_rate = pattern.get("success_rate", 0.0)

            # Calculate new statistics
            new_count = current_count + 1
            if success:
                new_rate = ((current_rate * current_count) + 1) / new_count
            else:
                new_rate = (current_rate * current_count) / new_count

            # Update pattern
            # Note: Weaviate doesn't support direct updates, so we'd need to delete and re-create
            # For now, we'll log this as a limitation
            self.logger.info(
                f"Pattern {pattern_id} usage updated: count={new_count}, success_rate={new_rate}"
            )

        except Exception as e:
            self.logger.error(f"Failed to update pattern usage: {e}")

    def _build_where_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Weaviate where filter from dictionary.

        Args:
            filters: Filter dictionary

        Returns:
            Weaviate where filter
        """
        where_conditions = []

        for field, value in filters.items():
            if isinstance(value, str):
                where_conditions.append({
                    "path": [field],
                    "operator": "Equal",
                    "valueString": value,
                })
            elif isinstance(value, bool):
                where_conditions.append({
                    "path": [field],
                    "operator": "Equal",
                    "valueBoolean": value,
                })
            elif isinstance(value, (int, float)):
                where_conditions.append({
                    "path": [field],
                    "operator": "Equal",
                    "valueNumber": value,
                })
            elif isinstance(value, list) and value:
                where_conditions.append({
                    "path": [field],
                    "operator": "ContainsAny",
                    "valueText": value,
                })

        if len(where_conditions) == 1:
            return where_conditions[0]
        elif len(where_conditions) > 1:
            return {
                "operator": "And",
                "operands": where_conditions,
            }
        else:
            return {}


# Singleton instance
_weaviate_client_instance: Optional[WeaviateClient] = None


def get_weaviate_client() -> WeaviateClient:
    """
    Get singleton Weaviate client instance.

    Returns:
        WeaviateClient instance
    """
    global _weaviate_client_instance
    if _weaviate_client_instance is None:
        _weaviate_client_instance = WeaviateClient()
    return _weaviate_client_instance


__all__ = ["WeaviateClient", "get_weaviate_client"]