"""Shared test fixtures for Requirement Analysis Agent tests."""

import pytest
from datetime import datetime
from typing import Any

from requirement_analysis_agent.models import (
    ACSource,
    AnalysisConfig,
    AnalysisMetadata,
    AnalysisResult,
    ApplicableRule,
    ClarifyingQuestion,
    DimensionScore,
    DomainValidation,
    DomainWarning,
    EntityMapping,
    ExtractedRequirement,
    Gap,
    GapCategory,
    GeneratedAC,
    Grade,
    InputType,
    QuestionCategory,
    QualityScore,
    RequirementStructure,
    Severity,
)


# =============================================================================
# Quality Score Fixtures
# =============================================================================

@pytest.fixture
def sample_dimension_score() -> DimensionScore:
    """Sample dimension score for testing."""
    return DimensionScore(
        score=85,
        grade=Grade.B,
        issues=["Minor issue identified"],
    )


@pytest.fixture
def sample_quality_score() -> QualityScore:
    """Sample quality score with all categories."""
    return QualityScore(
        overall_score=82,
        overall_grade=Grade.B,
        clarity=DimensionScore(score=85, grade=Grade.B, issues=["Ambiguity in step 2"]),
        completeness=DimensionScore(score=78, grade=Grade.C, issues=["Missing error handling"]),
        testability=DimensionScore(score=88, grade=Grade.B, issues=[]),
        consistency=DimensionScore(score=80, grade=Grade.B, issues=["Terminology inconsistency"]),
        recommendation="Address completeness issues before test generation.",
    )


@pytest.fixture
def low_quality_score() -> QualityScore:
    """Low quality score for testing blockers."""
    return QualityScore(
        overall_score=45,
        overall_grade=Grade.F,
        clarity=DimensionScore(score=40, grade=Grade.F, issues=["Very unclear"]),
        completeness=DimensionScore(score=50, grade=Grade.D, issues=["Many gaps"]),
        testability=DimensionScore(score=45, grade=Grade.F, issues=["Untestable"]),
        consistency=DimensionScore(score=45, grade=Grade.F, issues=["Inconsistent"]),
        recommendation="Major revision required.",
    )


# =============================================================================
# Gap Fixtures
# =============================================================================

@pytest.fixture
def sample_gaps() -> list[Gap]:
    """Sample gaps for testing."""
    return [
        Gap(
            id="GAP-001",
            category=GapCategory.MISSING_ERROR_HANDLING,
            severity=Severity.HIGH,
            description="No error handling for payment failure",
            location="acceptance criteria",
            suggestion="Add AC for payment failure scenario",
        ),
        Gap(
            id="GAP-002",
            category=GapCategory.AMBIGUOUS_TERM,
            severity=Severity.MEDIUM,
            description="'Fast checkout' is not defined",
            location="description",
            suggestion="Define specific time threshold (e.g., < 2 seconds)",
        ),
        Gap(
            id="GAP-003",
            category=GapCategory.MISSING_EDGE_CASE,
            severity=Severity.LOW,
            description="Cart empty state not addressed",
            location="description",
            suggestion="Specify behavior when cart is empty",
        ),
    ]


@pytest.fixture
def high_severity_gaps() -> list[Gap]:
    """Multiple high-severity gaps for testing blockers."""
    return [
        Gap(
            id="GAP-001",
            category=GapCategory.MISSING_AC,
            severity=Severity.HIGH,
            description="Critical AC missing",
            location="all",
            suggestion="Add critical AC",
        ),
        Gap(
            id="GAP-002",
            category=GapCategory.MISSING_ERROR_HANDLING,
            severity=Severity.HIGH,
            description="No error handling at all",
            location="all",
            suggestion="Add error handling",
        ),
    ]


# =============================================================================
# Question Fixtures
# =============================================================================

