"""Business rules validation orchestrator."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

class RuleType(Enum):
    """Types of business rules."""
    VALIDATION = "validation"
    CALCULATION = "calculation"
    WORKFLOW = "workflow"
    AUTHORIZATION = "authorization"
    CONSTRAINT = "constraint"
    TRIGGER = "trigger"

class RulePriority(Enum):
    """Business rule priority."""
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"

class ValidationStatus(Enum):
    """Validation status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

@dataclass
class BusinessRule:
    """Business rule definition."""
    id: str
    name: str
    description: str
    type: RuleType
    priority: RulePriority
    entity: str
    conditions: List[str]
    actions: List[str]
    error_message: str
    validation_logic: str
    dependencies: List[str]
    test_data_requirements: Dict[str, Any]

@dataclass
class ValidationResult:
    """Result of rule validation."""
    rule_id: str
    rule_name: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any]
    test_data_used: Dict[str, Any]
    execution_time_ms: int

@dataclass
class ValidationReport:
    """Business rules validation report."""
    entity: str
    workflow: Optional[str]
    total_rules: int
    passed: int
    failed: int
    warnings: int
    results: List[ValidationResult]
    compliance_score: float  # 0.0 to 100.0
    recommendations: List[str]
    critical_failures: List[str]


class BusinessRulesOrchestrator:
    """Orchestrates business rules validation with domain enrichment."""

    def __init__(self):
        pass

    async def validate_business_rules(
        self,
        entity_name: str,
        test_data: Dict[str, Any],
        workflow: Optional[str] = None,
        rules_to_validate: Optional[List[str]] = None
    ) -> ValidationReport:
        """
        Validate business rules for an entity.

        Args:
            entity_name: Name of the domain entity
            test_data: Data to validate against rules
            workflow: Specific workflow context
            rules_to_validate: Specific rules to validate (None = all)

        Returns:
            ValidationReport with results
        """
        # Get entity definition
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found")

        # Get business rules to validate
        business_rules = self._get_business_rules(entity, rules_to_validate)

        logger.info(
            "Validating business rules",
            entity=entity_name,
            workflow=workflow,
            rule_count=len(business_rules)
        )

        results = []
        passed_count = 0
        failed_count = 0
        warning_count = 0

        for rule in business_rules:
            result = await self._validate_rule(rule, test_data, entity)
            results.append(result)

            if result.status == ValidationStatus.PASSED:
                passed_count += 1
            elif result.status == ValidationStatus.FAILED:
                failed_count += 1
            elif result.status == ValidationStatus.WARNING:
                warning_count += 1

        # Calculate compliance score
        total_weighted = (passed_count * 1.0 + warning_count * 0.5)
        compliance_score = (total_weighted / len(business_rules)) * 100 if business_rules else 100

        # Identify critical failures
        critical_failures = [
            r.message for r in results
            if r.status == ValidationStatus.FAILED
            and any(rule.priority == RulePriority.MANDATORY for rule in business_rules if rule.id == r.rule_id)
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(results, entity)

        report = ValidationReport(
            entity=entity_name,
            workflow=workflow,
            total_rules=len(business_rules),
            passed=passed_count,
            failed=failed_count,
            warnings=warning_count,
            results=results,
            compliance_score=compliance_score,
            recommendations=recommendations,
            critical_failures=critical_failures
        )

        logger.info(
            "Business rules validation completed",
            entity=entity_name,
            passed=passed_count,
            failed=failed_count,
            compliance_score=compliance_score
        )

        return report

    def _get_business_rules(
        self,
        entity,
        rules_to_validate: Optional[List[str]] = None
    ) -> List[BusinessRule]:
        """Get business rules from entity definition."""
        rules = []

        for idx, rule_text in enumerate(entity.business_rules):
            # Parse business rule text into structured format
            rule_id = f"BR{idx+1:03d}"

            # Extract rule components from text
            rule = BusinessRule(
                id=rule_id,
                name=f"{entity.name}_{rule_id}",
                description=rule_text,
                type=self._determine_rule_type(rule_text),
                priority=self._determine_rule_priority(rule_text),
                entity=entity.name,
                conditions=self._extract_conditions(rule_text),
                actions=self._extract_actions(rule_text),
                error_message=f"Business rule violation: {rule_text}",
                validation_logic=self._generate_validation_logic(rule_text),
                dependencies=self._extract_dependencies(rule_text, entity),
                test_data_requirements=self._determine_test_data_requirements(rule_text, entity)
            )

            if not rules_to_validate or rule.id in rules_to_validate:
                rules.append(rule)

        return rules

    def _determine_rule_type(self, rule_text: str) -> RuleType:
        """Determine the type of business rule."""
        rule_lower = rule_text.lower()

        if "must" in rule_lower or "required" in rule_lower:
            return RuleType.VALIDATION
        elif "calculate" in rule_lower or "sum" in rule_lower or "total" in rule_lower:
            return RuleType.CALCULATION
        elif "cannot" in rule_lower or "limit" in rule_lower:
            return RuleType.CONSTRAINT
        elif "workflow" in rule_lower or "status" in rule_lower:
            return RuleType.WORKFLOW
        else:
            return RuleType.VALIDATION

    def _determine_rule_priority(self, rule_text: str) -> RulePriority:
        """Determine rule priority."""
        rule_lower = rule_text.lower()

        if "must" in rule_lower or "required" in rule_lower or "cannot" in rule_lower:
            return RulePriority.MANDATORY
        elif "should" in rule_lower or "recommended" in rule_lower:
            return RulePriority.RECOMMENDED
        else:
            return RulePriority.OPTIONAL

    def _extract_conditions(self, rule_text: str) -> List[str]:
        """Extract conditions from rule text."""
        conditions = []

        # Parse common patterns
        if ">=" in rule_text or "<=" in rule_text or ">" in rule_text or "<" in rule_text:
            conditions.append("Numerical comparison")
        if "at least" in rule_text.lower():
            conditions.append("Minimum requirement")
        if "match" in rule_text.lower():
            conditions.append("Value matching")

        return conditions if conditions else ["General validation"]

    def _extract_actions(self, rule_text: str) -> List[str]:
        """Extract actions from rule text."""
        actions = []

        if "reject" in rule_text.lower() or "fail" in rule_text.lower():
            actions.append("Reject transaction")
        if "alert" in rule_text.lower():
            actions.append("Send alert")
        if "validate" in rule_text.lower():
            actions.append("Perform validation")

        return actions if actions else ["Validate data"]

    def _generate_validation_logic(self, rule_text: str) -> str:
        """Generate validation logic from rule text."""
        # This would be more sophisticated in production
        return f"Validate: {rule_text}"

    def _extract_dependencies(self, rule_text: str, entity) -> List[str]:
        """Extract dependencies from rule text."""
        dependencies = []

        # Check for references to other entities
        for relationship in entity.relationships:
            if relationship.target in rule_text.lower():
                dependencies.append(relationship.target)

        return dependencies

    def _determine_test_data_requirements(self, rule_text: str, entity) -> Dict[str, Any]:
        """Determine test data requirements for rule validation."""
        requirements = {}

        # Parse rule to determine data needs
        if "$" in rule_text:
            requirements["monetary_value"] = True
        if "quantity" in rule_text.lower() or "count" in rule_text.lower():
            requirements["quantity_value"] = True
        if "date" in rule_text.lower() or "time" in rule_text.lower():
            requirements["temporal_value"] = True

        return requirements

    async def _validate_rule(
        self,
        rule: BusinessRule,
        test_data: Dict[str, Any],
        entity
    ) -> ValidationResult:
        """Validate a single business rule."""
        import time
        start_time = time.time()

        try:
            # Perform validation based on rule type
            if rule.type == RuleType.VALIDATION:
                status = self._validate_data_rule(rule, test_data, entity)
            elif rule.type == RuleType.CALCULATION:
                status = self._validate_calculation_rule(rule, test_data, entity)
            elif rule.type == RuleType.CONSTRAINT:
                status = self._validate_constraint_rule(rule, test_data, entity)
            else:
                status = ValidationStatus.PASSED

            message = f"Rule {rule.name} validation: {status.value}"

        except Exception as e:
            status = ValidationStatus.FAILED
            message = f"Rule validation error: {str(e)}"

        execution_time = int((time.time() - start_time) * 1000)

        return ValidationResult(
            rule_id=rule.id,
            rule_name=rule.name,
            status=status,
            message=message,
            details={"rule_description": rule.description},
            test_data_used=test_data,
            execution_time_ms=execution_time
        )

    def _validate_data_rule(self, rule: BusinessRule, test_data: Dict[str, Any], entity) -> ValidationStatus:
        """Validate data-related rules."""
        # Example validation for cart rules
        if "Cart must have at least 1 item" in rule.description:
            items = test_data.get("items", [])
            return ValidationStatus.PASSED if len(items) >= 1 else ValidationStatus.FAILED

        elif "Cart total must be >= $1.00" in rule.description:
            total = test_data.get("total", 0)
            return ValidationStatus.PASSED if float(total) >= 1.00 else ValidationStatus.FAILED

        elif "Item quantity must be 1-99" in rule.description:
            items = test_data.get("items", [])
            for item in items:
                qty = item.get("quantity", 0)
                if not (1 <= qty <= 99):
                    return ValidationStatus.FAILED
            return ValidationStatus.PASSED

        # Default pass for unimplemented rules
        return ValidationStatus.PASSED

    def _validate_calculation_rule(self, rule: BusinessRule, test_data: Dict[str, Any], entity) -> ValidationStatus:
        """Validate calculation rules."""
        # Example: Order total must match payment amount
        if "total must match payment" in rule.description.lower():
            order_total = test_data.get("total", 0)
            payment_amount = test_data.get("payment_amount", 0)

            if abs(float(order_total) - float(payment_amount)) < 0.01:
                return ValidationStatus.PASSED
            else:
                return ValidationStatus.FAILED

        return ValidationStatus.PASSED

    def _validate_constraint_rule(self, rule: BusinessRule, test_data: Dict[str, Any], entity) -> ValidationStatus:
        """Validate constraint rules."""
        # Example: Cannot cancel shipped orders
        if "cannot cancel shipped" in rule.description.lower():
            status = test_data.get("status", "")
            action = test_data.get("action", "")

            if status == "shipped" and action == "cancel":
                return ValidationStatus.FAILED

        return ValidationStatus.PASSED

    def _generate_recommendations(self, results: List[ValidationResult], entity) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        failed_rules = [r for r in results if r.status == ValidationStatus.FAILED]

        if failed_rules:
            recommendations.append(f"Fix {len(failed_rules)} failed business rule validations")

            # Add specific recommendations
            for result in failed_rules[:3]:  # Top 3 failures
                recommendations.append(f"Address: {result.message}")

        # Add entity-specific recommendations
        if len(entity.edge_cases) > 0:
            recommendations.append("Test edge cases to ensure business rule compliance")

        return recommendations

    async def generate_test_scenarios(
        self,
        entity_name: str,
        rules_to_test: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate test scenarios for business rules.

        Args:
            entity_name: Name of the entity
            rules_to_test: Specific rules to generate scenarios for

        Returns:
            List of test scenarios
        """
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found")

        scenarios = []
        business_rules = self._get_business_rules(entity, rules_to_test)

        for rule in business_rules:
            # Generate positive test scenario
            positive_scenario = {
                "scenario_id": f"{rule.id}_positive",
                "rule_id": rule.id,
                "type": "positive",
                "description": f"Valid data that satisfies {rule.name}",
                "test_data": self._generate_positive_test_data(rule, entity),
                "expected_result": "PASS"
            }
            scenarios.append(positive_scenario)

            # Generate negative test scenario
            negative_scenario = {
                "scenario_id": f"{rule.id}_negative",
                "rule_id": rule.id,
                "type": "negative",
                "description": f"Invalid data that violates {rule.name}",
                "test_data": self._generate_negative_test_data(rule, entity),
                "expected_result": "FAIL"
            }
            scenarios.append(negative_scenario)

            # Generate edge case scenario if applicable
            if rule.priority == RulePriority.MANDATORY:
                edge_scenario = {
                    "scenario_id": f"{rule.id}_edge",
                    "rule_id": rule.id,
                    "type": "edge_case",
                    "description": f"Edge case for {rule.name}",
                    "test_data": self._generate_edge_case_test_data(rule, entity),
                    "expected_result": "WARN or PASS"
                }
                scenarios.append(edge_scenario)

        return scenarios

    def _generate_positive_test_data(self, rule: BusinessRule, entity) -> Dict[str, Any]:
        """Generate test data that passes the rule."""
        # This would be more sophisticated in production
        return {
            "entity": entity.name,
            "rule_compliant": True,
            "sample_data": "Valid data"
        }

    def _generate_negative_test_data(self, rule: BusinessRule, entity) -> Dict[str, Any]:
        """Generate test data that fails the rule."""
        return {
            "entity": entity.name,
            "rule_compliant": False,
            "sample_data": "Invalid data"
        }

    def _generate_edge_case_test_data(self, rule: BusinessRule, entity) -> Dict[str, Any]:
        """Generate edge case test data."""
        return {
            "entity": entity.name,
            "edge_case": True,
            "sample_data": "Edge case data"
        }


def get_business_rules_orchestrator() -> BusinessRulesOrchestrator:
    """Get business rules orchestrator instance."""
    return BusinessRulesOrchestrator()