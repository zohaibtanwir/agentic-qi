"""Test Data Agent gRPC client implementation."""

import json
from typing import Any, Dict, List, Optional

import grpc
from tenacity import retry, stop_after_attempt, wait_exponential

from test_cases_agent.config import get_settings
from test_cases_agent.proto import test_data_pb2, test_data_pb2_grpc
from test_cases_agent.utils.logging import get_logger


class TestDataAgentClient:
    """Client for interacting with the Test Data Agent service."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize Test Data Agent client.

        Args:
            host: Test Data Agent host (defaults to config)
            port: Test Data Agent port (defaults to config)
        """
        settings = get_settings()
        self.host = host or settings.test_data_agent_host
        self.port = port or settings.test_data_agent_port
        self.address = f"{self.host}:{self.port}"
        self.logger = get_logger(__name__)
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[test_data_pb2_grpc.TestDataServiceStub] = None

    async def connect(self) -> None:
        """Establish connection to Test Data Agent."""
        if self._channel:
            return

        try:
            self.logger.info(f"Connecting to Test Data Agent at {self.address}")
            self._channel = grpc.aio.insecure_channel(
                self.address,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            self._stub = test_data_pb2_grpc.TestDataServiceStub(self._channel)

            # Test connection with health check
            await self.health_check()
            self.logger.info("Successfully connected to Test Data Agent")

        except Exception as e:
            self.logger.error(f"Failed to connect to Test Data Agent: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Test Data Agent."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
            self.logger.info("Disconnected from Test Data Agent")

    async def health_check(self) -> bool:
        """
        Check if Test Data Agent is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            request = test_data_pb2.HealthCheckRequest()
            response = await self._stub.HealthCheck(
                request,
                timeout=5.0,
            )
            return response.status == "SERVING"

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def generate_data(
        self,
        entity: str,
        count: int = 1,
        context: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        format: str = "json",
        include_metadata: bool = True,
        scenarios: Optional[List[str]] = None,
        relationships: Optional[List[str]] = None,
        edge_cases: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        inline_schema: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate test data from Test Data Agent.

        Args:
            entity: Entity type to generate
            count: Number of records to generate
            context: Optional context for generation
            constraints: Optional constraints dictionary
            format: Output format (json, csv, xml, yaml)
            include_metadata: Include generation metadata
            scenarios: List of scenarios to generate
            relationships: Related entities to include
            edge_cases: Edge cases to include
            custom_fields: Custom field specifications
            inline_schema: Inline schema definition

        Returns:
            Dictionary with generated data and metadata
        """
        if not self._stub:
            await self.connect()

        try:
            # Convert format string to enum
            format_map = {
                "json": test_data_pb2.JSON,
                "csv": test_data_pb2.CSV,
                "sql": test_data_pb2.SQL,
            }
            output_format_enum = format_map.get(format.lower(), test_data_pb2.JSON)

            # Build request
            request = test_data_pb2.GenerateRequest(
                entity=entity,
                count=count,
                output_format=output_format_enum,
            )

            if context:
                request.context = context

            if constraints:
                request.constraints = json.dumps(constraints)

            if scenarios:
                request.scenarios.extend(scenarios)

            if relationships:
                request.relationships.extend(relationships)

            if edge_cases:
                request.edge_cases.extend(edge_cases)

            if custom_fields:
                for key, value in custom_fields.items():
                    request.custom_fields[key] = json.dumps(value)

            if inline_schema:
                request.inline_schema = inline_schema

            # Make gRPC call
            response = await self._stub.GenerateData(
                request,
                timeout=60.0,
            )

            # Parse response
            result = {
                "success": response.success,
                "record_count": response.record_count,
            }

            # Parse data based on format
            if response.data:
                if format == "json":
                    try:
                        result["data"] = json.loads(response.data)
                    except json.JSONDecodeError:
                        result["data"] = response.data
                else:
                    result["data"] = response.data

            # Add metadata if present
            if response.metadata:
                result["metadata"] = {
                    "generation_path": response.metadata.generation_path,
                    "tokens_used": response.metadata.llm_tokens_used,
                    "coherence_score": response.metadata.coherence_score,
                    "generation_time_ms": response.metadata.generation_time_ms,
                }

            return result

        except grpc.RpcError as e:
            self.logger.error(
                f"Failed to generate data: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error generating data: {e}")
            raise

    async def get_schemas(
        self,
        entity_type: Optional[str] = None,
        include_examples: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get available schemas from Test Data Agent.

        Args:
            entity_type: Optional filter by domain (mapped from entity_type)
            include_examples: Include example data (ignored - not in proto)

        Returns:
            List of schema dictionaries
        """
        if not self._stub:
            await self.connect()

        try:
            request = test_data_pb2.GetSchemasRequest(
                domain=entity_type if entity_type else "",
            )

            response = await self._stub.GetSchemas(
                request,
                timeout=30.0,
            )

            schemas = []
            for schema in response.schemas:
                schema_dict = {
                    "name": schema.name,
                    "entity_type": schema.domain,  # Map domain to entity_type for backward compat
                    "description": schema.description,
                    "fields": [],
                    "version": "1.0",  # Default since not in proto
                    "tags": [],  # Default since not in proto
                }

                # Parse fields
                for field in schema.fields:
                    field_dict = {
                        "name": field.name,
                        "type": field.type,
                        "required": field.required,
                        "description": field.description,
                    }

                    if field.example:
                        field_dict["example"] = field.example

                    schema_dict["fields"].append(field_dict)

                schemas.append(schema_dict)

            return schemas

        except grpc.RpcError as e:
            self.logger.error(f"Failed to get schemas: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting schemas: {e}")
            raise

    async def validate_data(
        self,
        data: str,
        schema_name: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Validate data against a schema.

        Args:
            data: Data to validate (as string)
            schema_name: Name of schema to validate against
            format: Data format

        Returns:
            Validation result dictionary

        Raises:
            NotImplementedError: ValidateData RPC not yet implemented in proto
        """
        raise NotImplementedError(
            "ValidateData RPC is not implemented in test_data.proto. "
            "This method is planned for future implementation."
        )

    async def transform_data(
        self,
        data: str,
        source_format: str,
        target_format: str,
        transformation_rules: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Transform data between formats.

        Args:
            data: Source data
            source_format: Source format (json, csv, xml, yaml)
            target_format: Target format (json, csv, xml, yaml)
            transformation_rules: Optional transformation rules

        Returns:
            Transformed data as string

        Raises:
            NotImplementedError: TransformData RPC not yet implemented in proto
        """
        raise NotImplementedError(
            "TransformData RPC is not implemented in test_data.proto. "
            "This method is planned for future implementation."
        )

    async def get_generation_history(
        self,
        entity_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get generation history from Test Data Agent.

        Args:
            entity_type: Optional filter by entity type
            limit: Maximum number of records to return

        Returns:
            List of generation history records

        Raises:
            NotImplementedError: GetGenerationHistory RPC not yet implemented in proto
        """
        raise NotImplementedError(
            "GetGenerationHistory RPC is not implemented in test_data.proto. "
            "This method is planned for future implementation."
        )


# Singleton instance management
_test_data_client_instance: Optional[TestDataAgentClient] = None


def get_test_data_agent_client() -> TestDataAgentClient:
    """
    Get singleton Test Data Agent client instance.

    Returns:
        TestDataAgentClient instance
    """
    global _test_data_client_instance
    if _test_data_client_instance is None:
        _test_data_client_instance = TestDataAgentClient()
    return _test_data_client_instance


__all__ = ["TestDataAgentClient", "get_test_data_agent_client"]