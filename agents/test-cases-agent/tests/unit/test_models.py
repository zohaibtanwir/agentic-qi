"""Unit tests for data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from test_cases_agent.models import (
    Priority,
    TestCase,
    TestCaseMetadata,
    TestCaseRequest,
    TestCaseResponse,
    TestStep,
    TestType,
)


class TestTestStep:
    """Test TestStep model."""

    def test_valid_step(self):
        """Test creating a valid test step."""
        step = TestStep(
            step_number=1,
            action="Click login button",
            expected_result="Login page displays",
            test_data={"username": "test"},
            validation="Page title contains 'Login'",
        )
        assert step.step_number == 1
        assert step.action == "Click login button"
        assert step.expected_result == "Login page displays"
        assert step.test_data["username"] == "test"

    def test_step_without_optional_fields(self):
        """Test step with only required fields."""
        step = TestStep(
            step_number=1,
            action="Click button",
            expected_result="Button clicked",
        )
        assert step.test_data is None
        assert step.validation is None
        assert step.notes is None

    def test_invalid_step_number(self):
        """Test step with invalid step number."""
        with pytest.raises(ValidationError) as exc_info:
            TestStep(
                step_number=0,
                action="Click button",
                expected_result="Button clicked",
            )
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_empty_action(self):
        """Test step with empty action."""
        with pytest.raises(ValidationError) as exc_info:
            TestStep(
                step_number=1,
                action="",
                expected_result="Result",
            )
        assert "Field cannot be empty" in str(exc_info.value)

    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from fields."""
        step = TestStep(
            step_number=1,
            action="  Click button  ",
            expected_result="  Button clicked  ",
        )
        assert step.action == "Click button"
        assert step.expected_result == "Button clicked"


class TestTestCase:
    """Test TestCase model."""

    def test_valid_test_case(self):
        """Test creating a valid test case."""
        steps = [
            TestStep(
                step_number=1,
                action="Open login page",
                expected_result="Login page displays",
            ),
            TestStep(
                step_number=2,
                action="Enter credentials",
                expected_result="Credentials accepted",
            ),
        ]

        test_case = TestCase(
            id="TC001",
            title="Test user login",
            description="Verify user can login successfully",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.HIGH,
            steps=steps,
            preconditions="User account exists",
            test_data={"username": "testuser", "password": "testpass"},
        )

        assert test_case.id == "TC001"
        assert test_case.title == "Test user login"
        assert test_case.test_type == "functional"
        assert test_case.priority == "high"
        assert len(test_case.steps) == 2
        assert test_case.preconditions == "User account exists"

    def test_minimal_test_case(self):
        """Test test case with minimal required fields."""
        step = TestStep(
            step_number=1,
            action="Test action",
            expected_result="Expected result",
        )

        test_case = TestCase(
            id="TC002",
            title="Minimal test",
            description="Minimal test description",
            test_type=TestType.UNIT,
            priority=Priority.LOW,
            steps=[step],
        )

        assert test_case.id == "TC002"
        assert test_case.preconditions is None
        assert test_case.postconditions is None
        assert test_case.test_data is None

    def test_test_case_without_steps(self):
        """Test that test case requires at least one step."""
        with pytest.raises(ValidationError) as exc_info:
            TestCase(
                id="TC003",
                title="No steps test",
                description="Test without steps",
                test_type=TestType.FUNCTIONAL,
                priority=Priority.MEDIUM,
                steps=[],
            )
        assert "must have at least one step" in str(exc_info.value)

    def test_non_sequential_steps(self):
        """Test that step numbers must be sequential."""
        steps = [
            TestStep(
                step_number=1,
                action="Step 1",
                expected_result="Result 1",
            ),
            TestStep(
                step_number=3,  # Skip step 2
                action="Step 3",
                expected_result="Result 3",
            ),
        ]

        with pytest.raises(ValidationError) as exc_info:
            TestCase(
                id="TC004",
                title="Non-sequential steps",
                description="Test with non-sequential steps",
                test_type=TestType.FUNCTIONAL,
                priority=Priority.MEDIUM,
                steps=steps,
            )
        assert "must be sequential" in str(exc_info.value)

    def test_to_dict(self):
        """Test converting test case to dictionary."""
        step = TestStep(
            step_number=1,
            action="Test action",
            expected_result="Expected result",
        )

        test_case = TestCase(
            id="TC005",
            title="Dict test",
            description="Test dictionary conversion",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.MEDIUM,
            steps=[step],
        )

        result = test_case.to_dict()
        assert isinstance(result, dict)
        assert result["id"] == "TC005"
        assert result["title"] == "Dict test"
        assert "steps" in result
        assert len(result["steps"]) == 1

    def test_metadata_defaults(self):
        """Test that metadata has correct defaults."""
        step = TestStep(
            step_number=1,
            action="Test",
            expected_result="Result",
        )

        test_case = TestCase(
            id="TC006",
            title="Metadata test",
            description="Test metadata defaults",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.MEDIUM,
            steps=[step],
        )

        assert test_case.metadata.created_by == "test-cases-agent"
        assert test_case.metadata.version == "1.0.0"
        assert test_case.metadata.automation_status == "not_automated"
        assert isinstance(test_case.metadata.created_at, datetime)