@pytest.fixture
def sample_questions() -> list[ClarifyingQuestion]:
    """Sample clarifying questions for testing."""
    return [
        ClarifyingQuestion(
            id="Q-001",
            priority=Severity.HIGH,
            category=QuestionCategory.ERROR_HANDLING,
            question="What should happen when payment fails?",
            context="No error handling specified for payment failures",
            suggested_answers=[
                "Show error message and allow retry",
                "Redirect to alternative payment",
                "Cancel order and restore cart",
            ],
        ),
        ClarifyingQuestion(
            id="Q-002",
            priority=Severity.MEDIUM,
            category=QuestionCategory.SCOPE,
            question="Does this apply to guest checkout?",
            context="User type not specified in requirements",
            suggested_answers=[
                "Yes, applies to all users",
                "No, registered users only",
                "Both with different flows",
            ],
        ),
    ]


@pytest.fixture
def answered_questions() -> list[ClarifyingQuestion]:
    """Questions with answers provided."""
    return [
        ClarifyingQuestion(
            id="Q-001",
            priority=Severity.HIGH,
            category=QuestionCategory.ERROR_HANDLING,
            question="What should happen when payment fails?",
            context="No error handling specified",
            suggested_answers=["Show error", "Retry", "Cancel"],
            answer="Show error message and allow retry",
        ),
    ]


# =============================================================================
# Generated AC Fixtures
# =============================================================================

@pytest.fixture
def sample_generated_acs() -> list[GeneratedAC]:
    """Sample generated acceptance criteria for testing."""
    return [
        GeneratedAC(
            id="AC-GEN-001",
            source=ACSource.GAP_DETECTION,
            confidence=0.9,
            text="When payment fails, display error message with retry option",
            gherkin="""Given user attempts payment
When payment fails
Then error message is displayed
And retry option is available""",
        ),
        GeneratedAC(
            id="AC-GEN-002",
            source=ACSource.STRUCTURE_EXTRACTION,
            confidence=0.85,
            text="Cart total updates automatically when quantity changes",
            gherkin="""Given items in cart
When quantity is changed
Then total updates automatically""",
        ),
    ]


@pytest.fixture
def accepted_acs() -> list[GeneratedAC]:
    """Accepted generated ACs."""
    return [
        GeneratedAC(
            id="AC-GEN-001",
            source=ACSource.GAP_DETECTION,
            confidence=0.9,
            text="When payment fails, display error message",
            gherkin="Given...",
            accepted=True,
        ),
    ]


# =============================================================================
# Requirement Structure Fixtures
# =============================================================================

@pytest.fixture
def sample_structure() -> RequirementStructure:
    """Sample requirement structure for testing."""
    return RequirementStructure(
        actor="Customer",
        secondary_actors=["Payment Gateway", "Inventory System"],
        action="complete checkout",
        object="shopping cart",
        outcome="order is placed and payment processed",
        preconditions=["User is logged in", "Cart has at least one item"],
        postconditions=["Order confirmation sent", "Inventory updated"],
        triggers=["Click checkout button"],
        constraints=["Minimum order $10", "Maximum 100 items"],
        entities=["Customer", "Cart", "Order", "Product", "Payment"],
    )


# =============================================================================
# Domain Validation Fixtures
# =============================================================================

@pytest.fixture
def sample_domain_validation() -> DomainValidation:
    """Sample domain validation result."""
    return DomainValidation(
        valid=True,
        entities_found=[
            EntityMapping(
                term="cart",
                mapped_entity="ShoppingCart",
                confidence=0.95,
                domain_description="Customer shopping cart for holding products",
            ),
            EntityMapping(
                term="checkout",
                mapped_entity="CheckoutProcess",
                confidence=0.9,
                domain_description="Process for completing a purchase",
            ),
        ],
        rules_applicable=[
            ApplicableRule(
                rule_id="CART-001",
                rule="Cart must have at least one item for checkout",
                relevance=Severity.HIGH,
            ),
            ApplicableRule(
                rule_id="PAY-002",
                rule="Payment must be validated before order confirmation",
                relevance=Severity.HIGH,
            ),
        ],
        warnings=[],
    )


