"""gRPC client for eCommerce Domain Agent."""

from typing import Optional

import grpc

from requirement_analysis_agent.proto import ecommerce_domain_pb2 as pb2
from requirement_analysis_agent.proto import ecommerce_domain_pb2_grpc as pb2_grpc
from requirement_analysis_agent.utils.logging import get_logger


class DomainAgentError(Exception):
    """Error communicating with Domain Agent."""
    pass


class DomainAgentClient:
    """gRPC client for eCommerce Domain Agent service."""

    def __init__(self, host: str = "localhost", port: int = 50051):
        """
        Initialize Domain Agent client.

        Args:
            host: Domain Agent host
            port: Domain Agent port
        """
        self.host = host
        self.port = port
        self.address = f"{host}:{port}"
        self.logger = get_logger(__name__)
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[pb2_grpc.EcommerceDomainServiceStub] = None

    async def connect(self) -> None:
        """Establish connection to Domain Agent."""
        try:
            self._channel = grpc.aio.insecure_channel(self.address)
            self._stub = pb2_grpc.EcommerceDomainServiceStub(self._channel)
            self.logger.info("Connected to Domain Agent", address=self.address)
        except Exception as e:
            self.logger.error("Failed to connect to Domain Agent", error=str(e))
            raise DomainAgentError(f"Connection failed: {e}")

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
        if not self._stub:
            await self.connect()

        try:
            request = pb2.HealthCheckRequest()
            response = await self._stub.HealthCheck(request, timeout=5)
            return response.status == "healthy"
        except grpc.aio.AioRpcError as e:
            self.logger.warning("Domain Agent health check failed", error=str(e))
            return False

    async def get_entity(
        self,
        entity_name: str,
        include_relationships: bool = True,
        include_rules: bool = True,
        include_edge_cases: bool = False,
    ) -> Optional[dict]:
        """
        Get entity details from Domain Agent.

        Args:
            entity_name: Name of the entity
            include_relationships: Include entity relationships
            include_rules: Include business rules
            include_edge_cases: Include edge cases

        Returns:
            Entity details as dictionary, or None if not found
        """
        if not self._stub:
            await self.connect()

        try:
            request = pb2.EntityRequest(
                entity_name=entity_name,
                include_relationships=include_relationships,
                include_rules=include_rules,
                include_edge_cases=include_edge_cases,
            )
            response = await self._stub.GetEntity(request, timeout=10)

            if response.entity:
                return self._entity_to_dict(response.entity)
            return None

        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            self.logger.error("Failed to get entity", entity=entity_name, error=str(e))
            raise DomainAgentError(f"Failed to get entity: {e}")

    async def list_entities(self, category: str = "") -> list[dict]:
        """
        List all entities in the domain.

        Args:
            category: Optional category filter

        Returns:
            List of entity summaries
        """
        if not self._stub:
            await self.connect()

        try:
            request = pb2.ListEntitiesRequest(category=category)
            response = await self._stub.ListEntities(request, timeout=10)

            return [
                {
                    "name": e.name,
                    "description": e.description,
                    "category": e.category,
                    "field_count": e.field_count,
                }
                for e in response.entities
            ]
        except grpc.aio.AioRpcError as e:
            self.logger.error("Failed to list entities", error=str(e))
            raise DomainAgentError(f"Failed to list entities: {e}")

    async def query_knowledge(
        self,
        query: str,
        categories: Optional[list[str]] = None,
        max_results: int = 10,
    ) -> list[dict]:
        """
        Query domain knowledge.

        Args:
            query: Search query
            categories: Optional category filters
            max_results: Maximum number of results

        Returns:
            List of knowledge items
        """
        if not self._stub:
            await self.connect()

        try:
            request = pb2.KnowledgeRequest(
                request_id="",
                query=query,
                categories=categories or [],
                max_results=max_results,
            )
            response = await self._stub.QueryKnowledge(request, timeout=15)

            return [
                {
                    "id": item.id,
                    "category": item.category,
                    "title": item.title,
                    "content": item.content,
                    "relevance_score": item.relevance_score,
                    "metadata": dict(item.metadata),
                }
                for item in response.items
            ]
        except grpc.aio.AioRpcError as e:
            self.logger.error("Failed to query knowledge", query=query, error=str(e))
            raise DomainAgentError(f"Failed to query knowledge: {e}")

    async def get_domain_context(
        self,
        entity: str = "",
        workflow: str = "",
        scenario: str = "",
        aspects: Optional[list[str]] = None,
    ) -> dict:
        """
        Get domain context for analysis.

        Args:
            entity: Entity name
            workflow: Workflow name
            scenario: Scenario name
            aspects: Specific aspects to include

        Returns:
            Domain context dictionary
        """
        if not self._stub:
            await self.connect()

        try:
            request = pb2.DomainContextRequest(
                request_id="",
                entity=entity,
                workflow=workflow,
                scenario=scenario,
                aspects=aspects or [],
            )
            response = await self._stub.GetDomainContext(request, timeout=15)

            return {
                "context": response.context,
                "rules": [self._rule_to_dict(r) for r in response.rules],
                "relationships": [self._relationship_to_dict(r) for r in response.relationships],
                "edge_cases": list(response.edge_cases),
                "metadata": dict(response.metadata),
            }
        except grpc.aio.AioRpcError as e:
            self.logger.error("Failed to get domain context", error=str(e))
            raise DomainAgentError(f"Failed to get domain context: {e}")

    def _entity_to_dict(self, entity) -> dict:
        """Convert Entity protobuf to dictionary."""
        return {
            "name": entity.name,
            "description": entity.description,
            "fields": [
                {
                    "name": f.name,
                    "type": f.type,
                    "description": f.description,
                    "required": f.required,
                    "validations": list(f.validations),
                    "example": f.example,
                }
                for f in entity.fields
            ],
            "rules": [self._rule_to_dict(r) for r in entity.rules],
            "relationships": [self._relationship_to_dict(r) for r in entity.relationships],
            "edge_cases": list(entity.edge_cases),
            "test_scenarios": list(entity.test_scenarios),
        }

    def _rule_to_dict(self, rule) -> dict:
        """Convert BusinessRule protobuf to dictionary."""
        return {
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "entity": rule.entity,
            "condition": rule.condition,
            "constraint": rule.constraint,
            "severity": rule.severity,
        }

    def _relationship_to_dict(self, rel) -> dict:
        """Convert EntityRelationship protobuf to dictionary."""
        return {
            "source_entity": rel.source_entity,
            "target_entity": rel.target_entity,
            "relationship_type": rel.relationship_type,
            "description": rel.description,
            "required": rel.required,
        }

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._channel is not None and self._stub is not None