class TestTestCaseRequest:
    """Test TestCaseRequest model."""

    def test_valid_request(self):
        """Test creating a valid request."""
        request = TestCaseRequest(
            requirement="User should be able to login",
            entity_type="user",
            workflow="authentication",
            test_types=[TestType.FUNCTIONAL, TestType.EDGE_CASE],
            count=10,
            include_edge_cases=True,
        )

        assert request.requirement == "User should be able to login"
        assert request.entity_type == "user"
        assert request.workflow == "authentication"
        assert len(request.test_types) == 2
        assert request.count == 10

    def test_minimal_request(self):
        """Test request with minimal fields."""
        request = TestCaseRequest(
            requirement="Login test",
            entity_type="user",
        )

        assert request.count == 5  # Default
        assert request.include_edge_cases is True  # Default
        assert request.include_negative_tests is True  # Default
        assert request.detail_level == "medium"  # Default

    def test_invalid_count(self):
        """Test request with invalid count."""
        with pytest.raises(ValidationError) as exc_info:
            TestCaseRequest(
                requirement="Test",
                entity_type="user",
                count=25,  # Max is 20
            )
        assert "less than or equal to 20" in str(exc_info.value)

    def test_invalid_detail_level(self):
        """Test request with invalid detail level."""
        with pytest.raises(ValidationError) as exc_info:
            TestCaseRequest(
                requirement="Test",
                entity_type="user",
                detail_level="invalid",
            )
        assert "Detail level must be one of" in str(exc_info.value)

    def test_empty_requirement(self):
        """Test request with empty requirement."""
        with pytest.raises(ValidationError) as exc_info:
            TestCaseRequest(
                requirement="",
                entity_type="user",
            )
        assert "Field cannot be empty" in str(exc_info.value)


class TestTestCaseResponse:
    """Test TestCaseResponse model."""

    def test_valid_response(self):
        """Test creating a valid response."""
        step = TestStep(
            step_number=1,
            action="Test",
            expected_result="Result",
        )

        test_case = TestCase(
            id="TC007",
            title="Test",
            description="Test description",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.HIGH,
            steps=[step],
        )

        response = TestCaseResponse(
            success=True,
            test_cases=[test_case],
            count=1,
            generation_time_ms=100,
            llm_provider="anthropic",
            tokens_used=500,
        )

        assert response.success is True
        assert len(response.test_cases) == 1
        assert response.count == 1
        assert response.generation_time_ms == 100
        assert response.llm_provider == "anthropic"

    def test_empty_response(self):
        """Test response with no test cases."""
        response = TestCaseResponse(
            success=False,
            test_cases=[],
            count=0,
            generation_time_ms=50,
            llm_provider="anthropic",
            error="Failed to generate",
        )

        assert response.success is False
        assert len(response.test_cases) == 0
        assert response.error == "Failed to generate"

    def test_add_test_case(self):
        """Test adding test case to response."""
        response = TestCaseResponse(
            success=True,
            test_cases=[],
            count=0,
            generation_time_ms=100,
            llm_provider="anthropic",
        )

        step = TestStep(
            step_number=1,
            action="Test",
            expected_result="Result",
        )

        test_case1 = TestCase(
            id="TC008",
            title="Test 1",
            description="First test",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.HIGH,
            steps=[step],
        )

        test_case2 = TestCase(
            id="TC009",
            title="Test 2",
            description="Second test",
            test_type=TestType.EDGE_CASE,
            priority=Priority.MEDIUM,
            steps=[step],
        )

        response.add_test_case(test_case1)
        response.add_test_case(test_case2)

        assert response.count == 2
        assert len(response.test_cases) == 2
        assert response.test_type_distribution["functional"] == 1
        assert response.test_type_distribution["edge_case"] == 1
        assert response.priority_distribution["high"] == 1
        assert response.priority_distribution["medium"] == 1

    def test_response_with_warnings(self):
        """Test response with warnings and suggestions."""
        response = TestCaseResponse(
            success=True,
            test_cases=[],
            count=0,
            generation_time_ms=100,
            llm_provider="anthropic",
            warnings=["Low test coverage"],
            suggestions=["Add more edge cases"],
        )

        assert len(response.warnings) == 1
        assert "Low test coverage" in response.warnings
        assert len(response.suggestions) == 1
        assert "Add more edge cases" in response.suggestions

    def test_to_json(self):
        """Test converting response to JSON."""
        response = TestCaseResponse(
            success=True,
            test_cases=[],
            count=0,
            generation_time_ms=100,
            llm_provider="anthropic",
        )

        json_str = response.to_json()
        assert isinstance(json_str, str)
        assert '"success": true' in json_str
        assert '"llm_provider": "anthropic"' in json_str


class TestEnums:
    """Test enum values."""

    def test_test_type_values(self):
        """Test TestType enum values."""
        assert TestType.FUNCTIONAL.value == "functional"
        assert TestType.EDGE_CASE.value == "edge_case"
        assert TestType.PERFORMANCE.value == "performance"

    def test_priority_values(self):
        """Test Priority enum values."""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"