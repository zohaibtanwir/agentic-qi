"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from requirement_analysis_agent.models import (
    InputType,
    GapCategory,
    Severity,
    Grade,
    QuestionCategory,
    ACSource,
    DimensionScore,
    QualityScore,
    RequirementStructure,
    ExtractedRequirement,
    Gap,
    ClarifyingQuestion,
    GeneratedAC,
    EntityMapping,
    ApplicableRule,
    DomainWarning,
    DomainValidation,
    AnalysisMetadata,
    AnalysisResult,
    JiraStoryInput,
    FreeFormInput,
    TranscriptInput,
    AnalysisConfig,
    AnsweredQuestion,
    ACDecision,
    ReanalyzeInput,
    ForwardTestCasesConfig,
    ForwardInput,
    ExportConfig,
    StructuredRequirement,
)


class TestEnums:
    """Test enum values."""

    def test_input_type_values(self) -> None:
        """Test InputType enum has correct values."""
        assert InputType.JIRA.value == "jira"
        assert InputType.FREE_FORM.value == "free_form"
        assert InputType.TRANSCRIPT.value == "transcript"

    def test_gap_category_values(self) -> None:
        """Test GapCategory enum has all required values."""
        assert GapCategory.MISSING_AC.value == "missing_ac"
        assert GapCategory.AMBIGUOUS_TERM.value == "ambiguous_term"
        assert GapCategory.UNDEFINED_TERM.value == "undefined_term"
        assert GapCategory.MISSING_ERROR_HANDLING.value == "missing_error_handling"
        assert GapCategory.MISSING_EDGE_CASE.value == "missing_edge_case"
        assert GapCategory.MISSING_PRECONDITION.value == "missing_precondition"
        assert GapCategory.MISSING_POSTCONDITION.value == "missing_postcondition"
        assert GapCategory.CONTRADICTION.value == "contradiction"

    def test_severity_values(self) -> None:
        """Test Severity enum values."""
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"

    def test_grade_values(self) -> None:
        """Test Grade enum values."""
        assert Grade.A.value == "A"
        assert Grade.B.value == "B"
        assert Grade.C.value == "C"
        assert Grade.D.value == "D"
        assert Grade.F.value == "F"


class TestDimensionScore:
    """Test DimensionScore model."""

    def test_valid_dimension_score(self) -> None:
        """Test creating a valid dimension score."""
        score = DimensionScore(score=85, grade=Grade.B, issues=[])
        assert score.score == 85
        assert score.grade == Grade.B
        assert score.issues == []

    def test_dimension_score_with_issues(self) -> None:
        """Test dimension score with issues."""
        score = DimensionScore(
            score=60,
            grade=Grade.D,
            issues=["Vague terminology", "Missing context"],
        )
        assert len(score.issues) == 2
        assert "Vague terminology" in score.issues

    def test_dimension_score_bounds(self) -> None:
        """Test score bounds validation."""
        # Valid boundary values
        score_0 = DimensionScore(score=0, grade=Grade.F, issues=[])
        score_100 = DimensionScore(score=100, grade=Grade.A, issues=[])
        assert score_0.score == 0
        assert score_100.score == 100

        # Invalid values should raise error
        with pytest.raises(ValidationError):
            DimensionScore(score=-1, grade=Grade.F, issues=[])
        with pytest.raises(ValidationError):
            DimensionScore(score=101, grade=Grade.A, issues=[])


class TestQualityScore:
    """Test QualityScore model."""

    def test_valid_quality_score(self) -> None:
        """Test creating a valid quality score."""
        clarity = DimensionScore(score=80, grade=Grade.B, issues=[])
        completeness = DimensionScore(score=70, grade=Grade.C, issues=["Missing error handling"])
        testability = DimensionScore(score=85, grade=Grade.B, issues=[])
        consistency = DimensionScore(score=90, grade=Grade.A, issues=[])

        quality = QualityScore(
            overall_score=81,
            overall_grade=Grade.B,
            clarity=clarity,
            completeness=completeness,
            testability=testability,
            consistency=consistency,
            recommendation="Good quality, consider adding error handling scenarios.",
        )

        assert quality.overall_score == 81
        assert quality.overall_grade == Grade.B
        assert quality.completeness.issues[0] == "Missing error handling"


