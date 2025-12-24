import grpc
from concurrent import futures
from typing import Any

from ecommerce_agent.proto import ecommerce_domain_pb2 as pb2
from ecommerce_agent.proto import ecommerce_domain_pb2_grpc as pb2_grpc
from ecommerce_agent.utils.logging import get_logger, bind_context
from ecommerce_agent.domain.entities import list_entities, get_entity, EntityDefinition
from ecommerce_agent.domain.workflows import list_workflows, get_workflow, WorkflowDefinition

logger = get_logger(__name__)


def _entity_to_pb(entity: EntityDefinition) -> pb2.Entity:
    """Convert EntityDefinition to protobuf Entity."""
    fields = [
        pb2.EntityField(
            name=f.name,
            type=f.type,
            description=f.description,
            required=f.required,
            example=f.example or "",
        )
        for f in entity.fields
    ]
    relationships = [
        pb2.EntityRelationship(
            target_entity=r.target,
            relationship_type=r.type,
            description=r.description,
        )
        for r in entity.relationships
    ]
    # Convert business_rules strings to BusinessRule messages
    rules = [
        pb2.BusinessRule(
            id=f"BR{i+1:03d}",
            name=rule.split(":")[0].strip() if ":" in rule else f"Rule {i+1}",
            description=rule.split(":")[-1].strip() if ":" in rule else rule,
            entity=entity.name,
        )
        for i, rule in enumerate(entity.business_rules)
    ]
    return pb2.Entity(
        name=entity.name,
        description=entity.description,
        fields=fields,
        rules=rules,
        relationships=relationships,
        edge_cases=entity.edge_cases,
        test_scenarios=entity.test_scenarios,
    )


def _entity_to_summary_pb(entity: EntityDefinition) -> pb2.EntitySummary:
    """Convert EntityDefinition to protobuf EntitySummary."""
    return pb2.EntitySummary(
        name=entity.name,
        description=entity.description,
        category=entity.category,
        field_count=len(entity.fields),
    )


def _workflow_to_pb(workflow: WorkflowDefinition) -> pb2.Workflow:
    """Convert WorkflowDefinition to protobuf Workflow."""
    steps = [
        pb2.WorkflowStep(
            order=s.order,
            name=s.name,
            description=s.description,
            entity=s.entity,
            action=s.action,
            validations=s.validations,
            possible_outcomes=s.possible_outcomes,
        )
        for s in workflow.steps
    ]
    # Convert business_rules strings to BusinessRule messages
    rules = [
        pb2.BusinessRule(
            id=f"WBR{i+1:03d}",
            name=f"Workflow Rule {i+1}",
            description=rule,
        )
        for i, rule in enumerate(workflow.business_rules)
    ]
    return pb2.Workflow(
        name=workflow.name,
        description=workflow.description,
        steps=steps,
        involved_entities=workflow.involved_entities,
        rules=rules,
        edge_cases=workflow.edge_cases,
        test_scenarios=workflow.test_scenarios,
    )


def _workflow_to_summary_pb(workflow: WorkflowDefinition) -> pb2.WorkflowSummary:
    """Convert WorkflowDefinition to protobuf WorkflowSummary."""
    return pb2.WorkflowSummary(
        name=workflow.name,
        description=workflow.description,
        step_count=len(workflow.steps),
        involved_entities=workflow.involved_entities,
    )


