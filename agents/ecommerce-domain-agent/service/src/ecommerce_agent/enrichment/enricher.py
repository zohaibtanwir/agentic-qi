"""Request enrichment for test data generation."""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

from ecommerce_agent.context.builder import DomainContextBuilder, DomainContext
from ecommerce_agent.knowledge.retriever import get_retriever, RetrievalResult
from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.domain.workflows import get_workflow
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EnrichmentResult:
    """Result of request enrichment."""

    enriched: bool
    context: str
    hints: List[str]
    scenarios: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class RequestEnricher:
    """Enriches test data generation requests with domain context."""

    def __init__(self, use_knowledge: bool = True):
        """
        Initialize the request enricher.

        Args:
            use_knowledge: Whether to use knowledge retrieval
        """
        self.context_builder = DomainContextBuilder(use_knowledge=use_knowledge)
        self.use_knowledge = use_knowledge
        if use_knowledge:
            try:
                self.retriever = get_retriever()
            except Exception as e:
                logger.warning("Knowledge retrieval not available", error=str(e))
                self.retriever = None
                self.use_knowledge = False
        else:
            self.retriever = None

    async def enrich_request(
        self,
        entity: str,
        count: int = 10,
        workflow: Optional[str] = None,
        scenario: Optional[str] = None,
        user_context: Optional[str] = None,
        user_scenarios: Optional[List[Dict[str, Any]]] = None,
        include_edge_cases: bool = True,
        production_like: bool = True,
    ) -> EnrichmentResult:
        """
        Enrich a test data generation request with domain context.

        Args:
            entity: Entity type (e.g., "cart", "order")
            count: Number of records to generate
            workflow: Optional workflow context
            scenario: Optional scenario type
            user_context: User-provided context
            user_scenarios: User-provided scenarios
            include_edge_cases: Whether to include edge cases
            production_like: Whether to mimic production distributions

        Returns:
            Enriched request with context, hints, scenarios, and constraints
        """
        try:
            # Build domain context
            logger.info(
                "Enriching request",
                entity=entity,
                workflow=workflow,
                scenario=scenario,
            )

            domain_context = await self.context_builder.build_context(
                entity=entity,
                workflow=workflow,
                scenario=scenario,
                include_edge_cases=include_edge_cases,
            )

            # Prepare enriched context
            enriched_context = self._build_enriched_context(
                domain_context,
                user_context,
            )

            # Prepare generation hints
            hints = self._build_hints(
                domain_context,
                scenario,
                production_like,
            )

            # Prepare scenarios
            scenarios = self._build_scenarios(
                domain_context,
                user_scenarios,
                count,
                include_edge_cases,
            )

            # Get constraints
            constraints = domain_context.constraints or {}

            # Build metadata
            metadata = self._build_metadata(
                domain_context,
                workflow,
                scenario,
            )

            # Add knowledge-based insights if available
            if self.use_knowledge and self.retriever:
                self._add_knowledge_insights(
                    entity,
                    workflow,
                    enriched_context,
                    metadata,
                )

            logger.info(
                "Request enriched successfully",
                entity=entity,
                scenarios_count=len(scenarios),
                hints_count=len(hints),
                constraints_count=len(constraints),
            )

            return EnrichmentResult(
                enriched=True,
                context=enriched_context,
                hints=hints,
                scenarios=scenarios,
                constraints=constraints,
                metadata=metadata,
            )

        except Exception as e:
            logger.error("Request enrichment failed", error=str(e))

            # Return minimal enrichment on failure
            return EnrichmentResult(
                enriched=False,
                context=user_context or f"Generate test data for {entity}",
                hints=["realistic"],
                scenarios=[{
                    "name": "default",
                    "count": count,
                    "description": "Default scenario",
                }],
                constraints={},
                metadata={"entity": entity},
                error=str(e),
            )

    def _build_enriched_context(
        self,
        domain_context: DomainContext,
        user_context: Optional[str],
    ) -> str:
        """Build enriched context string."""
        parts = []

        # Add natural language domain context
        if domain_context.natural_language_context:
            parts.append(domain_context.natural_language_context)

        # Add user context if provided
        if user_context:
            parts.append("\nUser Context:")
            parts.append(user_context)

        # Add field details
        if domain_context.fields:
            parts.append("\nField Requirements:")
            for field in domain_context.fields[:10]:  # Limit to avoid token overflow
                field_desc = f"- {field['name']}: {field['type']}"
                if field.get('required'):
                    field_desc += " (required)"
                if field.get('validations'):
                    field_desc += f" - validations: {', '.join(field['validations'])}"
                parts.append(field_desc)

        # Add relationship context
        if domain_context.relationships:
            parts.append("\nRelationships:")
            for rel in domain_context.relationships[:5]:
                rel_desc = f"- {rel['type']} {rel['target']}"
                if rel.get('description'):
                    rel_desc += f": {rel['description']}"
                parts.append(rel_desc)

        return "\n".join(parts)

    def _build_hints(
        self,
        domain_context: DomainContext,
        scenario: Optional[str],
        production_like: bool,
    ) -> List[str]:
        """Build generation hints."""
        hints = []

        # Add domain hints
        if domain_context.generation_hints:
            hints.extend(domain_context.generation_hints)

        # Add production-like hint
        if production_like:
            hints.append("production_like")
            hints.append("realistic_distributions")

        # Add scenario-specific hints
        if scenario:
            scenario_lower = scenario.lower()
            if "stress" in scenario_lower or "load" in scenario_lower:
                hints.append("high_volume")
                hints.append("performance_testing")
            elif "security" in scenario_lower:
                hints.append("security_testing")
                hints.append("injection_attempts")
            elif "boundary" in scenario_lower:
                hints.append("boundary_values")
                hints.append("edge_conditions")

        # Add entity-specific hints
        if domain_context.entity_name:
            entity_lower = domain_context.entity_name.lower()
            if "payment" in entity_lower:
                hints.append("pci_compliance")
                hints.append("secure_data")
            elif "user" in entity_lower or "customer" in entity_lower:
                hints.append("gdpr_compliance")
                hints.append("privacy_aware")

        # Deduplicate hints
        return list(set(hints))

    def _build_scenarios(
        self,
        domain_context: DomainContext,
        user_scenarios: Optional[List[Dict[str, Any]]],
        count: int,
        include_edge_cases: bool,
    ) -> List[Dict[str, Any]]:
        """Build test scenarios."""
        scenarios = []

        # Add user-provided scenarios first
        if user_scenarios:
            for scenario in user_scenarios:
                scenarios.append({
                    "name": scenario.get("name", "custom"),
                    "count": scenario.get("count", 1),
                    "description": scenario.get("description", "User-defined scenario"),
                    "overrides": scenario.get("overrides", {}),
                })

        # Extract scenarios from domain context
        domain_scenarios = self.context_builder.extract_scenarios_from_context(
            domain_context,
            requested_scenarios=None,
        )

        # Add domain scenarios if we have room
        remaining_count = count
        for scenario in user_scenarios or []:
            remaining_count -= scenario.get("count", 1)

        if remaining_count > 0 and domain_scenarios:
            # Distribute remaining count among domain scenarios
            per_scenario = max(1, remaining_count // len(domain_scenarios))

            for domain_scenario in domain_scenarios[:5]:  # Limit to 5 scenarios
                scenario_dict = {
                    "name": domain_scenario["name"],
                    "count": min(per_scenario, remaining_count),
                    "description": domain_scenario["description"],
                }

                # Add overrides for specific scenarios
                if "happy" in domain_scenario["name"].lower():
                    scenario_dict["overrides"] = {"all_valid": "true"}
                elif "edge" in domain_scenario["name"].lower():
                    scenario_dict["overrides"] = {"include_edge_cases": "true"}
                elif "error" in domain_scenario["name"].lower():
                    scenario_dict["overrides"] = {"inject_errors": "true"}

                scenarios.append(scenario_dict)
                remaining_count -= scenario_dict["count"]

                if remaining_count <= 0:
                    break

        # Ensure at least one scenario
        if not scenarios:
            scenarios.append({
                "name": "default",
                "count": count,
                "description": f"Default test data for {domain_context.entity_name}",
            })

        return scenarios

    def _build_metadata(
        self,
        domain_context: DomainContext,
        workflow: Optional[str],
        scenario: Optional[str],
    ) -> Dict[str, Any]:
        """Build enrichment metadata."""
        metadata = {
            "entity": domain_context.entity_name,
            "entity_description": domain_context.entity_description,
            "field_count": len(domain_context.fields),
            "relationship_count": len(domain_context.relationships),
            "business_rules_count": len(domain_context.business_rules),
            "edge_cases_count": len(domain_context.edge_cases),
        }

        if workflow:
            metadata["workflow"] = workflow
            if domain_context.workflow_steps:
                metadata["workflow_steps_count"] = len(domain_context.workflow_steps)

        if scenario:
            metadata["scenario"] = scenario

        return metadata

    def _add_knowledge_insights(
        self,
        entity: str,
        workflow: Optional[str],
        enriched_context: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Add insights from knowledge retrieval."""
        try:
            # Search for additional insights
            query = f"{entity} test data patterns"
            if workflow:
                query += f" {workflow}"

            results = self.retriever.search(query, max_results=3)

            if results:
                # Add insight count to metadata
                metadata["knowledge_insights"] = len(results)

                # Could enhance context with insights
                # For now, just log that we found relevant knowledge
                logger.debug(
                    "Found knowledge insights",
                    count=len(results),
                    entity=entity,
                )

        except Exception as e:
            logger.warning("Could not add knowledge insights", error=str(e))

    async def enrich_batch(
        self,
        requests: List[Dict[str, Any]],
    ) -> List[EnrichmentResult]:
        """
        Enrich multiple requests in batch.

        Args:
            requests: List of request dictionaries

        Returns:
            List of enrichment results
        """
        results = []

        for request in requests:
            result = await self.enrich_request(
                entity=request.get("entity", "unknown"),
                count=request.get("count", 10),
                workflow=request.get("workflow"),
                scenario=request.get("scenario"),
                user_context=request.get("context"),
                user_scenarios=request.get("scenarios"),
                include_edge_cases=request.get("include_edge_cases", True),
                production_like=request.get("production_like", True),
            )
            results.append(result)

        return results

    def validate_enrichment(
        self,
        result: EnrichmentResult,
    ) -> Tuple[bool, List[str]]:
        """
        Validate enrichment result.

        Args:
            result: Enrichment result to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if enrichment succeeded
        if not result.enriched:
            errors.append(f"Enrichment failed: {result.error}")

        # Validate context
        if not result.context or len(result.context) < 10:
            errors.append("Context is missing or too short")

        # Validate scenarios
        if not result.scenarios:
            errors.append("No scenarios provided")
        else:
            total_count = sum(s.get("count", 0) for s in result.scenarios)
            if total_count <= 0:
                errors.append("Total scenario count is zero or negative")

        # Validate hints
        if not result.hints:
            errors.append("No generation hints provided")

        is_valid = len(errors) == 0
        return is_valid, errors


def get_enricher(use_knowledge: bool = True) -> RequestEnricher:
    """Get a request enricher instance."""
    return RequestEnricher(use_knowledge=use_knowledge)