# =============================================================================
# Extracted Requirement Fixtures
# =============================================================================

@pytest.fixture
def sample_extracted_requirement(sample_structure: RequirementStructure) -> ExtractedRequirement:
    """Sample extracted requirement for testing."""
    return ExtractedRequirement(
        title="E-commerce Checkout Feature",
        description="As a customer, I want to complete checkout so that I can purchase items in my cart.",
        structure=sample_structure,
        original_acs=[
            "User can view cart summary",
            "User can enter shipping address",
            "User can pay with credit card",
        ],
        input_type=InputType.JIRA,
    )


# =============================================================================
# Analysis Metadata Fixtures
# =============================================================================

@pytest.fixture
def sample_metadata() -> AnalysisMetadata:
    """Sample analysis metadata."""
    return AnalysisMetadata(
        llm_provider="anthropic",
        llm_model="claude-sonnet-4-20250514",
        tokens_used=3500,
        analysis_time_ms=2100,
        input_type=InputType.JIRA,
        agent_version="1.0.0",
    )


# =============================================================================
# Analysis Result Fixtures
# =============================================================================

@pytest.fixture
def sample_analysis_result(
    sample_quality_score: QualityScore,
    sample_gaps: list[Gap],
    sample_questions: list[ClarifyingQuestion],
    sample_generated_acs: list[GeneratedAC],
    sample_extracted_requirement: ExtractedRequirement,
    sample_domain_validation: DomainValidation,
    sample_metadata: AnalysisMetadata,
) -> AnalysisResult:
    """Complete analysis result for testing."""
    return AnalysisResult(
        request_id="REQ-TEST-001",
        success=True,
        quality_score=sample_quality_score,
        extracted_requirement=sample_extracted_requirement,
        gaps=sample_gaps,
        questions=sample_questions,
        generated_acs=sample_generated_acs,
        domain_validation=sample_domain_validation,
        ready_for_test_generation=False,
        blockers=["High severity gaps need to be addressed"],
        metadata=sample_metadata,
    )


@pytest.fixture
def ready_analysis_result(
    sample_quality_score: QualityScore,
    sample_extracted_requirement: ExtractedRequirement,
    sample_domain_validation: DomainValidation,
    sample_metadata: AnalysisMetadata,
) -> AnalysisResult:
    """Analysis result ready for test generation."""
    # Create a high-quality score
    high_score = QualityScore(
        overall_score=90,
        overall_grade=Grade.A,
        clarity=DimensionScore(score=92, grade=Grade.A, issues=[]),
        completeness=DimensionScore(score=88, grade=Grade.B, issues=[]),
        testability=DimensionScore(score=90, grade=Grade.A, issues=[]),
        consistency=DimensionScore(score=90, grade=Grade.A, issues=[]),
        recommendation="Ready for test generation.",
    )

    return AnalysisResult(
        request_id="REQ-READY-001",
        success=True,
        quality_score=high_score,
        extracted_requirement=sample_extracted_requirement,
        gaps=[],  # No gaps
        questions=[],  # No unanswered questions
        generated_acs=[],
        domain_validation=sample_domain_validation,
        ready_for_test_generation=True,
        blockers=[],
        metadata=sample_metadata,
    )


