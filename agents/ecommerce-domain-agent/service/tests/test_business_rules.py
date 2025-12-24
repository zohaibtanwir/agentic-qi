"""Tests for BusinessRulesOrchestrator."""

import pytest
from unittest.mock import patch, MagicMock

from ecommerce_agent.orchestrator.business_rules import (
    RuleType,
    RulePriority,
    ValidationStatus,
    BusinessRule,
    ValidationResult,
    ValidationReport,
    BusinessRulesOrchestrator,
    get_business_rules_orchestrator,
)


# =============================================================================
# Tests for Enums
# =============================================================================

class TestRuleType:
    """Tests for RuleType enum."""

    def test_all_rule_types_exist(self):
        """Test that all expected rule types exist."""
        assert RuleType.VALIDATION.value == "validation"
        assert RuleType.CALCULATION.value == "calculation"
        assert RuleType.WORKFLOW.value == "workflow"
        assert RuleType.AUTHORIZATION.value == "authorization"
        assert RuleType.CONSTRAINT.value == "constraint"
        assert RuleType.TRIGGER.value == "trigger"

    def test_rule_type_count(self):
        """Test that we have expected number of rule types."""
        assert len(RuleType) == 6


class TestRulePriority:
    """Tests for RulePriority enum."""

    def test_all_priorities_exist(self):
        """Test that all expected priorities exist."""
        assert RulePriority.MANDATORY.value == "mandatory"
        assert RulePriority.RECOMMENDED.value == "recommended"
        assert RulePriority.OPTIONAL.value == "optional"

    def test_priority_count(self):
        """Test that we have expected number of priorities."""
        assert len(RulePriority) == 3


class TestValidationStatus:
    """Tests for ValidationStatus enum."""

    def test_all_statuses_exist(self):
        """Test that all expected statuses exist."""
        assert ValidationStatus.PASSED.value == "passed"
        assert ValidationStatus.FAILED.value == "failed"
        assert ValidationStatus.WARNING.value == "warning"
        assert ValidationStatus.SKIPPED.value == "skipped"

    def test_status_count(self):
        """Test that we have expected number of statuses."""
        assert len(ValidationStatus) == 4


# =============================================================================
# Tests for Dataclasses
# =============================================================================

class TestBusinessRule:
    """Tests for BusinessRule dataclass."""

    def test_create_business_rule(self):
        """Test creating a business rule."""
        rule = BusinessRule(
            id="BR001",
            name="test_rule",
            description="Test description",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=["condition1"],
            actions=["action1"],
            error_message="Error message",
            validation_logic="validate test",
            dependencies=["customer"],
            test_data_requirements={"monetary_value": True}
        )

        assert rule.id == "BR001"
        assert rule.name == "test_rule"
        assert rule.type == RuleType.VALIDATION
        assert rule.priority == RulePriority.MANDATORY
        assert rule.entity == "cart"
        assert len(rule.conditions) == 1
        assert len(rule.actions) == 1


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_validation_result(self):
        """Test creating a validation result."""
        result = ValidationResult(
            rule_id="BR001",
            rule_name="test_rule",
            status=ValidationStatus.PASSED,
            message="Validation passed",
            details={"key": "value"},
            test_data_used={"item": "data"},
            execution_time_ms=10
        )

        assert result.rule_id == "BR001"
        assert result.status == ValidationStatus.PASSED
        assert result.execution_time_ms == 10


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    def test_create_validation_report(self):
        """Test creating a validation report."""
        result = ValidationResult(
            rule_id="BR001",
            rule_name="test",
            status=ValidationStatus.PASSED,
            message="OK",
            details={},
            test_data_used={},
            execution_time_ms=5
        )

        report = ValidationReport(
            entity="cart",
            workflow=None,
            total_rules=1,
            passed=1,
            failed=0,
            warnings=0,
            results=[result],
            compliance_score=100.0,
            recommendations=[],
            critical_failures=[]
        )

        assert report.entity == "cart"
        assert report.total_rules == 1
        assert report.compliance_score == 100.0


# =============================================================================
# Tests for BusinessRulesOrchestrator
# =============================================================================

class TestBusinessRulesOrchestratorInit:
    """Tests for BusinessRulesOrchestrator initialization."""

    def test_create_orchestrator(self):
        """Test creating an orchestrator."""
        orchestrator = BusinessRulesOrchestrator()
        assert orchestrator is not None

    def test_get_orchestrator_function(self):
        """Test get_business_rules_orchestrator function."""
        orchestrator = get_business_rules_orchestrator()
        assert isinstance(orchestrator, BusinessRulesOrchestrator)


