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

            # Map output format string to enum
            output_format_map = {
                "JSON": td_pb2.OutputFormat.JSON,
                "CSV": td_pb2.OutputFormat.CSV,
                "SQL": td_pb2.OutputFormat.SQL,
            }
            output_format_enum = output_format_map.get(output_format, td_pb2.OutputFormat.JSON)

            # Map generation method string to enum
            gen_method_map = {
                "TRADITIONAL": td_pb2.GenerationMethod.TRADITIONAL,
                "LLM": td_pb2.GenerationMethod.LLM,
                "RAG": td_pb2.GenerationMethod.RAG,
                "HYBRID": td_pb2.GenerationMethod.HYBRID,
            }
            gen_method_enum = gen_method_map.get(generation_method, td_pb2.GenerationMethod.HYBRID)

            # Build the request
            request = td_pb2.GenerateRequest(
                request_id=request_id,
                domain=domain,
                entity=entity,
                count=count,
                context=context,
                output_format=output_format_enum,
                generation_method=gen_method_enum,
                production_like=production_like,
                use_cache=use_cache,
            )

            # Add scenarios as Scenario messages
            for scenario in scenarios:
                if isinstance(scenario, dict):
                    scenario_msg = td_pb2.Scenario(
                        name=scenario.get("name", ""),
                        count=scenario.get("count", 0),
                        description=scenario.get("description", ""),
                    )
                    # Add overrides if present
                    if "overrides" in scenario:
                        for k, v in scenario["overrides"].items():
                            scenario_msg.overrides[k] = str(v)
                    request.scenarios.append(scenario_msg)
                elif isinstance(scenario, str):
                    # Handle string scenarios (convert to Scenario message)
                    request.scenarios.append(td_pb2.Scenario(name=scenario))

            # Note: Constraints message doesn't exist in current proto
            # If needed, constraints can be passed via context field

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

    # Note: GenerationMethod, OutputFormat enums, and Constraints message
    # don't exist in current test_data.proto
    # The proto uses simple string fields for format and scenarios

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