@pytest.fixture
def failed_analysis_result() -> AnalysisResult:
    """Failed analysis result for testing."""
    # Provide minimal valid structure for failed result
    minimal_structure = RequirementStructure(
        actor="Unknown",
        action="Unknown",
        object="Unknown",
        outcome="Unknown",
    )
    minimal_requirement = ExtractedRequirement(
        title="Failed Analysis",
        description="Analysis failed",
        structure=minimal_structure,
        original_acs=[],
        input_type=InputType.FREE_FORM,
    )
    minimal_score = QualityScore(
        overall_score=0,
        overall_grade=Grade.F,
        clarity=DimensionScore(score=0, grade=Grade.F, issues=["Analysis failed"]),
        completeness=DimensionScore(score=0, grade=Grade.F, issues=["Analysis failed"]),
        testability=DimensionScore(score=0, grade=Grade.F, issues=["Analysis failed"]),
        consistency=DimensionScore(score=0, grade=Grade.F, issues=["Analysis failed"]),
        recommendation="Unable to complete analysis.",
    )
    minimal_metadata = AnalysisMetadata(
        llm_provider="none",
        llm_model="none",
        tokens_used=0,
        analysis_time_ms=0,
        input_type=InputType.FREE_FORM,
        agent_version="1.0.0",
    )
    return AnalysisResult(
        request_id="REQ-FAIL-001",
        success=False,
        quality_score=minimal_score,
        extracted_requirement=minimal_requirement,
        gaps=[],
        questions=[],
        generated_acs=[],
        domain_validation=None,
        ready_for_test_generation=False,
        blockers=["Analysis failed due to invalid input"],
        metadata=minimal_metadata,
        error="Invalid input: requirement text is too short",
    )


# =============================================================================
# Analysis Config Fixtures
# =============================================================================

@pytest.fixture
def default_config() -> AnalysisConfig:
    """Default analysis configuration."""
    return AnalysisConfig()


@pytest.fixture
def minimal_config() -> AnalysisConfig:
    """Minimal analysis configuration."""
    return AnalysisConfig(
        include_domain_validation=False,
        generate_questions=False,
        generate_acceptance_criteria=False,
    )


@pytest.fixture
def full_config() -> AnalysisConfig:
    """Full analysis configuration with all options."""
    return AnalysisConfig(
        include_domain_validation=True,
        generate_questions=True,
        generate_acceptance_criteria=True,
        domain="ecommerce",
        llm_provider="anthropic",
        llm_model="claude-sonnet-4-20250514",
    )


# =============================================================================
# Input Data Fixtures (Jira, Free Form, Transcript)
# =============================================================================

@pytest.fixture
def sample_jira_input() -> dict[str, Any]:
    """Sample Jira story input."""
    return {
        "key": "ECOM-1234",
        "summary": "Add to Cart Feature",
        "description": """As a customer, I want to add items to my shopping cart
so that I can purchase multiple items in one transaction.

## Acceptance Criteria
- User can add items from product page
- Cart icon shows item count
- Cart total updates automatically

## Technical Notes
- Use existing cart API
- Support guest and logged-in users""",
        "acceptance_criteria": [
            "User can add items from product page",
            "Cart icon shows item count",
            "Cart total updates automatically",
        ],
        "priority": "High",
        "labels": ["ecommerce", "cart"],
        "story_points": 5,
    }


@pytest.fixture
def sample_freeform_input() -> dict[str, Any]:
    """Sample free-form input."""
    return {
        "title": "User Authentication Feature",
        "text": """Implement user authentication with the following requirements:

1. Users should be able to register with email and password
2. Users should be able to log in with valid credentials
3. System should display appropriate error messages for invalid login attempts
4. Sessions should expire after 24 hours of inactivity
5. Users should be able to reset their password via email

The system should follow OWASP security best practices.""",
        "context": "This is for an e-commerce platform with existing user database.",
    }


@pytest.fixture
def sample_transcript_input() -> dict[str, Any]:
    """Sample meeting transcript input."""
    return {
        "meeting_title": "Sprint Planning - Cart Feature",
        "meeting_date": "2024-01-15",
        "transcript": """John (PM): Let's discuss the cart feature for this sprint.

Sarah (Dev): We need to handle the add-to-cart functionality. What's the expected behavior?

John (PM): Users should be able to add items directly from the product page. The cart icon should update immediately.

Mike (QA): What about error handling? What if the item is out of stock?

John (PM): Good point. We should show an error message if the item is unavailable.

Sarah (Dev): Should we support guest checkout?

John (PM): Yes, guest users can add to cart, but they'll need to create an account at checkout.

Mike (QA): Decision: Support both guest and registered users for cart operations.

John (PM): Agreed. Let's also make sure we handle network errors gracefully.""",
    }
