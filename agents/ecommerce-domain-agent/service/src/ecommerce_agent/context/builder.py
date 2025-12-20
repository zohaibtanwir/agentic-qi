"""Domain context builder for enriching test data generation requests."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.domain.workflows import get_workflow, get_workflows_for_entity
from ecommerce_agent.domain.business_rules import get_rules_for_entity
from ecommerce_agent.domain.edge_cases import (
    get_edge_cases_for_entity,
    get_edge_cases_for_workflow,
)
from ecommerce_agent.knowledge.retriever import get_retriever
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DomainContext:
    """Complete domain context for test generation."""

    entity_name: str
    entity_description: str
    fields: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    business_rules: List[str]
    edge_cases: List[str]
    test_scenarios: List[str]
    workflow_context: Optional[str] = None
    workflow_steps: List[Dict[str, Any]] = None
    natural_language_context: str = ""
    constraints: Dict[str, Any] = None
    generation_hints: List[str] = None


class DomainContextBuilder:
    """Builds comprehensive domain context for test generation."""

    def __init__(self, use_knowledge: bool = True):
        """
        Initialize the context builder.

        Args:
            use_knowledge: Whether to use knowledge retrieval for enrichment
        """
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

    async def build_context(
        self,
        entity: str,
        workflow: Optional[str] = None,
        scenario: Optional[str] = None,
        aspects: Optional[List[str]] = None,
        include_edge_cases: bool = True,
    ) -> DomainContext:
        """
        Build comprehensive domain context.

        Args:
            entity: Entity name (e.g., "cart", "order")
            workflow: Optional workflow context (e.g., "checkout")
            scenario: Optional scenario (e.g., "happy_path", "edge_case")
            aspects: Specific aspects to include (e.g., ["business_rules", "relationships"])
            include_edge_cases: Whether to include edge cases

        Returns:
            Complete domain context for test generation
        """
        # Get entity definition
        entity_def = get_entity(entity)
        if not entity_def:
            logger.error("Entity not found", entity=entity)
            return self._empty_context(entity)

        # Initialize context
        context = DomainContext(
            entity_name=entity_def.name,
            entity_description=entity_def.description,
            fields=[],
            relationships=[],
            business_rules=[],
            edge_cases=[],
            test_scenarios=entity_def.test_scenarios,
            generation_hints=[],
        )

        # Add fields
        for field in entity_def.fields:
            context.fields.append({
                "name": field.name,
                "type": field.type,
                "description": field.description,
                "required": field.required,
                "example": field.example,
                "validations": field.validations,
            })

        # Add relationships
        for rel in entity_def.relationships:
            context.relationships.append({
                "target": rel.target,
                "type": rel.type,
                "description": rel.description,
                "required": rel.required,
            })

        # Add business rules
        rules = get_rules_for_entity(entity)
        for rule in rules:
            rule_text = f"{rule.id}: {rule.constraint} (Severity: {rule.severity.value})"
            context.business_rules.append(rule_text)

        # Add edge cases if requested
        if include_edge_cases:
            edge_cases = get_edge_cases_for_entity(entity)
            for ec in edge_cases:
                context.edge_cases.append(f"{ec.name}: {ec.description}")

        # Add workflow context if specified
        if workflow:
            self._add_workflow_context(context, workflow, include_edge_cases)

        # Add scenario-specific hints
        if scenario:
            self._add_scenario_hints(context, scenario)

        # Use knowledge retrieval for additional context
        if self.use_knowledge and self.retriever:
            self._enrich_with_knowledge(context, entity, workflow)

        # Build natural language context
        context.natural_language_context = self._build_natural_language(context)

        # Build constraints from business rules
        context.constraints = self._build_constraints(context)

        logger.info(
            "Built domain context",
            entity=entity,
            workflow=workflow,
            rules_count=len(context.business_rules),
            edge_cases_count=len(context.edge_cases),
        )

        return context

    def _add_workflow_context(
        self,
        context: DomainContext,
        workflow_name: str,
        include_edge_cases: bool,
    ) -> None:
        """Add workflow-specific context."""
        workflow = get_workflow(workflow_name)
        if not workflow:
            logger.warning("Workflow not found", workflow=workflow_name)
            return

        context.workflow_context = workflow_name
        context.workflow_steps = []

        for step in workflow.steps:
            context.workflow_steps.append({
                "order": step.order,
                "name": step.name,
                "description": step.description,
                "entity": step.entity,
                "action": step.action,
                "validations": step.validations,
                "possible_outcomes": step.possible_outcomes,
            })

        # Add workflow-specific edge cases
        if include_edge_cases:
            workflow_edge_cases = get_edge_cases_for_workflow(workflow_name)
            for ec in workflow_edge_cases:
                edge_case_text = f"{ec.name}: {ec.description}"
                if edge_case_text not in context.edge_cases:
                    context.edge_cases.append(edge_case_text)

        # Add workflow business rules
        for rule_desc in workflow.business_rules:
            if rule_desc not in context.business_rules:
                context.business_rules.append(rule_desc)

    def _add_scenario_hints(self, context: DomainContext, scenario: str) -> None:
        """Add scenario-specific generation hints."""
        scenario_lower = scenario.lower()

        if "happy" in scenario_lower or "success" in scenario_lower:
            context.generation_hints = ["realistic", "valid", "complete"]
        elif "edge" in scenario_lower:
            context.generation_hints = ["edge_case", "boundary", "unusual"]
        elif "error" in scenario_lower or "fail" in scenario_lower:
            context.generation_hints = ["invalid", "defect_triggering", "error_prone"]
        elif "stress" in scenario_lower or "load" in scenario_lower:
            context.generation_hints = ["high_volume", "concurrent", "stress"]
        else:
            context.generation_hints = ["realistic", "production_like"]

    def _enrich_with_knowledge(
        self,
        context: DomainContext,
        entity: str,
        workflow: Optional[str],
    ) -> None:
        """Enrich context with knowledge from RAG."""
        try:
            # Search for related patterns
            patterns = self.retriever.find_test_patterns(entity, scenario=None, limit=3)
            if patterns:
                logger.debug("Found test patterns", count=len(patterns))
                # Could add pattern-based hints or examples
                context.generation_hints.append("pattern_based")

            # Search for additional context
            if workflow:
                query = f"{entity} {workflow} test data"
            else:
                query = f"{entity} test data generation"

            knowledge_items = self.retriever.search(query, max_results=5)
            if knowledge_items:
                logger.debug("Found knowledge items", count=len(knowledge_items))
                # Could extract additional rules or scenarios

        except Exception as e:
            logger.warning("Knowledge enrichment failed", error=str(e))

    def _build_natural_language(self, context: DomainContext) -> str:
        """Build natural language context description."""
        parts = [
            f"Generate test data for {context.entity_name}: {context.entity_description}",
            "",
            "Entity Details:",
            f"- {len(context.fields)} fields defined",
            f"- {len(context.relationships)} relationships",
        ]

        if context.business_rules:
            parts.append("")
            parts.append("Business Rules to Honor:")
            for rule in context.business_rules[:5]:  # Limit to top 5
                parts.append(f"- {rule}")

        if context.workflow_context:
            parts.append("")
            parts.append(f"Workflow Context: {context.workflow_context}")
            if context.workflow_steps:
                parts.append(f"- {len(context.workflow_steps)} workflow steps")

        if context.edge_cases and len(context.edge_cases) > 0:
            parts.append("")
            parts.append("Consider Edge Cases:")
            for edge_case in context.edge_cases[:3]:  # Limit to top 3
                parts.append(f"- {edge_case}")

        if context.test_scenarios:
            parts.append("")
            parts.append(f"Suggested Scenarios: {', '.join(context.test_scenarios[:5])}")

        return "\n".join(parts)

    def _build_constraints(self, context: DomainContext) -> Dict[str, Any]:
        """Build field constraints from business rules."""
        constraints = {}

        # Parse business rules for constraints
        for field in context.fields:
            field_name = field["name"]
            field_type = field["type"]

            # Add basic type constraints
            if field_type == "integer":
                constraints[field_name] = {"min": 0, "max": 999999}
            elif field_type == "decimal":
                constraints[field_name] = {"min": 0.0, "max": 999999.99}
            elif field_type == "string":
                constraints[field_name] = {"min_length": 1, "max_length": 255}
            elif field_type == "enum":
                # Extract enum values from field description if available
                if ":" in field["description"]:
                    enum_part = field["description"].split(":")[-1]
                    if "," in enum_part:
                        values = [v.strip() for v in enum_part.split(",")]
                        constraints[field_name] = {"enum_values": values}

        # Apply specific constraints from business rules
        for rule in context.business_rules:
            if "quantity" in rule.lower() and "1-99" in rule:
                constraints["quantity"] = {"min": 1, "max": 99}
            elif "total" in rule.lower() and ">= $1.00" in rule:
                constraints["total"] = {"min": 1.00}
            elif "100 unique items" in rule:
                constraints["item_count"] = {"max": 100}

        return constraints

    def _empty_context(self, entity: str) -> DomainContext:
        """Return an empty context for unknown entities."""
        return DomainContext(
            entity_name=entity,
            entity_description=f"Unknown entity: {entity}",
            fields=[],
            relationships=[],
            business_rules=[],
            edge_cases=[],
            test_scenarios=[],
            natural_language_context=f"No domain knowledge available for entity: {entity}",
        )

    def extract_scenarios_from_context(
        self,
        context: DomainContext,
        requested_scenarios: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract scenario definitions from domain context.

        Args:
            context: Domain context
            requested_scenarios: Specific scenarios requested

        Returns:
            List of scenario definitions for Test Data Agent
        """
        scenarios = []

        if requested_scenarios:
            # Use requested scenarios
            for scenario_name in requested_scenarios:
                scenarios.append({
                    "name": scenario_name,
                    "count": 1,
                    "description": f"Test scenario: {scenario_name}",
                })
        else:
            # Generate scenarios from test_scenarios
            for scenario_name in context.test_scenarios[:5]:  # Limit to 5
                scenarios.append({
                    "name": scenario_name,
                    "count": 1,
                    "description": f"Domain scenario: {scenario_name}",
                })

        # Add edge case scenarios if present
        if context.edge_cases and len(scenarios) < 10:
            for edge_case in context.edge_cases[:2]:  # Add up to 2 edge cases
                ec_name = edge_case.split(":")[0].strip()
                scenarios.append({
                    "name": f"edge_{ec_name}",
                    "count": 1,
                    "description": edge_case,
                })

        # Ensure at least one scenario
        if not scenarios:
            scenarios.append({
                "name": "default",
                "count": 1,
                "description": "Default test data scenario",
            })

        return scenarios


def get_context_builder(use_knowledge: bool = True) -> DomainContextBuilder:
    """Get a domain context builder instance."""
    return DomainContextBuilder(use_knowledge=use_knowledge)