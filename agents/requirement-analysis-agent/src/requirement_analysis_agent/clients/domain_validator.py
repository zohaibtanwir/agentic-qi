"""Domain Validator - Validates requirements against domain knowledge."""

from typing import Optional

from requirement_analysis_agent.clients.domain_agent import DomainAgentClient, DomainAgentError
from requirement_analysis_agent.models import (
    ApplicableRule,
    DomainValidation,
    DomainWarning,
    EntityMapping,
    Severity,
)
from requirement_analysis_agent.utils.logging import get_logger


class DomainValidator:
    """Validates requirements against eCommerce domain knowledge."""

    def __init__(self, domain_client: DomainAgentClient):
        """
        Initialize domain validator.

        Args:
            domain_client: Domain Agent gRPC client
        """
        self.client = domain_client
        self.logger = get_logger(__name__)
        self._available_entities: Optional[list[dict]] = None

    async def validate(
        self,
        entities: list[str],
        domain: str = "ecommerce",
    ) -> DomainValidation:
        """
        Validate requirement entities against domain knowledge.

        Args:
            entities: List of entity names mentioned in requirement
            domain: Domain context (default: ecommerce)

        Returns:
            DomainValidation result
        """
        self.logger.info(
            "Validating entities against domain",
            entity_count=len(entities),
            domain=domain,
        )

        entities_found = []
        rules_applicable = []
        warnings = []

        # Check if domain agent is available
        is_healthy = await self._check_health()
        if not is_healthy:
            self.logger.warning("Domain Agent not available, skipping validation")
            return DomainValidation(
                valid=True,  # Don't block if domain agent unavailable
                entities_found=[],
                rules_applicable=[],
                warnings=[
                    DomainWarning(
                        type="service_unavailable",
                        message="Domain Agent is not available",
                        suggestion="Domain validation skipped - proceed with caution",
                    )
                ],
            )

        # Load available entities if not cached
        if self._available_entities is None:
            await self._load_available_entities()

        # Validate each entity
        for entity_name in entities:
            entity_result = await self._validate_entity(entity_name)
            if entity_result:
                mapping, entity_rules = entity_result
                entities_found.append(mapping)
                rules_applicable.extend(entity_rules)
            else:
                # Entity not found in domain
                warnings.append(
                    DomainWarning(
                        type="unknown_entity",
                        message=f"'{entity_name}' is not a recognized domain entity",
                        suggestion=f"Consider using a standard entity or defining '{entity_name}'",
                    )
                )

        # Determine validity
        # Valid if no critical warnings (unknown entities are warnings, not errors)
        valid = len([w for w in warnings if w.type == "critical"]) == 0

        result = DomainValidation(
            valid=valid,
            entities_found=entities_found,
            rules_applicable=rules_applicable,
            warnings=warnings,
        )

        self.logger.info(
            "Domain validation complete",
            valid=valid,
            entities_found=len(entities_found),
            rules_count=len(rules_applicable),
            warnings_count=len(warnings),
        )

        return result

    async def get_context_for_entities(
        self,
        entities: list[str],
    ) -> dict:
        """
        Get domain context for specific entities.

        Args:
            entities: List of entity names

        Returns:
            Combined domain context
        """
        contexts = []
        all_rules = []
        all_edge_cases = []

        for entity_name in entities:
            try:
                context = await self.client.get_domain_context(entity=entity_name)
                if context.get("context"):
                    contexts.append(context["context"])
                all_rules.extend(context.get("rules", []))
                all_edge_cases.extend(context.get("edge_cases", []))
            except DomainAgentError:
                continue

        return {
            "combined_context": "\n\n".join(contexts),
            "rules": all_rules,
            "edge_cases": list(set(all_edge_cases)),  # Deduplicate
        }

    async def query_relevant_knowledge(
        self,
        description: str,
        max_results: int = 5,
    ) -> list[dict]:
        """
        Query domain knowledge relevant to requirement description.

        Args:
            description: Requirement description text
            max_results: Maximum results to return

        Returns:
            List of relevant knowledge items
        """
        try:
            return await self.client.query_knowledge(
                query=description,
                max_results=max_results,
            )
        except DomainAgentError as e:
            self.logger.warning("Knowledge query failed", error=str(e))
            return []

    async def _check_health(self) -> bool:
        """Check if Domain Agent is healthy."""
        try:
            return await self.client.health_check()
        except Exception:
            return False

    async def _load_available_entities(self) -> None:
        """Load available entities from Domain Agent."""
        try:
            self._available_entities = await self.client.list_entities()
            self.logger.debug(
                "Loaded available entities",
                count=len(self._available_entities),
            )
        except DomainAgentError as e:
            self.logger.warning("Failed to load entities", error=str(e))
            self._available_entities = []

    async def _validate_entity(
        self,
        entity_name: str,
    ) -> Optional[tuple[EntityMapping, list[ApplicableRule]]]:
        """
        Validate a single entity against domain knowledge.

        Args:
            entity_name: Entity name to validate

        Returns:
            Tuple of (EntityMapping, list of ApplicableRule) or None if not found
        """
        # Normalize entity name for matching
        normalized = entity_name.lower().strip()

        # Check if entity exists in available entities
        matched_entity = None
        for entity in self._available_entities or []:
            if entity["name"].lower() == normalized:
                matched_entity = entity
                break
            # Also check for partial matches
            if normalized in entity["name"].lower() or entity["name"].lower() in normalized:
                matched_entity = entity
                break

        if not matched_entity:
            return None

        # Get full entity details
        try:
            entity_details = await self.client.get_entity(
                matched_entity["name"],
                include_rules=True,
            )
            if not entity_details:
                return None

            # Create entity mapping
            mapping = EntityMapping(
                term=entity_name,
                mapped_entity=entity_details["name"],
                confidence=1.0 if entity_name.lower() == entity_details["name"].lower() else 0.8,
                domain_description=entity_details["description"],
            )

            # Extract applicable rules
            rules = []
            for rule in entity_details.get("rules", []):
                rules.append(
                    ApplicableRule(
                        rule_id=rule["id"],
                        rule=rule["description"],
                        relevance=self._parse_severity(rule.get("severity", "medium")),
                    )
                )

            return mapping, rules

        except DomainAgentError as e:
            self.logger.warning(
                "Failed to get entity details",
                entity=entity_name,
                error=str(e),
            )
            return None

    def _parse_severity(self, severity: str) -> Severity:
        """Parse severity string to Severity enum."""
        severity = severity.lower()
        try:
            return Severity(severity)
        except ValueError:
            return Severity.MEDIUM
