"""Test Data Agent gRPC client."""

import json
from typing import Any, Dict, List, Optional
import grpc
from grpc import aio

from ecommerce_agent.proto import test_data_pb2 as td_pb2
from ecommerce_agent.proto import test_data_pb2_grpc as td_pb2_grpc
from ecommerce_agent.config import get_settings
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


class TestDataAgentClient:
    """Client for Test Data Agent service."""

    def __init__(self):
        """Initialize the Test Data Agent client."""
        self.settings = get_settings()
        self.target = f"{self.settings.test_data_agent_host}:{self.settings.test_data_agent_port}"
        self._channel: Optional[aio.Channel] = None
        self._stub: Optional[td_pb2_grpc.TestDataServiceStub] = None

    async def connect(self) -> None:
        """Connect to Test Data Agent."""
        if not self._channel:
            self._channel = aio.insecure_channel(
                self.target,
                options=[
                    ("grpc.max_receive_message_length", 50 * 1024 * 1024),
                    ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ],
            )
            self._stub = td_pb2_grpc.TestDataServiceStub(self._channel)
            logger.info("Connected to Test Data Agent", target=self.target)

    async def close(self) -> None:
        """Close the connection."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
            logger.info("Disconnected from Test Data Agent")

    async def health_check(self) -> Dict[str, str]:
        """Check Test Data Agent health."""
        try:
            await self.connect()
            request = td_pb2.HealthCheckRequest()
            response = await self._stub.HealthCheck(
                request,
                timeout=self.settings.test_data_agent_timeout,
            )
            return {
                "status": response.status,
                "components": dict(response.components),
            }
        except grpc.RpcError as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def get_schemas(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available schemas from Test Data Agent."""
        try:
            await self.connect()
            request = td_pb2.GetSchemasRequest()
            if domain:
                request.domain = domain

            response = await self._stub.GetSchemas(
                request,
                timeout=self.settings.test_data_agent_timeout,
            )

            schemas = []
            for schema_info in response.schemas:
                schemas.append({
                    "name": schema_info.name,
                    "domain": schema_info.domain,
                    "description": schema_info.description,
                    "fields": list(schema_info.fields),
                })

            return schemas

        except grpc.RpcError as e:
            logger.error("Failed to get schemas", error=str(e))
            return []

    async def generate_data(
        self,
        request_id: str,
        domain: str,
        entity: str,
        count: int,
        context: str,
        hints: List[str],
        scenarios: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None,
        output_format: str = "JSON",
        use_cache: bool = True,
        production_like: bool = True,
        custom_schema: Optional[Dict[str, Any]] = None,
        generation_method: str = "HYBRID",
    ) -> Dict[str, Any]:
        """
        Generate test data via Test Data Agent.

        Args:
            request_id: Unique request identifier
            domain: Domain (e.g., "ecommerce")
            entity: Entity type (e.g., "cart", "order")
            count: Number of records to generate
            context: Natural language context for generation
            hints: Generation hints (e.g., ["realistic", "edge_case"])
            scenarios: List of scenario definitions
            constraints: Field constraints
            output_format: Output format (JSON, CSV, SQL)
            use_cache: Whether to use cached patterns
            production_like: Whether to mimic production distributions

        Returns:
            Generation response with data and metadata
        """
        try:
            await self.connect()

            # Build the request
            request = td_pb2.GenerateRequest(
                request_id=request_id,
                domain=domain,
                entity=entity,
                count=count,
                context=context,
                hints=hints,
                output_format=self._map_output_format(output_format),
                use_cache=use_cache,
                production_like=production_like,
                generation_method=self._map_generation_method(generation_method),
            )

            # Add scenarios
            for scenario_dict in scenarios:
                scenario = td_pb2.Scenario(
                    name=scenario_dict.get("name", ""),
                    count=scenario_dict.get("count", 1),
                    description=scenario_dict.get("description", ""),
                )
                # Add overrides if present
                if "overrides" in scenario_dict:
                    for key, value in scenario_dict["overrides"].items():
                        scenario.overrides[key] = str(value)
                request.scenarios.append(scenario)

            # Add constraints if provided
            if constraints:
                request.constraints.CopyFrom(self._build_constraints(constraints))

            # Add custom schema if provided
            if custom_schema:
                # Convert custom schema to JSON string for transmission
                request.custom_schema = json.dumps(custom_schema)

            # Call Test Data Agent
            logger.info(
                "Calling Test Data Agent",
                request_id=request_id,
                entity=entity,
                count=count,
            )

            response = await self._stub.GenerateData(
                request,
                timeout=self.settings.test_data_agent_timeout,
            )

            # Process response
            result = {
                "request_id": response.request_id,
                "success": response.success,
                "data": response.data,
                "record_count": response.record_count,
                "error": response.error if response.error else None,
            }

            # Add metadata if present
            if response.metadata:
                result["metadata"] = {
                    "generation_path": response.metadata.generation_path,
                    "llm_tokens_used": response.metadata.llm_tokens_used,
                    "generation_time_ms": response.metadata.generation_time_ms,
                    "coherence_score": response.metadata.coherence_score,
                    "scenario_counts": dict(response.metadata.scenario_counts),
                }

            if response.success:
                logger.info(
                    "Test data generated successfully",
                    request_id=request_id,
                    record_count=response.record_count,
                )
            else:
                logger.error(
                    "Test data generation failed",
                    request_id=request_id,
                    error=response.error,
                )

            return result

        except grpc.RpcError as e:
            logger.error(
                "Test Data Agent call failed",
                request_id=request_id,
                error=str(e),
            )
            return {
                "request_id": request_id,
                "success": False,
                "error": f"RPC failed: {str(e)}",
                "record_count": 0,
            }

    async def generate_data_stream(
        self,
        request_id: str,
        domain: str,
        entity: str,
        count: int,
        context: str,
        **kwargs,
    ):
        """
        Generate test data with streaming (for large requests).

        This is an async generator that yields data chunks.
        """
        try:
            await self.connect()

            # Build request (similar to generate_data)
            request = td_pb2.GenerateRequest(
                request_id=request_id,
                domain=domain,
                entity=entity,
                count=count,
                context=context,
                **kwargs,
            )

            # Stream the response
            stream = self._stub.GenerateDataStream(request)

            async for chunk in stream:
                yield {
                    "request_id": chunk.request_id,
                    "data": chunk.data,
                    "chunk_index": chunk.chunk_index,
                    "is_final": chunk.is_final,
                }

        except grpc.RpcError as e:
            logger.error("Streaming failed", error=str(e))
            yield {
                "error": str(e),
                "is_final": True,
            }

    def _map_generation_method(self, method_str: str) -> td_pb2.GenerationMethod:
        """Map generation method string to proto enum."""
        mapping = {
            "TRADITIONAL": td_pb2.GenerationMethod.TRADITIONAL,
            "LLM": td_pb2.GenerationMethod.LLM,
            "RAG": td_pb2.GenerationMethod.RAG,
            "HYBRID": td_pb2.GenerationMethod.HYBRID,
        }
        return mapping.get(method_str.upper(), td_pb2.GenerationMethod.HYBRID)

    def _map_output_format(self, format_str: str) -> td_pb2.OutputFormat:
        """Map string format to protobuf enum."""
        format_map = {
            "JSON": td_pb2.OutputFormat.JSON,
            "CSV": td_pb2.OutputFormat.CSV,
            "SQL": td_pb2.OutputFormat.SQL,
        }
        return format_map.get(format_str.upper(), td_pb2.OutputFormat.JSON)

    def _build_constraints(self, constraints_dict: Dict[str, Any]) -> td_pb2.Constraints:
        """Build protobuf Constraints from dictionary."""
        constraints = td_pb2.Constraints()

        for field_name, constraint_dict in constraints_dict.items():
            field_constraint = td_pb2.FieldConstraint()

            if "min" in constraint_dict:
                field_constraint.min = float(constraint_dict["min"])
            if "max" in constraint_dict:
                field_constraint.max = float(constraint_dict["max"])
            if "enum_values" in constraint_dict:
                field_constraint.enum_values.extend(constraint_dict["enum_values"])
            if "regex" in constraint_dict:
                field_constraint.regex = constraint_dict["regex"]
            if "min_length" in constraint_dict:
                field_constraint.min_length = int(constraint_dict["min_length"])
            if "max_length" in constraint_dict:
                field_constraint.max_length = int(constraint_dict["max_length"])
            if "format" in constraint_dict:
                field_constraint.format = constraint_dict["format"]

            constraints.field_constraints[field_name].CopyFrom(field_constraint)

        return constraints

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Singleton instance
_test_data_client: Optional[TestDataAgentClient] = None


async def get_test_data_client() -> TestDataAgentClient:
    """Get singleton Test Data Agent client."""
    global _test_data_client
    if not _test_data_client:
        _test_data_client = TestDataAgentClient()
        await _test_data_client.connect()
    return _test_data_client