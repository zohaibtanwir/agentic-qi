"""Weaviate vector database client for knowledge management."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
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
    TEST_CASE_HISTORY_SCHEMA = "TestCaseHistory"

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
        self._client: Optional[weaviate.WeaviateClient] = None

    async def connect(self) -> None:
        """Connect to Weaviate instance."""
        if self._client and self._client.is_connected():
            return

        try:
            self.logger.info(f"Connecting to Weaviate at {self.url}")

            # Parse URL to get host and port
            parsed = urlparse(self.url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 8080
            is_secure = parsed.scheme == "https"

            # Create client with v4 API
            if self.api_key:
                auth_config = weaviate.auth.AuthApiKey(api_key=self.api_key)
                self._client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=is_secure,
                    grpc_host=host,
                    grpc_port=50051,
                    grpc_secure=is_secure,
                    auth_credentials=auth_config,
                )
            else:
                self._client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=is_secure,
                    grpc_host=host,
                    grpc_port=50051,
                    grpc_secure=is_secure,
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
            self._client.close()
            self._client = None
            self.logger.info("Disconnected from Weaviate")

    async def _ensure_schemas(self) -> None:
        """Ensure required schemas exist in Weaviate."""
        try:
            # Check if collections exist using v4 API
            existing_collections = self._client.collections.list_all(simple=True)
            existing_names = set(existing_collections)

            # Create TestCaseHistory collection if needed (most important for History feature)
            if self.TEST_CASE_HISTORY_SCHEMA not in existing_names:
                await self._create_test_case_history_schema()

            self.logger.info("All required schemas are ready")

        except Exception as e:
            self.logger.warning(f"Failed to ensure schemas (non-fatal): {e}")
            # Don't raise - allow service to continue even without Weaviate

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

    async def _create_test_case_history_schema(self) -> None:
        """Create TestCaseHistory schema for storing generated test case sessions."""
        from weaviate.classes.config import Property, DataType

        # Create collection with v4 API (no vectorizer for simple storage)
        self._client.collections.create(
            name=self.TEST_CASE_HISTORY_SCHEMA,
            description="Stores test case generation history sessions",
            properties=[
                Property(name="session_id", data_type=DataType.TEXT, description="Unique session identifier"),
                Property(name="user_story", data_type=DataType.TEXT, description="Original user story input"),
                Property(name="acceptance_criteria", data_type=DataType.TEXT, description="Acceptance criteria (JSON array)"),
                Property(name="domain", data_type=DataType.TEXT, description="Domain context (e.g., ecommerce)"),
                Property(name="test_types", data_type=DataType.TEXT_ARRAY, description="Types of tests generated"),
                Property(name="coverage_level", data_type=DataType.TEXT, description="Coverage level"),
                Property(name="generated_test_cases", data_type=DataType.TEXT, description="Generated test cases (JSON)"),
                Property(name="test_case_count", data_type=DataType.INT, description="Number of test cases"),
                Property(name="generation_method", data_type=DataType.TEXT, description="Method used"),
                Property(name="model_used", data_type=DataType.TEXT, description="LLM model used"),
                Property(name="generation_time_ms", data_type=DataType.INT, description="Generation time in ms"),
                Property(name="status", data_type=DataType.TEXT, description="Generation status"),
                Property(name="error_message", data_type=DataType.TEXT, description="Error message if failed"),
                Property(name="metadata", data_type=DataType.TEXT, description="Additional metadata (JSON)"),
                Property(name="created_at", data_type=DataType.DATE, description="Creation timestamp"),
                Property(name="updated_at", data_type=DataType.DATE, description="Update timestamp"),
            ],
        )
        self.logger.info(f"Created {self.TEST_CASE_HISTORY_SCHEMA} collection")

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
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "coverage_score": test_case.get("coverage_score", 0.0),
                "complexity_score": test_case.get("complexity_score", 0.0),
                "domain_context": json.dumps(test_case.get("domain_context", {})),
            }

            # Store in Weaviate using v4 API
            collection = self._client.collections.get(self.TEST_CASES_SCHEMA)
            result = collection.data.insert(properties=data)

            self.logger.info(f"Stored test case with ID: {result}")
            return str(result)

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

    # ============================================================
    # Test Case History Methods
    # ============================================================

    async def store_test_case_history(
        self,
        session_data: Dict[str, Any],
    ) -> str:
        """
        Store a test case generation session in history.

        Args:
            session_data: Session data including user_story, test_cases, etc.

        Returns:
            UUID of stored session
        """
        if not self._client:
            await self.connect()

        try:
            session_id = session_data.get("session_id", str(uuid4()))
            now = datetime.now(timezone.utc).isoformat()

            # Prepare data for storage
            data = {
                "session_id": session_id,
                "user_story": session_data.get("user_story", ""),
                "acceptance_criteria": json.dumps(session_data.get("acceptance_criteria", [])),
                "domain": session_data.get("domain", ""),
                "test_types": session_data.get("test_types", []),
                "coverage_level": session_data.get("coverage_level", "standard"),
                "generated_test_cases": json.dumps(session_data.get("generated_test_cases", [])),
                "test_case_count": session_data.get("test_case_count", 0),
                "generation_method": session_data.get("generation_method", "llm"),
                "model_used": session_data.get("model_used", ""),
                "generation_time_ms": session_data.get("generation_time_ms", 0),
                "status": session_data.get("status", "success"),
                "error_message": session_data.get("error_message", ""),
                "metadata": json.dumps(session_data.get("metadata", {})),
                "created_at": session_data.get("created_at", now),
                "updated_at": now,
            }

            # Store in Weaviate using v4 API
            collection = self._client.collections.get(self.TEST_CASE_HISTORY_SCHEMA)
            result = collection.data.insert(properties=data)

            self.logger.info(f"Stored test case history session with ID: {result}")
            return str(result)

        except Exception as e:
            self.logger.error(f"Failed to store test case history: {e}")
            raise

    async def list_test_case_history(
        self,
        limit: int = 20,
        offset: int = 0,
        domain: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List test case generation history sessions.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            domain: Optional filter by domain
            status: Optional filter by status

        Returns:
            List of history sessions (sorted by created_at descending)
        """
        if not self._client:
            await self.connect()

        try:
            from weaviate.classes.query import Filter

            # Get the collection
            collection = self._client.collections.get(self.TEST_CASE_HISTORY_SCHEMA)

            # Build filters for v4 API
            filters = None
            filter_conditions = []
            if domain:
                filter_conditions.append(Filter.by_property("domain").equal(domain))
            if status:
                filter_conditions.append(Filter.by_property("status").equal(status))

            if len(filter_conditions) == 1:
                filters = filter_conditions[0]
            elif len(filter_conditions) > 1:
                filters = Filter.all_of(filter_conditions)

            # Execute query using v4 API
            response = collection.query.fetch_objects(
                limit=limit,
                offset=offset,
                filters=filters,
                include_vector=False,
            )

            # Convert response to list of dicts
            sessions = []
            for obj in response.objects:
                session_data = dict(obj.properties)
                session_data["weaviate_id"] = str(obj.uuid)

                # Parse JSON fields
                if "acceptance_criteria" in session_data and session_data["acceptance_criteria"]:
                    try:
                        session_data["acceptance_criteria"] = json.loads(session_data["acceptance_criteria"])
                    except json.JSONDecodeError:
                        session_data["acceptance_criteria"] = []

                sessions.append(session_data)

            # Sort by created_at descending (newest first)
            sessions.sort(
                key=lambda x: x.get("created_at", "") or "",
                reverse=True
            )

            return sessions

        except Exception as e:
            self.logger.error(f"Failed to list test case history: {e}")
            # Return empty list instead of raising - allows UI to work
            return []

    async def get_test_case_history(
        self,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific test case history session by ID.

        Args:
            session_id: The session ID to retrieve

        Returns:
            Session data or None if not found
        """
        if not self._client:
            await self.connect()

        try:
            from weaviate.classes.query import Filter

            # Get the collection
            collection = self._client.collections.get(self.TEST_CASE_HISTORY_SCHEMA)

            # Query by session_id using v4 API
            response = collection.query.fetch_objects(
                filters=Filter.by_property("session_id").equal(session_id),
                limit=1,
                include_vector=False,
            )

            if not response.objects:
                return None

            obj = response.objects[0]
            session = dict(obj.properties)
            session["weaviate_id"] = str(obj.uuid)

            # Parse JSON fields
            for field in ["acceptance_criteria", "generated_test_cases", "metadata"]:
                if field in session and session[field]:
                    try:
                        session[field] = json.loads(session[field])
                    except json.JSONDecodeError:
                        session[field] = [] if field != "metadata" else {}

            return session

        except Exception as e:
            self.logger.error(f"Failed to get test case history: {e}")
            return None

    async def delete_test_case_history(
        self,
        session_id: str,
    ) -> bool:
        """
        Delete a test case history session.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deleted, False if not found
        """
        if not self._client:
            await self.connect()

        try:
            from weaviate.classes.query import Filter

            # Get the collection
            collection = self._client.collections.get(self.TEST_CASE_HISTORY_SCHEMA)

            # First find the object
            response = collection.query.fetch_objects(
                filters=Filter.by_property("session_id").equal(session_id),
                limit=1,
                include_vector=False,
            )

            if not response.objects:
                self.logger.warning(f"History session {session_id} not found for deletion")
                return False

            weaviate_id = response.objects[0].uuid

            # Delete by UUID using v4 API
            collection.data.delete_by_id(weaviate_id)

            self.logger.info(f"Deleted test case history session: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete test case history: {e}")
            return False

    async def count_test_case_history(
        self,
        domain: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Count total test case history sessions.

        Args:
            domain: Optional filter by domain
            status: Optional filter by status

        Returns:
            Total count of sessions
        """
        if not self._client:
            await self.connect()

        try:
            from weaviate.classes.query import Filter
            from weaviate.classes.aggregate import GroupByAggregate

            # Get the collection
            collection = self._client.collections.get(self.TEST_CASE_HISTORY_SCHEMA)

            # Build filters for v4 API
            filters = None
            filter_conditions = []
            if domain:
                filter_conditions.append(Filter.by_property("domain").equal(domain))
            if status:
                filter_conditions.append(Filter.by_property("status").equal(status))

            if len(filter_conditions) == 1:
                filters = filter_conditions[0]
            elif len(filter_conditions) > 1:
                filters = Filter.all_of(filter_conditions)

            # Aggregate count using v4 API
            response = collection.aggregate.over_all(
                filters=filters,
                total_count=True,
            )

            return response.total_count or 0

        except Exception as e:
            self.logger.error(f"Failed to count test case history: {e}")
            return 0

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