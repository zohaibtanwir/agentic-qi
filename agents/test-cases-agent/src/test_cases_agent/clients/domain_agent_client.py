"""Domain Agent gRPC client implementation."""

import asyncio
from typing import Any, Dict, List, Optional

import grpc
from tenacity import retry, stop_after_attempt, wait_exponential

from test_cases_agent.config import get_settings
from test_cases_agent.proto import (
    ecommerce_domain_pb2,
    ecommerce_domain_pb2_grpc,
)
from test_cases_agent.utils.logging import get_logger


class DomainAgentClient:
    """Client for interacting with the Domain Agent service."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize Domain Agent client.

        Args:
            host: Domain Agent host (defaults to config)
            port: Domain Agent port (defaults to config)
        """
        settings = get_settings()
        self.host = host or settings.domain_agent_host
        self.port = port or settings.domain_agent_port
        self.address = f"{self.host}:{self.port}"
        self.logger = get_logger(__name__)
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[ecommerce_domain_pb2_grpc.DomainServiceStub] = None

    async def connect(self) -> None:
        """Establish connection to Domain Agent."""
        if self._channel:
            return

        try:
            self.logger.info(f"Connecting to Domain Agent at {self.address}")
            self._channel = grpc.aio.insecure_channel(
                self.address,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            self._stub = ecommerce_domain_pb2_grpc.EcommerceDomainServiceStub(self._channel)

            # Test connection with health check
            await self.health_check()
            self.logger.info("Successfully connected to Domain Agent")

        except Exception as e:
            self.logger.error(f"Failed to connect to Domain Agent: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Domain Agent."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
            self.logger.info("Disconnected from Domain Agent")

    async def health_check(self) -> bool:
        """
        Check if Domain Agent is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            request = ecommerce_domain_pb2.HealthCheckRequest()
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
    async def get_domain_context(
        self,
        entity_type: str,
        scenario: Optional[str] = None,
        include_rules: bool = True,
        include_relationships: bool = True,
        include_edge_cases: bool = True,
    ) -> Dict[str, Any]:
        """
        Get domain context for an entity.

        Args:
            entity_type: Type of entity (e.g., "order", "customer")
            scenario: Optional scenario for context
            include_rules: Include business rules
            include_relationships: Include entity relationships
            include_edge_cases: Include edge cases

        Returns:
            Domain context dictionary
        """
        if not self._stub:
            await self.connect()

        try:
            request = ecommerce_domain_pb2.DomainContextRequest(
                entity=entity_type,
                scenario=scenario,
            )

            response = await self._stub.GetDomainContext(
                request,
                timeout=30.0,
            )

            return {
                "entity_type": entity_type,  # Echo back the requested entity
                "description": response.context,  # Map context to description
                "business_rules": [rule.description for rule in response.rules],  # Extract rule descriptions
                "relationships": [
                    {
                        "entity": rel.target_entity,
                        "relationship_type": rel.relationship_type,
                        "cardinality": "1:N",  # Default since not in proto
                        "description": rel.description,
                    }
                    for rel in response.relationships
                ],
                "edge_cases": list(response.edge_cases),
                "constraints": [],  # Not in proto, return empty
                "validation_rules": [],  # Not in proto, return empty
                "metadata": dict(response.metadata) if response.metadata else {},
            }

        except grpc.RpcError as e:
            self.logger.error(
                f"Failed to get domain context: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting domain context: {e}")
            raise

    async def get_entity(
        self,
        entity_type: str,
        include_rules: bool = True,
        include_relationships: bool = True,
        include_edge_cases: bool = True,
    ) -> Dict[str, Any]:
        """
        Get detailed entity information.

        Args:
            entity_type: Type of entity
            include_rules: Include business rules
            include_relationships: Include relationships
            include_edge_cases: Include edge cases

        Returns:
            Entity information dictionary
        """
        if not self._stub:
            await self.connect()

        try:
            request = ecommerce_domain_pb2.EntityRequest(
                entity_name=entity_type,
                include_rules=include_rules,
                include_relationships=include_relationships,
                include_edge_cases=include_edge_cases,
            )

            response = await self._stub.GetEntity(
                request,
                timeout=30.0,
            )

            return {
                "entity_type": response.entity.name,  # Map name to entity_type
                "description": response.entity.description,
                "attributes": [
                    {
                        "name": field.name,
                        "type": field.type,
                        "required": field.required,
                        "description": field.description,
                        "constraints": list(field.validations),  # Map validations to constraints
                    }
                    for field in response.entity.fields  # Use fields not attributes
                ],
                "business_rules": [rule.description for rule in response.entity.rules],  # Extract descriptions
                "relationships": [rel.relationship_type for rel in response.entity.relationships],  # Extract types
                "edge_cases": list(response.entity.edge_cases),
            }

        except grpc.RpcError as e:
            self.logger.error(f"Failed to get entity: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting entity: {e}")
            raise

    async def get_workflow(
        self,
        workflow_name: str,
        include_validations: bool = True,
        include_edge_cases: bool = True,
    ) -> Dict[str, Any]:
        """
        Get workflow information.

        Args:
            workflow_name: Name of workflow
            include_validations: Include validation rules
            include_edge_cases: Include edge cases

        Returns:
            Workflow information dictionary
        """
        if not self._stub:
            await self.connect()

        try:
            request = ecommerce_domain_pb2.WorkflowRequest(
                workflow_name=workflow_name,
                include_steps=True,
                include_edge_cases=include_edge_cases,
            )

            response = await self._stub.GetWorkflow(
                request,
                timeout=30.0,
            )

            return {
                "workflow_name": response.workflow.name,
                "description": response.workflow.description,
                "steps": [
                    {
                        "step_number": step.order,  # Map order to step_number
                        "name": step.name,
                        "description": step.description,
                        "entity_type": step.entity,  # Map entity to entity_type
                        "action": step.action,
                        "validations": list(step.validations),
                        "next_steps": list(step.possible_outcomes),  # Map possible_outcomes to next_steps
                    }
                    for step in response.workflow.steps
                ],
                "entities_involved": list(response.workflow.involved_entities),
                "business_rules": [rule.description for rule in response.workflow.rules],  # Extract descriptions
                "edge_cases": list(response.workflow.edge_cases),
            }

        except grpc.RpcError as e:
            self.logger.error(f"Failed to get workflow: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting workflow: {e}")
            raise

    async def get_edge_cases(
        self,
        entity_type: Optional[str] = None,
        workflow_name: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get edge cases for entity or workflow.

        Args:
            entity_type: Optional entity type filter
            workflow_name: Optional workflow name filter
            severity: Optional severity filter
            category: Optional category filter

        Returns:
            List of edge case dictionaries
        """
        if not self._stub:
            await self.connect()

        try:
            request = ecommerce_domain_pb2.EdgeCasesRequest(
                entity=entity_type if entity_type else "",
                workflow=workflow_name if workflow_name else "",
                category=category if category else "",
            )

            response = await self._stub.GetEdgeCases(
                request,
                timeout=30.0,
            )

            return [
                {
                    "id": edge_case.id,
                    "entity_type": edge_case.entity,  # Map entity to entity_type
                    "workflow_name": edge_case.workflow,  # Map workflow to workflow_name
                    "description": edge_case.description,
                    "severity": edge_case.severity,
                    "category": edge_case.category,
                    "test_scenarios": [edge_case.test_approach],  # Map test_approach to list
                    "expected_behavior": edge_case.expected_behavior,
                    "business_impact": edge_case.expected_behavior,  # Use expected_behavior as business_impact
                }
                for edge_case in response.edge_cases
            ]

        except grpc.RpcError as e:
            self.logger.error(f"Failed to get edge cases: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting edge cases: {e}")
            raise

    async def generate_test_data(
        self,
        entity_type: str,
        count: int = 1,
        scenario: Optional[str] = None,
        include_edge_cases: bool = False,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Generate test data with domain context.

        This method proxies to the Test Data Agent with domain context.

        Args:
            entity_type: Type of entity to generate
            count: Number of records to generate
            scenario: Optional scenario for generation
            include_edge_cases: Include edge case data
            format: Output format (json, csv, etc.)

        Returns:
            Generated test data dictionary
        """
        if not self._stub:
            await self.connect()

        try:
            request = ecommerce_domain_pb2.GenerateTestDataRequest(
                entity=entity_type,
                count=count,
                workflow_context=scenario,
                include_edge_cases=include_edge_cases,
                output_format=format,
            )

            response = await self._stub.GenerateTestData(
                request,
                timeout=60.0,
            )

            return {
                "success": response.success,
                "data": response.data,
                "record_count": response.record_count,
                "metadata": dict(response.metadata) if response.metadata else {},
                "error_message": response.error_message if response.error_message else None,
            }

        except grpc.RpcError as e:
            self.logger.error(
                f"Failed to generate test data: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error generating test data: {e}")
            raise


# Singleton instance management
_domain_client_instance: Optional[DomainAgentClient] = None


def get_domain_agent_client() -> DomainAgentClient:
    """
    Get singleton Domain Agent client instance.

    Returns:
        DomainAgentClient instance
    """
    global _domain_client_instance
    if _domain_client_instance is None:
        _domain_client_instance = DomainAgentClient()
    return _domain_client_instance


__all__ = ["DomainAgentClient", "get_domain_agent_client"]