class EcommerceDomainServicer(pb2_grpc.EcommerceDomainServiceServicer):
    """gRPC service implementation for eCommerce Domain Agent."""

    def __init__(self):
        """Initialize the servicer with dependencies."""
        # Dependencies will be injected later
        pass

    async def GetDomainContext(
        self,
        request: pb2.DomainContextRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.DomainContextResponse:
        """Get domain context for test generation."""
        bind_context(request_id=request.request_id, method="GetDomainContext")
        logger.info("Getting domain context", entity=request.entity, workflow=request.workflow)

        # TODO: Implement
        return pb2.DomainContextResponse(
            request_id=request.request_id,
            context="Domain context placeholder",
        )

    async def QueryKnowledge(
        self,
        request: pb2.KnowledgeRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.KnowledgeResponse:
        """Query domain knowledge."""
        bind_context(request_id=request.request_id, method="QueryKnowledge")
        logger.info("Querying knowledge", query=request.query)

        # TODO: Implement
        return pb2.KnowledgeResponse(
            request_id=request.request_id,
            items=[],
            summary="Knowledge query placeholder",
        )

    async def GetEntity(
        self,
        request: pb2.EntityRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EntityResponse:
        """Get entity details."""
        logger.info("Getting entity", entity=request.entity_name)

        entity = get_entity(request.entity_name)
        if entity:
            return pb2.EntityResponse(entity=_entity_to_pb(entity))
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Entity '{request.entity_name}' not found")
            return pb2.EntityResponse()

    async def GetWorkflow(
        self,
        request: pb2.WorkflowRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.WorkflowResponse:
        """Get workflow details."""
        logger.info("Getting workflow", workflow=request.workflow_name)

        workflow = get_workflow(request.workflow_name)
        if workflow:
            return pb2.WorkflowResponse(workflow=_workflow_to_pb(workflow))
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Workflow '{request.workflow_name}' not found")
            return pb2.WorkflowResponse()

    async def ListEntities(
        self,
        request: pb2.ListEntitiesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListEntitiesResponse:
        """List all entities."""
        category = request.category if request.category else None
        logger.info("Listing entities", category=category)

        entities = list_entities(category)
        pb_entities = [_entity_to_summary_pb(e) for e in entities]
        return pb2.ListEntitiesResponse(entities=pb_entities)

    async def ListWorkflows(
        self,
        request: pb2.ListWorkflowsRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListWorkflowsResponse:
        """List all workflows."""
        logger.info("Listing workflows")

        workflows = list_workflows()
        pb_workflows = [_workflow_to_summary_pb(w) for w in workflows]
        return pb2.ListWorkflowsResponse(workflows=pb_workflows)

    async def GetEdgeCases(
        self,
        request: pb2.EdgeCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EdgeCasesResponse:
        """Get edge cases."""
        logger.info("Getting edge cases", entity=request.entity, workflow=request.workflow)

        edge_case_strs = []
        entity_name = request.entity if request.entity else ""
        workflow_name = request.workflow if request.workflow else ""

        if request.entity:
            entity = get_entity(request.entity)
            if entity:
                edge_case_strs.extend(entity.edge_cases)
        if request.workflow:
            workflow = get_workflow(request.workflow)
            if workflow:
                edge_case_strs.extend(workflow.edge_cases)

        # Deduplicate and convert to EdgeCase messages
        seen = set()
        edge_cases = []
        for i, ec_str in enumerate(edge_case_strs):
            if ec_str not in seen:
                seen.add(ec_str)
                edge_cases.append(pb2.EdgeCase(
                    id=f"EC{i+1:03d}",
                    name=ec_str[:50] + "..." if len(ec_str) > 50 else ec_str,
                    description=ec_str,
                    entity=entity_name,
                    workflow=workflow_name,
                ))

        return pb2.EdgeCasesResponse(edge_cases=edge_cases)

    async def GenerateTestData(
        self,
        request: pb2.GenerateTestDataRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GenerateTestDataResponse:
        """Generate test data via Test Data Agent."""
        bind_context(request_id=request.request_id, method="GenerateTestData")
        logger.info("Generating test data", entity=request.entity, count=request.count)

        # TODO: Implement with Test Data Agent client
        return pb2.GenerateTestDataResponse(
            request_id=request.request_id,
            success=False,
            error="Not implemented yet",
        )

    async def HealthCheck(
        self,
        request: pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.HealthCheckResponse:
        """Health check."""
        return pb2.HealthCheckResponse(
            status="healthy",
            components={"grpc": "healthy"},
        )


async def create_server(port: int) -> grpc.aio.Server:
    """Create and configure the gRPC server."""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ],
    )

    servicer = EcommerceDomainServicer()
    pb2_grpc.add_EcommerceDomainServiceServicer_to_server(servicer, server)

    server.add_insecure_port(f"[::]:{port}")

    logger.info("gRPC server created", port=port)
    return server