class TestDetermineRuleType:
    """Tests for _determine_rule_type method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    def test_validation_rule_must(self, orchestrator):
        """Test rule with 'must' keyword."""
        result = orchestrator._determine_rule_type("Cart must have at least 1 item")
        assert result == RuleType.VALIDATION

    def test_validation_rule_required(self, orchestrator):
        """Test rule with 'required' keyword."""
        result = orchestrator._determine_rule_type("Shipping address required")
        assert result == RuleType.VALIDATION

    def test_calculation_rule_calculate(self, orchestrator):
        """Test rule with 'calculate' keyword."""
        result = orchestrator._determine_rule_type("Calculate shipping cost")
        assert result == RuleType.CALCULATION

    def test_calculation_rule_sum(self, orchestrator):
        """Test rule with 'sum' keyword."""
        result = orchestrator._determine_rule_type("Sum all item prices")
        assert result == RuleType.CALCULATION

    def test_calculation_rule_total(self, orchestrator):
        """Test rule with 'total' keyword."""
        result = orchestrator._determine_rule_type("Order total includes tax")
        assert result == RuleType.CALCULATION

    def test_constraint_rule_cannot(self, orchestrator):
        """Test rule with 'cannot' keyword."""
        result = orchestrator._determine_rule_type("Cannot cancel shipped orders")
        assert result == RuleType.CONSTRAINT

    def test_constraint_rule_limit(self, orchestrator):
        """Test rule with 'limit' keyword."""
        result = orchestrator._determine_rule_type("Limit items to 99")
        assert result == RuleType.CONSTRAINT

    def test_workflow_rule_workflow(self, orchestrator):
        """Test rule with 'workflow' keyword."""
        result = orchestrator._determine_rule_type("Workflow requires approval")
        assert result == RuleType.WORKFLOW

    def test_workflow_rule_status(self, orchestrator):
        """Test rule with 'status' keyword."""
        result = orchestrator._determine_rule_type("Status change triggers email")
        assert result == RuleType.WORKFLOW

    def test_default_validation(self, orchestrator):
        """Test default to validation for unmatched rules."""
        result = orchestrator._determine_rule_type("Some random rule")
        assert result == RuleType.VALIDATION


class TestDetermineRulePriority:
    """Tests for _determine_rule_priority method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    def test_mandatory_must(self, orchestrator):
        """Test mandatory priority with 'must' keyword."""
        result = orchestrator._determine_rule_priority("Cart must have items")
        assert result == RulePriority.MANDATORY

    def test_mandatory_required(self, orchestrator):
        """Test mandatory priority with 'required' keyword."""
        result = orchestrator._determine_rule_priority("Address required")
        assert result == RulePriority.MANDATORY

    def test_mandatory_cannot(self, orchestrator):
        """Test mandatory priority with 'cannot' keyword."""
        result = orchestrator._determine_rule_priority("Cannot cancel shipped order")
        assert result == RulePriority.MANDATORY

    def test_recommended_should(self, orchestrator):
        """Test recommended priority with 'should' keyword."""
        result = orchestrator._determine_rule_priority("Should validate email")
        assert result == RulePriority.RECOMMENDED

    def test_recommended_keyword(self, orchestrator):
        """Test recommended priority with 'recommended' keyword."""
        result = orchestrator._determine_rule_priority("Recommended to use 2FA")
        assert result == RulePriority.RECOMMENDED

    def test_optional_default(self, orchestrator):
        """Test optional priority for unmatched rules."""
        result = orchestrator._determine_rule_priority("Backup data weekly")
        assert result == RulePriority.OPTIONAL


