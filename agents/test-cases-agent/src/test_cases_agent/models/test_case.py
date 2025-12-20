"""Test case data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TestType(str, Enum):
    """Test type enumeration."""

    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UNIT = "unit"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    EDGE_CASE = "edge_case"
    NEGATIVE = "negative"
    REGRESSION = "regression"
    SMOKE = "smoke"
    ACCEPTANCE = "acceptance"


class Priority(str, Enum):
    """Test priority enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestStep(BaseModel):
    """Individual test step model."""

    step_number: int = Field(..., description="Step sequence number", ge=1)
    action: str = Field(..., description="Action to perform")
    expected_result: str = Field(..., description="Expected outcome")
    test_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Test data for this step"
    )
    validation: Optional[str] = Field(
        default=None, description="Validation criteria"
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")

    @validator("action", "expected_result")
    def validate_not_empty(cls, v):
        """Ensure action and expected result are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class TestCaseMetadata(BaseModel):
    """Metadata for test case."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = Field(default="test-cases-agent")
    version: str = Field(default="1.0.0")
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    related_requirements: List[str] = Field(default_factory=list)
    related_test_cases: List[str] = Field(default_factory=list)
    automation_status: str = Field(default="not_automated")
    execution_time_estimate: Optional[int] = Field(
        default=None, description="Estimated execution time in minutes"
    )


class TestCase(BaseModel):
    """Complete test case model."""

    id: str = Field(..., description="Unique test case identifier")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Detailed description")
    test_type: TestType = Field(..., description="Type of test")
    priority: Priority = Field(..., description="Test priority")

    # Test content
    preconditions: Optional[str] = Field(
        default=None, description="Preconditions for test execution"
    )
    steps: List[TestStep] = Field(..., description="Test execution steps")
    postconditions: Optional[str] = Field(
        default=None, description="Postconditions after test execution"
    )

    # Test data
    test_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Global test data"
    )
    expected_results: Optional[str] = Field(
        default=None, description="Overall expected results"
    )

    # Additional information
    metadata: TestCaseMetadata = Field(
        default_factory=TestCaseMetadata, description="Test case metadata"
    )
    domain_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Domain-specific context"
    )
    coverage: Optional[Dict[str, Any]] = Field(
        default=None, description="Coverage information"
    )

    @validator("title", "description")
    def validate_not_empty(cls, v):
        """Ensure title and description are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @validator("steps")
    def validate_steps(cls, v):
        """Ensure at least one step exists."""
        if not v:
            raise ValueError("Test case must have at least one step")
        # Validate step numbers are sequential
        step_numbers = [step.step_number for step in v]
        if step_numbers != list(range(1, len(step_numbers) + 1)):
            raise ValueError("Step numbers must be sequential starting from 1")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True, indent=2)

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TestCaseRequest(BaseModel):
    """Request model for test case generation."""

    # Required fields
    requirement: str = Field(..., description="Requirement or user story")
    entity_type: str = Field(..., description="Entity type to test")

    # Optional fields
    workflow: Optional[str] = Field(
        default=None, description="Workflow name"
    )
    test_types: Optional[List[TestType]] = Field(
        default=None, description="Specific test types to generate"
    )
    priority_focus: Optional[Priority] = Field(
        default=None, description="Priority focus for tests"
    )
    count: int = Field(
        default=5, description="Number of test cases to generate", ge=1, le=20
    )
    include_edge_cases: bool = Field(
        default=True, description="Include edge cases"
    )
    include_negative_tests: bool = Field(
        default=True, description="Include negative test cases"
    )

    # Context
    domain_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional domain context"
    )
    existing_tests: Optional[List[str]] = Field(
        default=None, description="IDs of existing test cases to avoid duplication"
    )

    # Generation preferences
    detail_level: str = Field(
        default="medium", description="Detail level: low, medium, high"
    )
    language: str = Field(
        default="en", description="Language for test case content"
    )
    format_style: str = Field(
        default="standard", description="Format style: standard, bdd, minimal"
    )

    @validator("requirement", "entity_type")
    def validate_not_empty(cls, v):
        """Ensure required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @validator("detail_level")
    def validate_detail_level(cls, v):
        """Validate detail level."""
        valid_levels = ["low", "medium", "high"]
        if v not in valid_levels:
            raise ValueError(f"Detail level must be one of {valid_levels}")
        return v

    @validator("format_style")
    def validate_format_style(cls, v):
        """Validate format style."""
        valid_styles = ["standard", "bdd", "minimal"]
        if v not in valid_styles:
            raise ValueError(f"Format style must be one of {valid_styles}")
        return v


class TestCaseResponse(BaseModel):
    """Response model for test case generation."""

    success: bool = Field(..., description="Whether generation was successful")
    test_cases: List[TestCase] = Field(
        default_factory=list, description="Generated test cases"
    )
    count: int = Field(..., description="Number of test cases generated")

    # Metadata
    generation_time_ms: int = Field(
        ..., description="Generation time in milliseconds"
    )
    llm_provider: str = Field(..., description="LLM provider used")
    tokens_used: Optional[int] = Field(
        default=None, description="Total tokens used"
    )

    # Coverage information
    coverage_summary: Optional[Dict[str, Any]] = Field(
        default=None, description="Coverage summary"
    )
    test_type_distribution: Optional[Dict[str, int]] = Field(
        default=None, description="Distribution of test types"
    )
    priority_distribution: Optional[Dict[str, int]] = Field(
        default=None, description="Distribution of priorities"
    )

    # Warnings and suggestions
    warnings: List[str] = Field(
        default_factory=list, description="Any warnings during generation"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )

    # Error information (if failed)
    error: Optional[str] = Field(
        default=None, description="Error message if generation failed"
    )
    error_details: Optional[Dict[str, Any]] = Field(
        default=None, description="Detailed error information"
    )

    @validator("test_cases")
    def validate_test_cases_count(cls, v, values):
        """Validate test cases count matches."""
        if "count" in values and len(v) != values["count"]:
            values["count"] = len(v)  # Update count to match actual
        return v

    def add_test_case(self, test_case: TestCase) -> None:
        """Add a test case to the response."""
        self.test_cases.append(test_case)
        self.count = len(self.test_cases)
        self._update_distributions()

    def _update_distributions(self) -> None:
        """Update type and priority distributions."""
        if not self.test_cases:
            return

        # Update test type distribution
        type_dist = {}
        priority_dist = {}

        for tc in self.test_cases:
            # Count test types
            test_type = tc.test_type
            type_dist[test_type] = type_dist.get(test_type, 0) + 1

            # Count priorities
            priority = tc.priority
            priority_dist[priority] = priority_dist.get(priority, 0) + 1

        self.test_type_distribution = type_dist
        self.priority_distribution = priority_dist

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True, indent=2)

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }