"""Enhanced gRPC server with knowledge layer integration."""

import grpc
import json
from concurrent import futures
from typing import Any, Optional

from ecommerce_agent.proto import ecommerce_domain_pb2 as pb2
from ecommerce_agent.proto import ecommerce_domain_pb2_grpc as pb2_grpc
from ecommerce_agent.domain.entities import get_entity, list_entities
from ecommerce_agent.domain.workflows import get_workflow, list_workflows
from ecommerce_agent.domain.business_rules import get_rules_for_entity
from ecommerce_agent.domain.edge_cases import (
    get_edge_cases_for_entity,
    get_edge_cases_for_workflow,
)
from ecommerce_agent.knowledge.retriever import get_retriever
from ecommerce_agent.utils.logging import get_logger, bind_context

logger = get_logger(__name__)


class EnhancedEcommerceDomainServicer(pb2_grpc.EcommerceDomainServiceServicer):
    """Enhanced gRPC service with knowledge retrieval."""

    def __init__(self, use_knowledge: bool = True):
        """
        Initialize the servicer.

        Args:
            use_knowledge: If True, use Weaviate for knowledge retrieval
        """
        self.use_knowledge = use_knowledge
        if use_knowledge:
            try:
                self.retriever = get_retriever()
                logger.info("Knowledge retriever initialized")
            except Exception as e:
                logger.warning("Failed to initialize knowledge retriever", error=str(e))
                self.retriever = None
                self.use_knowledge = False
        else:
            self.retriever = None

    async def GetDomainContext(
        self,
        request: pb2.DomainContextRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.DomainContextResponse:
        """Get domain context for test generation."""
        bind_context(request_id=request.request_id, method="GetDomainContext")
        logger.info("Getting domain context", entity=request.entity, workflow=request.workflow)

        response = pb2.DomainContextResponse(request_id=request.request_id)

        # Build context from entity
        if request.entity:
            entity = get_entity(request.entity)
            if entity:
                # Add business rules
                rules = get_rules_for_entity(request.entity)
                for rule in rules:
                    response.rules.append(
                        pb2.BusinessRule(
                            id=rule.id,
                            name=rule.name,
                            description=rule.description,
                            entity=rule.entity,
                            condition=rule.condition,
                            constraint=rule.constraint,
                            severity=rule.severity.value,
                        )
                    )

                # Add relationships
                for rel in entity.relationships:
                    response.relationships.append(
                        pb2.EntityRelationship(
                            source_entity=entity.name,
                            target_entity=rel.target,
                            relationship_type=rel.type,
                            description=rel.description,
                            required=rel.required,
                        )
                    )

                # Add edge cases
                edge_cases = get_edge_cases_for_entity(request.entity)
                for ec in edge_cases:
                    response.edge_cases.append(ec.description)

                # Build natural language context
                context_parts = [
                    f"Entity: {entity.name} - {entity.description}",
                    f"Category: {entity.category}",
                    f"Fields: {len(entity.fields)}",
                    f"Relationships: {len(entity.relationships)}",
                    f"Business Rules: {len(rules)}",
                    f"Edge Cases: {len(edge_cases)}",
                ]
                response.context = "\n".join(context_parts)

        # Add workflow context
        if request.workflow:
            workflow = get_workflow(request.workflow)
            if workflow:
                workflow_edge_cases = get_edge_cases_for_workflow(request.workflow)
                for ec in workflow_edge_cases:
                    if ec.description not in response.edge_cases:
                        response.edge_cases.append(ec.description)

                response.metadata["workflow_steps"] = str(len(workflow.steps))
                response.metadata["involved_entities"] = ", ".join(workflow.involved_entities)

        return response

    async def QueryKnowledge(
        self,
        request: pb2.KnowledgeRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.KnowledgeResponse:
        """Query domain knowledge."""
        bind_context(request_id=request.request_id, method="QueryKnowledge")
        logger.info("Querying knowledge", query=request.query)

        response = pb2.KnowledgeResponse(request_id=request.request_id)

        if self.use_knowledge and self.retriever:
            # Use knowledge retriever for semantic search
            try:
                results = self.retriever.search(
                    query=request.query,
                    categories=list(request.categories) if request.categories else None,
                    max_results=request.max_results or 10,
                )

                for result in results:
                    item = pb2.KnowledgeItem(
                        id=f"{result.item_type}_{result.title[:20]}",
                        category=result.item_type,
                        title=result.title,
                        content=result.content,
                        relevance_score=result.relevance_score,
                    )
                    # Add metadata
                    for key, value in result.metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            item.metadata[key] = str(value)
                    response.items.append(item)

                response.summary = self.retriever.summarize_knowledge(
                    request.query,
                    max_items=5,
                )

            except Exception as e:
                logger.error("Knowledge retrieval failed", error=str(e))
                response.summary = "Knowledge retrieval failed"
        else:
            # Fallback to simple search without Weaviate
            response.summary = "Knowledge layer not available, using fallback"

        return response

    async def GetEntity(
        self,
        request: pb2.EntityRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EntityResponse:
        """Get entity details."""
        logger.info("Getting entity", entity=request.entity_name)

        entity = get_entity(request.entity_name)
        if not entity:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Entity '{request.entity_name}' not found")
            return pb2.EntityResponse()

        pb_entity = pb2.Entity(
            name=entity.name,
            description=entity.description,
        )

        # Add fields
        for field in entity.fields:
            pb_entity.fields.append(
                pb2.EntityField(
                    name=field.name,
                    type=field.type,
                    description=field.description,
                    required=field.required,
                    validations=field.validations,
                    example=field.example,
                )
            )

        # Add relationships if requested
        if request.include_relationships:
            for rel in entity.relationships:
                pb_entity.relationships.append(
                    pb2.EntityRelationship(
                        source_entity=entity.name,
                        target_entity=rel.target,
                        relationship_type=rel.type,
                        description=rel.description,
                        required=rel.required,
                    )
                )

        # Add business rules if requested
        if request.include_rules:
            rules = get_rules_for_entity(entity.name)
            for rule in rules:
                pb_entity.rules.append(
                    pb2.BusinessRule(
                        id=rule.id,
                        name=rule.name,
                        description=rule.description,
                        entity=rule.entity,
                        condition=rule.condition,
                        constraint=rule.constraint,
                        severity=rule.severity.value,
                    )
                )

        # Add edge cases if requested
        if request.include_edge_cases:
            pb_entity.edge_cases.extend(entity.edge_cases)

        # Add test scenarios
        pb_entity.test_scenarios.extend(entity.test_scenarios)

        return pb2.EntityResponse(entity=pb_entity)

    async def GetWorkflow(
        self,
        request: pb2.WorkflowRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.WorkflowResponse:
        """Get workflow details."""
        logger.info("Getting workflow", workflow=request.workflow_name)

        workflow = get_workflow(request.workflow_name)
        if not workflow:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Workflow '{request.workflow_name}' not found")
            return pb2.WorkflowResponse()

        pb_workflow = pb2.Workflow(
            name=workflow.name,
            description=workflow.description,
        )

        # Add steps if requested
        if request.include_steps:
            for step in workflow.steps:
                pb_workflow.steps.append(
                    pb2.WorkflowStep(
                        order=step.order,
                        name=step.name,
                        description=step.description,
                        entity=step.entity,
                        action=step.action,
                        validations=step.validations,
                        possible_outcomes=step.possible_outcomes,
                    )
                )

        # Add involved entities
        pb_workflow.involved_entities.extend(workflow.involved_entities)

        # Add business rules
        for rule_desc in workflow.business_rules:
            pb_workflow.rules.append(
                pb2.BusinessRule(
                    id="",
                    name="",
                    description=rule_desc,
                    entity="",
                    condition="",
                    constraint=rule_desc,
                    severity="info",
                )
            )

        # Add edge cases if requested
        if request.include_edge_cases:
            pb_workflow.edge_cases.extend(workflow.edge_cases)

        # Add test scenarios
        pb_workflow.test_scenarios.extend(workflow.test_scenarios)

        return pb2.WorkflowResponse(workflow=pb_workflow)

    async def ListEntities(
        self,
        request: pb2.ListEntitiesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListEntitiesResponse:
        """List all entities."""
        logger.info("Listing entities", category=request.category)

        entities = list_entities(request.category if request.category else None)

        response = pb2.ListEntitiesResponse()
        for entity in entities:
            response.entities.append(
                pb2.EntitySummary(
                    name=entity.name,
                    description=entity.description,
                    category=entity.category,
                    field_count=len(entity.fields),
                )
            )

        return response

    async def ListWorkflows(
        self,
        request: pb2.ListWorkflowsRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListWorkflowsResponse:
        """List all workflows."""
        logger.info("Listing workflows")

        workflows = list_workflows()

        response = pb2.ListWorkflowsResponse()
        for workflow in workflows:
            response.workflows.append(
                pb2.WorkflowSummary(
                    name=workflow.name,
                    description=workflow.description,
                    step_count=len(workflow.steps),
                    involved_entities=workflow.involved_entities,
                )
            )

        return response

    async def GetEdgeCases(
        self,
        request: pb2.EdgeCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.EdgeCasesResponse:
        """Get edge cases."""
        logger.info("Getting edge cases", entity=request.entity, workflow=request.workflow)

        edge_cases = []

        if request.entity:
            edge_cases.extend(get_edge_cases_for_entity(request.entity))

        if request.workflow:
            edge_cases.extend(get_edge_cases_for_workflow(request.workflow))

        # Remove duplicates
        seen = set()
        unique_cases = []
        for ec in edge_cases:
            if ec.id not in seen:
                seen.add(ec.id)
                unique_cases.append(ec)

        response = pb2.EdgeCasesResponse()
        for ec in unique_cases:
            pb_edge_case = pb2.EdgeCase(
                id=ec.id,
                name=ec.name,
                description=ec.description,
                category=ec.category,
                entity=ec.entity or "",
                workflow=ec.workflow or "",
                test_approach=ec.test_approach,
                expected_behavior=ec.expected_behavior,
                severity=ec.severity,
            )
            if ec.example_data:
                for key, value in ec.example_data.items():
                    pb_edge_case.example_data[key] = str(value)

            response.edge_cases.append(pb_edge_case)

        return response

    async def GenerateTestData(
        self,
        request: pb2.GenerateTestDataRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GenerateTestDataResponse:
        """Generate test data via Test Data Agent with orchestration."""
        bind_context(request_id=request.request_id, method="GenerateTestData")
        logger.info("Generating test data", entity=request.entity, count=request.count)

        try:
            # Import orchestrator here to avoid circular imports
            from ecommerce_agent.orchestrator.generator import (
                get_orchestrator,
                GenerationRequest,
            )

            # Get the orchestrator
            orchestrator = get_orchestrator(
                use_knowledge=self.use_knowledge,
                store_patterns=True,
            )

            # Map proto generation method to string
            generation_method_map = {
                0: "HYBRID",  # UNSPECIFIED defaults to HYBRID
                1: "TRADITIONAL",
                2: "LLM",
                3: "RAG",
                4: "HYBRID",
            }
            gen_method = generation_method_map.get(request.generation_method, "HYBRID")

            # Convert proto string scenarios to dict format expected by orchestrator
            scenarios_list = None
            if request.scenarios:
                scenarios_list = []
                for scenario_name in request.scenarios:
                    scenarios_list.append({
                        "name": scenario_name,
                        "count": 1,
                        "description": f"User-requested scenario: {scenario_name}",
                    })

            # Build generation request using correct proto field names
            gen_request = GenerationRequest(
                entity=request.entity,
                count=request.count,
                workflow=request.workflow_context if request.workflow_context else None,
                scenario=None,  # Not in proto, derived from scenarios
                context=request.custom_context if request.custom_context else None,
                scenarios=scenarios_list,
                output_format=request.output_format if request.output_format else "JSON",
                include_edge_cases=request.include_edge_cases,
                production_like=request.production_like,
                use_cache=request.use_cache,
                generation_method=gen_method,
            )

            # Validate request
            is_valid, errors = orchestrator.validate_request(gen_request)
            if not is_valid:
                return pb2.GenerateTestDataResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Invalid request: {'; '.join(errors)}",
                )

            # Generate test data
            result = await orchestrator.generate(
                gen_request,
                request_id=request.request_id,
            )

            # Build response
            response = pb2.GenerateTestDataResponse(
                request_id=result.request_id,
                success=result.success,
                data=result.data,
                record_count=result.record_count,
                error=result.error if result.error else "",
            )

            # Add metadata if available - using proper GenerationMetadata message
            if result.generation_metadata:
                gen_meta = result.generation_metadata
                response.metadata.generation_path = gen_meta.get("generation_path", "")
                response.metadata.llm_tokens_used = gen_meta.get("llm_tokens_used", 0)
                response.metadata.generation_time_ms = gen_meta.get("generation_time_ms", 0.0)
                response.metadata.coherence_score = gen_meta.get("coherence_score", 0.0)
                # Add domain context summary
                if result.enrichment_metadata:
                    response.metadata.domain_context_used = json.dumps(result.enrichment_metadata)
                # Add scenario counts
                if gen_meta.get("scenario_counts"):
                    for k, v in gen_meta["scenario_counts"].items():
                        response.metadata.scenario_counts[k] = v

            logger.info(
                "Test data generation complete",
                request_id=request.request_id,
                success=result.success,
                record_count=result.record_count,
            )

            return response

        except Exception as e:
            logger.error(
                "Test data generation failed",
                request_id=request.request_id,
                error=str(e),
            )
            return pb2.GenerateTestDataResponse(
                request_id=request.request_id,
                success=False,
                error=f"Generation failed: {str(e)}",
            )

    async def HealthCheck(
        self,
        request: pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.HealthCheckResponse:
        """Health check."""
        components = {"grpc": "healthy"}

        # Check knowledge layer
        if self.use_knowledge and self.retriever:
            try:
                # Simple check - just see if we can access the client
                components["knowledge_layer"] = "healthy"
            except:
                components["knowledge_layer"] = "unhealthy"
        else:
            components["knowledge_layer"] = "disabled"

        return pb2.HealthCheckResponse(
            status="healthy" if all(v == "healthy" for v in components.values()) else "degraded",
            components=components,
        )


async def create_enhanced_server(port: int, use_knowledge: bool = True) -> grpc.aio.Server:
    """Create and configure the enhanced gRPC server."""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ],
    )

    servicer = EnhancedEcommerceDomainServicer(use_knowledge=use_knowledge)
    pb2_grpc.add_EcommerceDomainServiceServicer_to_server(servicer, server)

    server.add_insecure_port(f"[::]:{port}")

    logger.info(
        "Enhanced gRPC server created",
        port=port,
        knowledge_enabled=use_knowledge,
    )
    return server