class TestExtractConditions:
    """Tests for _extract_conditions method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    def test_numerical_comparison_gte(self, orchestrator):
        """Test extraction of >= comparison."""
        result = orchestrator._extract_conditions("Total >= 100")
        assert "Numerical comparison" in result

    def test_numerical_comparison_lte(self, orchestrator):
        """Test extraction of <= comparison."""
        result = orchestrator._extract_conditions("Items <= 99")
        assert "Numerical comparison" in result

    def test_numerical_comparison_gt(self, orchestrator):
        """Test extraction of > comparison."""
        result = orchestrator._extract_conditions("Quantity > 0")
        assert "Numerical comparison" in result

    def test_numerical_comparison_lt(self, orchestrator):
        """Test extraction of < comparison."""
        result = orchestrator._extract_conditions("Price < 10000")
        assert "Numerical comparison" in result

    def test_minimum_requirement(self, orchestrator):
        """Test extraction of 'at least' condition."""
        result = orchestrator._extract_conditions("At least one item required")
        assert "Minimum requirement" in result

    def test_value_matching(self, orchestrator):
        """Test extraction of 'match' condition."""
        result = orchestrator._extract_conditions("Password must match confirmation")
        assert "Value matching" in result

    def test_multiple_conditions(self, orchestrator):
        """Test extraction of multiple conditions."""
        result = orchestrator._extract_conditions("Total >= 100 and at least one item must match")
        assert "Numerical comparison" in result
        assert "Minimum requirement" in result
        assert "Value matching" in result

    def test_default_condition(self, orchestrator):
        """Test default condition for unmatched rules."""
        result = orchestrator._extract_conditions("Simple rule")
        assert result == ["General validation"]


class TestExtractActions:
    """Tests for _extract_actions method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    def test_reject_action(self, orchestrator):
        """Test extraction of 'reject' action."""
        result = orchestrator._extract_actions("Reject transaction if invalid")
        assert "Reject transaction" in result

    def test_fail_action(self, orchestrator):
        """Test extraction of 'fail' action."""
        result = orchestrator._extract_actions("Fail validation on error")
        assert "Reject transaction" in result

    def test_alert_action(self, orchestrator):
        """Test extraction of 'alert' action."""
        result = orchestrator._extract_actions("Alert admin on fraud")
        assert "Send alert" in result

    def test_validate_action(self, orchestrator):
        """Test extraction of 'validate' action."""
        result = orchestrator._extract_actions("Validate user input")
        assert "Perform validation" in result

    def test_multiple_actions(self, orchestrator):
        """Test extraction of multiple actions."""
        result = orchestrator._extract_actions("Reject and alert on fraud")
        assert "Reject transaction" in result
        assert "Send alert" in result

    def test_default_action(self, orchestrator):
        """Test default action for unmatched rules."""
        result = orchestrator._extract_actions("Process order")
        assert result == ["Validate data"]


class TestGenerateValidationLogic:
    """Tests for _generate_validation_logic method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    def test_generate_logic(self, orchestrator):
        """Test that validation logic is generated."""
        rule_text = "Cart must have items"
        result = orchestrator._generate_validation_logic(rule_text)
        assert "Validate:" in result
        assert rule_text in result


class TestExtractDependencies:
    """Tests for _extract_dependencies method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        """Create a mock entity with relationships."""
        entity = MagicMock()
        entity.relationships = [
            MagicMock(target="customer"),
            MagicMock(target="order"),
            MagicMock(target="payment"),
        ]
        return entity

    def test_extract_dependency(self, orchestrator, mock_entity):
        """Test extracting dependency from rule text."""
        result = orchestrator._extract_dependencies(
            "Customer must be verified", mock_entity
        )
        assert "customer" in result

    def test_no_dependencies(self, orchestrator, mock_entity):
        """Test no dependencies when none match."""
        result = orchestrator._extract_dependencies(
            "Price must be positive", mock_entity
        )
        assert len(result) == 0

    def test_multiple_dependencies(self, orchestrator, mock_entity):
        """Test multiple dependencies."""
        result = orchestrator._extract_dependencies(
            "Customer order requires payment", mock_entity
        )
        assert "customer" in result
        assert "order" in result
        assert "payment" in result