class TestRequirementStructure:
    """Test RequirementStructure model."""

    def test_valid_structure(self) -> None:
        """Test creating a valid requirement structure."""
        structure = RequirementStructure(
            actor="Customer",
            secondary_actors=["Payment Gateway"],
            action="checkout",
            object="shopping cart",
            outcome="complete purchase",
            preconditions=["User is logged in", "Cart has items"],
            postconditions=["Order is created", "Payment is processed"],
            triggers=["Click checkout button"],
            constraints=["Minimum order value $10"],
            entities=["Customer", "Order", "Product", "Payment"],
        )

        assert structure.actor == "Customer"
        assert len(structure.preconditions) == 2
        assert len(structure.entities) == 4

    def test_minimal_structure(self) -> None:
        """Test structure with minimal required fields."""
        structure = RequirementStructure(
            actor="User",
            action="login",
            object="system",
            outcome="access granted",
        )

        assert structure.actor == "User"
        assert structure.secondary_actors == []
        assert structure.preconditions == []


class TestGap:
    """Test Gap model."""

    def test_valid_gap(self) -> None:
        """Test creating a valid gap."""
        gap = Gap(
            id="GAP-001",
            category=GapCategory.MISSING_ERROR_HANDLING,
            severity=Severity.HIGH,
            description="No error handling specified for failed payment",
            location="acceptance criteria",
            suggestion="Add AC: 'When payment fails, user sees error message'",
        )

        assert gap.id == "GAP-001"
        assert gap.category == GapCategory.MISSING_ERROR_HANDLING
        assert gap.severity == Severity.HIGH


class TestClarifyingQuestion:
    """Test ClarifyingQuestion model."""

    def test_valid_question(self) -> None:
        """Test creating a valid question."""
        question = ClarifyingQuestion(
            id="Q-001",
            priority=Severity.HIGH,
            category=QuestionCategory.ERROR_HANDLING,
            question="What should happen when the payment gateway is unavailable?",
            context="The requirement doesn't specify fallback behavior",
            suggested_answers=[
                "Show error and retry option",
                "Queue payment for retry",
                "Use alternative gateway",
            ],
        )

        assert question.id == "Q-001"
        assert len(question.suggested_answers) == 3
        assert question.answer is None

    def test_question_with_answer(self) -> None:
        """Test question with an answer."""
        question = ClarifyingQuestion(
            id="Q-002",
            priority=Severity.MEDIUM,
            category=QuestionCategory.SCOPE,
            question="Should this apply to guest checkout?",
            context="Requirement unclear about user types",
            suggested_answers=["Yes", "No"],
            answer="Yes, apply to all users",
        )

        assert question.answer == "Yes, apply to all users"


class TestGeneratedAC:
    """Test GeneratedAC model."""

    def test_valid_generated_ac(self) -> None:
        """Test creating a valid generated AC."""
        ac = GeneratedAC(
            id="AC-GEN-001",
            source=ACSource.GAP_DETECTION,
            confidence=0.85,
            text="When payment fails, the system should display an error message",
            gherkin="Given a payment failure\nWhen the checkout is attempted\nThen an error message is displayed",
        )

        assert ac.id == "AC-GEN-001"
        assert ac.source == ACSource.GAP_DETECTION
        assert ac.confidence == 0.85
        assert not ac.accepted

    def test_confidence_bounds(self) -> None:
        """Test confidence score bounds."""
        # Valid bounds
        ac_0 = GeneratedAC(
            id="AC-001", source=ACSource.GAP_DETECTION, confidence=0.0, text="test", gherkin=""
        )
        ac_1 = GeneratedAC(
            id="AC-002", source=ACSource.GAP_DETECTION, confidence=1.0, text="test", gherkin=""
        )
        assert ac_0.confidence == 0.0
        assert ac_1.confidence == 1.0

        # Invalid bounds
        with pytest.raises(ValidationError):
            GeneratedAC(
                id="AC-003", source=ACSource.GAP_DETECTION, confidence=-0.1, text="test", gherkin=""
            )
        with pytest.raises(ValidationError):
            GeneratedAC(
                id="AC-004", source=ACSource.GAP_DETECTION, confidence=1.1, text="test", gherkin=""
            )


class TestDomainValidation:
    """Test DomainValidation model."""

    def test_valid_domain_validation(self) -> None:
        """Test creating a valid domain validation result."""
        entity_mapping = EntityMapping(
            term="cart",
            mapped_entity="ShoppingCart",
            confidence=0.95,
            domain_description="Container for products before checkout",
        )
        rule = ApplicableRule(
            rule_id="RULE-001",
            rule="Order must have at least one item",
            relevance=Severity.HIGH,
        )
        warning = DomainWarning(
            type="missing_entity",
            message="'wishlist' is not a recognized entity",
            suggestion="Consider using 'favorites' or defining 'wishlist'",
        )

        validation = DomainValidation(
            valid=True,
            entities_found=[entity_mapping],
            rules_applicable=[rule],
            warnings=[warning],
        )

        assert validation.valid
        assert len(validation.entities_found) == 1
        assert validation.entities_found[0].mapped_entity == "ShoppingCart"


class TestInputModels:
    """Test input models."""

    def test_jira_story_input(self) -> None:
        """Test JiraStoryInput model."""
        jira_input = JiraStoryInput(
            key="ECOM-1234",
            summary="Add wishlist feature",
            description="As a customer, I want to save products to a wishlist",
            acceptance_criteria=["User can add product to wishlist", "User can remove from wishlist"],
            story_points=5,
            labels=["feature", "wishlist"],
            priority="High",
        )

        assert jira_input.key == "ECOM-1234"
        assert len(jira_input.acceptance_criteria) == 2
        assert jira_input.story_points == 5

    def test_jira_story_defaults(self) -> None:
        """Test JiraStoryInput defaults."""
        jira_input = JiraStoryInput(
            key="ECOM-001",
            summary="Test story",
            description="Description",
        )

        assert jira_input.acceptance_criteria == []
        assert jira_input.story_points == 0
        assert jira_input.priority == "Medium"

    def test_free_form_input(self) -> None:
        """Test FreeFormInput model."""
        free_form = FreeFormInput(
            text="Users should be able to search for products by name",
            context="E-commerce search feature",
            title="Product Search",
        )

        assert free_form.text == "Users should be able to search for products by name"
        assert free_form.title == "Product Search"

    def test_transcript_input(self) -> None:
        """Test TranscriptInput model."""
        transcript = TranscriptInput(
            transcript="PM: We need a checkout feature\nDev: What about guest checkout?",
            meeting_title="Sprint Planning",
            meeting_date="2025-01-15",
            participants=["PM", "Dev", "QA"],
        )

        assert "checkout feature" in transcript.transcript
        assert len(transcript.participants) == 3


class TestAnalysisConfig:
    """Test AnalysisConfig model."""

    def test_default_config(self) -> None:
        """Test default analysis config."""
        config = AnalysisConfig()

        assert config.include_domain_validation is True
        assert config.generate_acceptance_criteria is True
        assert config.generate_questions is True
        assert config.llm_provider == "anthropic"
        assert config.domain == "ecommerce"

    def test_custom_config(self) -> None:
        """Test custom analysis config."""
        config = AnalysisConfig(
            include_domain_validation=False,
            generate_acceptance_criteria=True,
            generate_questions=False,
            domain="healthcare",
        )

        assert config.include_domain_validation is False
        assert config.generate_questions is False
        assert config.domain == "healthcare"