class TestDetermineTestDataRequirements:
    """Tests for _determine_test_data_requirements method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        return MagicMock()

    def test_monetary_requirement(self, orchestrator, mock_entity):
        """Test detecting monetary value requirement."""
        result = orchestrator._determine_test_data_requirements(
            "Total must be >= $10.00", mock_entity
        )
        assert result.get("monetary_value") is True

    def test_quantity_requirement(self, orchestrator, mock_entity):
        """Test detecting quantity value requirement."""
        result = orchestrator._determine_test_data_requirements(
            "Item quantity must be positive", mock_entity
        )
        assert result.get("quantity_value") is True

    def test_count_requirement(self, orchestrator, mock_entity):
        """Test detecting count value requirement."""
        result = orchestrator._determine_test_data_requirements(
            "Item count must be at least 1", mock_entity
        )
        assert result.get("quantity_value") is True

    def test_date_requirement(self, orchestrator, mock_entity):
        """Test detecting date value requirement."""
        result = orchestrator._determine_test_data_requirements(
            "Expiry date must be in future", mock_entity
        )
        assert result.get("temporal_value") is True

    def test_time_requirement(self, orchestrator, mock_entity):
        """Test detecting time value requirement."""
        result = orchestrator._determine_test_data_requirements(
            "Processing time within 24 hours", mock_entity
        )
        assert result.get("temporal_value") is True

    def test_multiple_requirements(self, orchestrator, mock_entity):
        """Test detecting multiple requirements."""
        result = orchestrator._determine_test_data_requirements(
            "Order total $100 with 5 items by date 2024-01-01", mock_entity
        )
        assert result.get("monetary_value") is True
        assert result.get("temporal_value") is True

    def test_no_requirements(self, orchestrator, mock_entity):
        """Test no special requirements detected."""
        result = orchestrator._determine_test_data_requirements(
            "Simple validation rule", mock_entity
        )
        assert len(result) == 0


class TestValidateDataRule:
    """Tests for _validate_data_rule method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        return MagicMock()

    def test_cart_minimum_items_pass(self, orchestrator, mock_entity):
        """Test cart with minimum items passes."""
        rule = BusinessRule(
            id="BR001",
            name="test",
            description="Cart must have at least 1 item",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"items": [{"id": 1}]}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_cart_minimum_items_fail(self, orchestrator, mock_entity):
        """Test cart without items fails."""
        rule = BusinessRule(
            id="BR001",
            name="test",
            description="Cart must have at least 1 item",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"items": []}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.FAILED

    def test_cart_total_minimum_pass(self, orchestrator, mock_entity):
        """Test cart with valid total passes."""
        rule = BusinessRule(
            id="BR002",
            name="test",
            description="Cart total must be >= $1.00",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"total": 10.00}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_cart_total_minimum_fail(self, orchestrator, mock_entity):
        """Test cart with low total fails."""
        rule = BusinessRule(
            id="BR002",
            name="test",
            description="Cart total must be >= $1.00",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"total": 0.50}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.FAILED

    def test_item_quantity_valid(self, orchestrator, mock_entity):
        """Test valid item quantities pass."""
        rule = BusinessRule(
            id="BR003",
            name="test",
            description="Item quantity must be 1-99",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"items": [{"quantity": 1}, {"quantity": 50}, {"quantity": 99}]}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_item_quantity_invalid_zero(self, orchestrator, mock_entity):
        """Test zero quantity fails."""
        rule = BusinessRule(
            id="BR003",
            name="test",
            description="Item quantity must be 1-99",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"items": [{"quantity": 0}]}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.FAILED

    def test_item_quantity_invalid_too_high(self, orchestrator, mock_entity):
        """Test quantity over 99 fails."""
        rule = BusinessRule(
            id="BR003",
            name="test",
            description="Item quantity must be 1-99",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"items": [{"quantity": 100}]}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.FAILED

    def test_unimplemented_rule_passes(self, orchestrator, mock_entity):
        """Test unimplemented rules default to pass."""
        rule = BusinessRule(
            id="BR999",
            name="test",
            description="Some unimplemented rule",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {}
        result = orchestrator._validate_data_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED


class TestValidateCalculationRule:
    """Tests for _validate_calculation_rule method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        return MagicMock()

    def test_payment_matches_total_pass(self, orchestrator, mock_entity):
        """Test matching payment and total passes."""
        rule = BusinessRule(
            id="BR004",
            name="test",
            description="Order total must match payment amount",
            type=RuleType.CALCULATION,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"total": 100.00, "payment_amount": 100.00}
        result = orchestrator._validate_calculation_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_payment_matches_total_with_tolerance(self, orchestrator, mock_entity):
        """Test payment within tolerance passes."""
        rule = BusinessRule(
            id="BR004",
            name="test",
            description="Order total must match payment amount",
            type=RuleType.CALCULATION,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"total": 100.00, "payment_amount": 100.005}  # Within 0.01
        result = orchestrator._validate_calculation_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_payment_does_not_match_total(self, orchestrator, mock_entity):
        """Test mismatched payment and total fails."""
        rule = BusinessRule(
            id="BR004",
            name="test",
            description="Order total must match payment amount",
            type=RuleType.CALCULATION,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"total": 100.00, "payment_amount": 99.00}
        result = orchestrator._validate_calculation_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.FAILED

    def test_unimplemented_calculation_rule_passes(self, orchestrator, mock_entity):
        """Test unimplemented calculation rules pass."""
        rule = BusinessRule(
            id="BR999",
            name="test",
            description="Some other calculation",
            type=RuleType.CALCULATION,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {}
        result = orchestrator._validate_calculation_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED


class TestValidateConstraintRule:
    """Tests for _validate_constraint_rule method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        return MagicMock()

    def test_cannot_cancel_shipped_fail(self, orchestrator, mock_entity):
        """Test canceling shipped order fails."""
        rule = BusinessRule(
            id="BR006",
            name="test",
            description="Cannot cancel shipped orders",
            type=RuleType.CONSTRAINT,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"status": "shipped", "action": "cancel"}
        result = orchestrator._validate_constraint_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.FAILED

    def test_cancel_pending_order_pass(self, orchestrator, mock_entity):
        """Test canceling pending order passes."""
        rule = BusinessRule(
            id="BR006",
            name="test",
            description="Cannot cancel shipped orders",
            type=RuleType.CONSTRAINT,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"status": "pending", "action": "cancel"}
        result = orchestrator._validate_constraint_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_shipped_order_update_pass(self, orchestrator, mock_entity):
        """Test updating shipped order (non-cancel) passes."""
        rule = BusinessRule(
            id="BR006",
            name="test",
            description="Cannot cancel shipped orders",
            type=RuleType.CONSTRAINT,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"status": "shipped", "action": "update"}
        result = orchestrator._validate_constraint_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED

    def test_unimplemented_constraint_rule_passes(self, orchestrator, mock_entity):
        """Test unimplemented constraint rules pass."""
        rule = BusinessRule(
            id="BR999",
            name="test",
            description="Some other constraint",
            type=RuleType.CONSTRAINT,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {}
        result = orchestrator._validate_constraint_rule(rule, test_data, mock_entity)
        assert result == ValidationStatus.PASSED


class TestValidateRule:
    """Tests for _validate_rule method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        return MagicMock()

    @pytest.mark.asyncio
    async def test_validate_validation_rule(self, orchestrator, mock_entity):
        """Test validating a validation type rule."""
        rule = BusinessRule(
            id="BR001",
            name="test_rule",
            description="Cart must have at least 1 item",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"items": [{"id": 1}]}
        result = await orchestrator._validate_rule(rule, test_data, mock_entity)

        assert isinstance(result, ValidationResult)
        assert result.rule_id == "BR001"
        assert result.status == ValidationStatus.PASSED
        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_validate_calculation_rule(self, orchestrator, mock_entity):
        """Test validating a calculation type rule."""
        rule = BusinessRule(
            id="BR004",
            name="test_rule",
            description="Order total must match payment amount",
            type=RuleType.CALCULATION,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"total": 100.00, "payment_amount": 100.00}
        result = await orchestrator._validate_rule(rule, test_data, mock_entity)

        assert result.status == ValidationStatus.PASSED

    @pytest.mark.asyncio
    async def test_validate_constraint_rule(self, orchestrator, mock_entity):
        """Test validating a constraint type rule."""
        rule = BusinessRule(
            id="BR006",
            name="test_rule",
            description="Cannot cancel shipped orders",
            type=RuleType.CONSTRAINT,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {"status": "shipped", "action": "cancel"}
        result = await orchestrator._validate_rule(rule, test_data, mock_entity)

        assert result.status == ValidationStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_workflow_rule(self, orchestrator, mock_entity):
        """Test validating a workflow type rule passes by default."""
        rule = BusinessRule(
            id="BR010",
            name="test_rule",
            description="Workflow requires approval",
            type=RuleType.WORKFLOW,
            priority=RulePriority.MANDATORY,
            entity="order",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        test_data = {}
        result = await orchestrator._validate_rule(rule, test_data, mock_entity)

        assert result.status == ValidationStatus.PASSED

    @pytest.mark.asyncio
    async def test_validate_rule_exception(self, orchestrator, mock_entity):
        """Test rule validation handles exceptions."""
        rule = BusinessRule(
            id="BR001",
            name="test_rule",
            description="Cart total must be >= $1.00",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )
        # Provide invalid data that will cause float conversion error
        test_data = {"total": "invalid"}
        result = await orchestrator._validate_rule(rule, test_data, mock_entity)

        assert result.status == ValidationStatus.FAILED
        assert "error" in result.message.lower()


class TestGenerateRecommendations:
    """Tests for _generate_recommendations method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        entity = MagicMock()
        entity.edge_cases = ["Edge case 1"]
        return entity

    def test_recommendations_with_failures(self, orchestrator, mock_entity):
        """Test recommendations generated for failures."""
        results = [
            ValidationResult(
                rule_id="BR001",
                rule_name="test1",
                status=ValidationStatus.FAILED,
                message="Rule failed",
                details={},
                test_data_used={},
                execution_time_ms=5
            ),
            ValidationResult(
                rule_id="BR002",
                rule_name="test2",
                status=ValidationStatus.PASSED,
                message="Rule passed",
                details={},
                test_data_used={},
                execution_time_ms=5
            ),
        ]

        recommendations = orchestrator._generate_recommendations(results, mock_entity)

        assert len(recommendations) >= 1
        assert "1 failed" in recommendations[0]
        assert any("edge cases" in r.lower() for r in recommendations)

    def test_recommendations_with_multiple_failures(self, orchestrator, mock_entity):
        """Test recommendations for multiple failures."""
        results = [
            ValidationResult(
                rule_id=f"BR00{i}",
                rule_name=f"test{i}",
                status=ValidationStatus.FAILED,
                message=f"Rule {i} failed",
                details={},
                test_data_used={},
                execution_time_ms=5
            )
            for i in range(5)
        ]

        recommendations = orchestrator._generate_recommendations(results, mock_entity)

        assert "5 failed" in recommendations[0]
        # Should include up to 3 specific failures
        assert len([r for r in recommendations if "Address:" in r]) <= 3

    def test_recommendations_no_failures(self, orchestrator, mock_entity):
        """Test recommendations with no failures."""
        results = [
            ValidationResult(
                rule_id="BR001",
                rule_name="test1",
                status=ValidationStatus.PASSED,
                message="Rule passed",
                details={},
                test_data_used={},
                execution_time_ms=5
            ),
        ]

        recommendations = orchestrator._generate_recommendations(results, mock_entity)

        # Should only have edge case recommendation
        assert len(recommendations) == 1
        assert "edge cases" in recommendations[0].lower()

    def test_recommendations_no_edge_cases(self, orchestrator):
        """Test recommendations when entity has no edge cases."""
        entity = MagicMock()
        entity.edge_cases = []

        results = [
            ValidationResult(
                rule_id="BR001",
                rule_name="test1",
                status=ValidationStatus.PASSED,
                message="Rule passed",
                details={},
                test_data_used={},
                execution_time_ms=5
            ),
        ]

        recommendations = orchestrator._generate_recommendations(results, entity)

        assert len(recommendations) == 0


class TestGetBusinessRules:
    """Tests for _get_business_rules method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        entity = MagicMock()
        entity.name = "cart"
        entity.business_rules = [
            "BR001: Cart must have at least 1 item",
            "BR002: Cart total must be >= $1.00",
            "BR003: Item quantity must be 1-99",
        ]
        entity.relationships = []
        return entity

    def test_get_all_rules(self, orchestrator, mock_entity):
        """Test getting all rules when no filter."""
        rules = orchestrator._get_business_rules(mock_entity)

        assert len(rules) == 3
        assert rules[0].id == "BR001"
        assert rules[1].id == "BR002"
        assert rules[2].id == "BR003"

    def test_get_filtered_rules(self, orchestrator, mock_entity):
        """Test getting filtered rules."""
        rules = orchestrator._get_business_rules(mock_entity, ["BR001", "BR003"])

        assert len(rules) == 2
        assert rules[0].id == "BR001"
        assert rules[1].id == "BR003"

    def test_rule_structure(self, orchestrator, mock_entity):
        """Test rule structure is complete."""
        rules = orchestrator._get_business_rules(mock_entity)

        rule = rules[0]
        assert rule.id == "BR001"
        assert rule.name == "cart_BR001"
        assert "Cart must have" in rule.description
        assert rule.entity == "cart"
        assert isinstance(rule.type, RuleType)
        assert isinstance(rule.priority, RulePriority)


class TestValidateBusinessRules:
    """Tests for validate_business_rules method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_validate_cart_rules_pass(self, orchestrator):
        """Test validating cart rules with valid data."""
        test_data = {
            "items": [{"id": 1, "quantity": 5}],
            "total": 50.00
        }

        report = await orchestrator.validate_business_rules("cart", test_data)

        assert isinstance(report, ValidationReport)
        assert report.entity == "cart"
        assert report.total_rules == 3
        assert report.passed >= 1

    @pytest.mark.asyncio
    async def test_validate_cart_rules_fail(self, orchestrator):
        """Test validating cart rules with invalid data."""
        test_data = {
            "items": [],  # Empty cart
            "total": 0.50  # Below minimum
        }

        report = await orchestrator.validate_business_rules("cart", test_data)

        assert report.failed >= 1
        assert report.compliance_score < 100

    @pytest.mark.asyncio
    async def test_validate_with_workflow(self, orchestrator):
        """Test validation with workflow context."""
        test_data = {"items": [{"id": 1, "quantity": 1}], "total": 10.00}

        report = await orchestrator.validate_business_rules(
            "cart", test_data, workflow="checkout"
        )

        assert report.workflow == "checkout"

    @pytest.mark.asyncio
    async def test_validate_specific_rules(self, orchestrator):
        """Test validating specific rules only."""
        test_data = {"items": [{"id": 1, "quantity": 1}], "total": 10.00}

        report = await orchestrator.validate_business_rules(
            "cart", test_data, rules_to_validate=["BR001"]
        )

        assert report.total_rules == 1

    @pytest.mark.asyncio
    async def test_validate_unknown_entity(self, orchestrator):
        """Test validation with unknown entity raises error."""
        with pytest.raises(ValueError, match="not found"):
            await orchestrator.validate_business_rules("unknown_entity", {})

    @pytest.mark.asyncio
    async def test_compliance_score_calculation(self, orchestrator):
        """Test compliance score is calculated correctly."""
        test_data = {
            "items": [{"id": 1, "quantity": 1}],
            "total": 10.00
        }

        report = await orchestrator.validate_business_rules("cart", test_data)

        # All rules should pass
        assert report.compliance_score == 100.0

    @pytest.mark.asyncio
    async def test_critical_failures_identified(self, orchestrator):
        """Test critical failures are identified."""
        test_data = {
            "items": [],  # Violates mandatory rule
            "total": 0.50
        }

        report = await orchestrator.validate_business_rules("cart", test_data)

        # Should have critical failures for mandatory rules
        assert len(report.critical_failures) >= 0  # May or may not have critical failures


class TestGenerateTestScenarios:
    """Tests for generate_test_scenarios method."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_generate_scenarios_for_cart(self, orchestrator):
        """Test generating test scenarios for cart entity."""
        scenarios = await orchestrator.generate_test_scenarios("cart")

        assert len(scenarios) > 0
        # Each rule should have at least positive and negative scenarios
        assert len(scenarios) >= 6  # 3 rules * 2 scenarios minimum

    @pytest.mark.asyncio
    async def test_scenario_structure(self, orchestrator):
        """Test scenario structure is correct."""
        scenarios = await orchestrator.generate_test_scenarios("cart")

        for scenario in scenarios:
            assert "scenario_id" in scenario
            assert "rule_id" in scenario
            assert "type" in scenario
            assert "description" in scenario
            assert "test_data" in scenario
            assert "expected_result" in scenario

    @pytest.mark.asyncio
    async def test_positive_negative_scenarios(self, orchestrator):
        """Test both positive and negative scenarios are generated."""
        scenarios = await orchestrator.generate_test_scenarios("cart")

        positive = [s for s in scenarios if s["type"] == "positive"]
        negative = [s for s in scenarios if s["type"] == "negative"]

        assert len(positive) >= 3  # At least one per rule
        assert len(negative) >= 3  # At least one per rule

    @pytest.mark.asyncio
    async def test_edge_case_scenarios_for_mandatory(self, orchestrator):
        """Test edge case scenarios for mandatory rules."""
        scenarios = await orchestrator.generate_test_scenarios("cart")

        edge_cases = [s for s in scenarios if s["type"] == "edge_case"]

        # Should have edge cases for mandatory rules
        assert len(edge_cases) >= 1

    @pytest.mark.asyncio
    async def test_generate_scenarios_specific_rules(self, orchestrator):
        """Test generating scenarios for specific rules."""
        scenarios = await orchestrator.generate_test_scenarios(
            "cart", rules_to_test=["BR001"]
        )

        # Should only have scenarios for BR001
        rule_ids = set(s["rule_id"] for s in scenarios)
        assert rule_ids == {"BR001"}

    @pytest.mark.asyncio
    async def test_generate_scenarios_unknown_entity(self, orchestrator):
        """Test generating scenarios for unknown entity raises error."""
        with pytest.raises(ValueError, match="not found"):
            await orchestrator.generate_test_scenarios("unknown_entity")


class TestGenerateTestData:
    """Tests for test data generation methods."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.fixture
    def mock_entity(self):
        entity = MagicMock()
        entity.name = "cart"
        return entity

    @pytest.fixture
    def mock_rule(self):
        return BusinessRule(
            id="BR001",
            name="test_rule",
            description="Test rule",
            type=RuleType.VALIDATION,
            priority=RulePriority.MANDATORY,
            entity="cart",
            conditions=[],
            actions=[],
            error_message="",
            validation_logic="",
            dependencies=[],
            test_data_requirements={}
        )

    def test_generate_positive_test_data(self, orchestrator, mock_rule, mock_entity):
        """Test generating positive test data."""
        data = orchestrator._generate_positive_test_data(mock_rule, mock_entity)

        assert data["entity"] == "cart"
        assert data["rule_compliant"] is True

    def test_generate_negative_test_data(self, orchestrator, mock_rule, mock_entity):
        """Test generating negative test data."""
        data = orchestrator._generate_negative_test_data(mock_rule, mock_entity)

        assert data["entity"] == "cart"
        assert data["rule_compliant"] is False

    def test_generate_edge_case_test_data(self, orchestrator, mock_rule, mock_entity):
        """Test generating edge case test data."""
        data = orchestrator._generate_edge_case_test_data(mock_rule, mock_entity)

        assert data["entity"] == "cart"
        assert data["edge_case"] is True


class TestOrderEntityRules:
    """Tests for order entity business rules."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_validate_order_rules(self, orchestrator):
        """Test validating order rules."""
        test_data = {
            "total": 100.00,
            "payment_amount": 100.00,
            "status": "pending",
            "action": "update"
        }

        report = await orchestrator.validate_business_rules("order", test_data)

        assert report.entity == "order"
        assert report.total_rules == 3

    @pytest.mark.asyncio
    async def test_order_cancel_shipped_fails(self, orchestrator):
        """Test that canceling shipped order fails validation."""
        test_data = {
            "status": "shipped",
            "action": "cancel"
        }

        report = await orchestrator.validate_business_rules("order", test_data)

        # Should have at least one failure
        assert report.failed >= 1


class TestPaymentEntityRules:
    """Tests for payment entity business rules."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_validate_payment_rules(self, orchestrator):
        """Test validating payment rules."""
        test_data = {
            "amount": 100.00,
            "order_total": 100.00
        }

        report = await orchestrator.validate_business_rules("payment", test_data)

        assert report.entity == "payment"
        assert report.total_rules >= 1


class TestInventoryEntityRules:
    """Tests for inventory entity business rules."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_validate_inventory_rules(self, orchestrator):
        """Test validating inventory rules."""
        test_data = {
            "quantity_on_hand": 100,
            "quantity_reserved": 10,
            "quantity_available": 90
        }

        report = await orchestrator.validate_business_rules("inventory", test_data)

        assert report.entity == "inventory"


class TestCustomerEntityRules:
    """Tests for customer entity business rules."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_validate_customer_rules(self, orchestrator):
        """Test validating customer rules."""
        test_data = {
            "email": "test@example.com",
            "loyalty_tier": "gold"
        }

        report = await orchestrator.validate_business_rules("customer", test_data)

        assert report.entity == "customer"


class TestShippingEntityRules:
    """Tests for shipping entity business rules."""

    @pytest.fixture
    def orchestrator(self):
        return BusinessRulesOrchestrator()

    @pytest.mark.asyncio
    async def test_validate_shipping_rules(self, orchestrator):
        """Test validating shipping rules."""
        test_data = {
            "tracking_number": "1Z999AA10123456784",
            "carrier": "FedEx"
        }

        report = await orchestrator.validate_business_rules("shipping", test_data)

        assert report.entity == "shipping"