class TestAnalysisResult:
    """Test AnalysisResult model."""

    def test_successful_result(self) -> None:
        """Test creating a successful analysis result."""
        clarity = DimensionScore(score=80, grade=Grade.B, issues=[])
        completeness = DimensionScore(score=75, grade=Grade.C, issues=[])
        testability = DimensionScore(score=85, grade=Grade.B, issues=[])
        consistency = DimensionScore(score=90, grade=Grade.A, issues=[])

        quality = QualityScore(
            overall_score=82,
            overall_grade=Grade.B,
            clarity=clarity,
            completeness=completeness,
            testability=testability,
            consistency=consistency,
            recommendation="Ready for test generation",
        )

        structure = RequirementStructure(
            actor="User",
            action="checkout",
            object="cart",
            outcome="order created",
        )

        extracted = ExtractedRequirement(
            title="Checkout Feature",
            description="User can checkout their cart",
            structure=structure,
            original_acs=["User can pay with credit card"],
            input_type=InputType.JIRA,
        )

        metadata = AnalysisMetadata(
            llm_provider="anthropic",
            llm_model="claude-sonnet-4-20250514",
            tokens_used=1500,
            analysis_time_ms=2500.0,
            input_type=InputType.JIRA,
            agent_version="1.0.0",
        )

        result = AnalysisResult(
            request_id="req-12345",
            success=True,
            quality_score=quality,
            extracted_requirement=extracted,
            gaps=[],
            questions=[],
            generated_acs=[],
            ready_for_test_generation=True,
            metadata=metadata,
        )

        assert result.success
        assert result.ready_for_test_generation
        assert result.quality_score.overall_score == 82

    def test_failed_result(self) -> None:
        """Test creating a failed analysis result with error."""
        clarity = DimensionScore(score=0, grade=Grade.F, issues=[])
        completeness = DimensionScore(score=0, grade=Grade.F, issues=[])
        testability = DimensionScore(score=0, grade=Grade.F, issues=[])
        consistency = DimensionScore(score=0, grade=Grade.F, issues=[])

        quality = QualityScore(
            overall_score=0,
            overall_grade=Grade.F,
            clarity=clarity,
            completeness=completeness,
            testability=testability,
            consistency=consistency,
            recommendation="Analysis failed",
        )

        structure = RequirementStructure(actor="", action="", object="", outcome="")
        extracted = ExtractedRequirement(
            title="",
            description="",
            structure=structure,
            input_type=InputType.FREE_FORM,
        )

        metadata = AnalysisMetadata(
            llm_provider="anthropic",
            llm_model="claude-sonnet-4-20250514",
            tokens_used=0,
            analysis_time_ms=100.0,
            input_type=InputType.FREE_FORM,
            agent_version="1.0.0",
        )

        result = AnalysisResult(
            request_id="req-error",
            success=False,
            quality_score=quality,
            extracted_requirement=extracted,
            metadata=metadata,
            error="Failed to parse requirement: empty input",
        )

        assert not result.success
        assert result.error is not None
        assert "empty input" in result.error


class TestStructuredRequirement:
    """Test StructuredRequirement model."""

    def test_valid_structured_requirement(self) -> None:
        """Test creating a valid structured requirement."""
        req = StructuredRequirement(
            id="REQ-001",
            title="Checkout Feature",
            description="User completes purchase",
            acceptance_criteria=[
                "User can enter payment info",
                "User receives confirmation",
            ],
            domain="ecommerce",
            entities=["User", "Order", "Payment"],
            preconditions=["Cart has items"],
            quality_score=85,
            gaps_addressed=True,
            questions_answered=True,
        )

        assert req.id == "REQ-001"
        assert len(req.acceptance_criteria) == 2
        assert req.quality_score == 85
        assert req.gaps_addressed
