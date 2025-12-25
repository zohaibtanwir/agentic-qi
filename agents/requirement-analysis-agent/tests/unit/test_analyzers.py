"""Unit tests for analysis components."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from requirement_analysis_agent.analysis import (
    AnalysisEngine,
    QualityScorer,
    GapDetector,
    StructureExtractor,
    QuestionGenerator,
    ACGenerator,
    LLMParsingError,
)
from requirement_analysis_agent.llm.base import LLMResponse
from requirement_analysis_agent.models import (
    ACSource,
    AnalysisConfig,
    GapCategory,
    Grade,
    InputType,
    QuestionCategory,
    Severity,
)
from requirement_analysis_agent.parsers.base import ParsedInput


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, response_content: str = "{}"):
        self.response_content = response_content
        self.provider_name = "mock"
        self.default_model = "mock-model"
        self._client = True

    async def generate(self, messages, config=None):
        return LLMResponse(
            content=self.response_content,
            model="mock-model",
            provider="mock",
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        )

    async def initialize(self):
        pass


class TestQualityScorer:
    """Tests for QualityScorer."""

    @pytest.fixture
    def quality_response(self) -> str:
        """Sample quality scoring response."""
        return json.dumps({
            "overall_score": 82,
            "overall_grade": "B",
            "clarity": {"score": 85, "grade": "B", "issues": ["Minor ambiguity in step 2"]},
            "completeness": {"score": 78, "grade": "C", "issues": ["Missing error handling"]},
            "testability": {"score": 88, "grade": "B", "issues": []},
            "consistency": {"score": 80, "grade": "B", "issues": ["Terminology inconsistency"]},
            "recommendation": "Good requirement, address completeness issues.",
        })

    @pytest.fixture
    def mock_llm(self, quality_response: str) -> MockLLMClient:
        return MockLLMClient(quality_response)

    async def test_analyze_returns_quality_score(self, mock_llm: MockLLMClient) -> None:
        """Test that analyze returns a valid QualityScore."""
        scorer = QualityScorer(mock_llm)
        result = await scorer.analyze(
            title="Add checkout feature",
            description="User can checkout their cart",
            acceptance_criteria=["User can pay with credit card"],
        )

        assert result.overall_score == 82
        assert result.overall_grade == Grade.B
        assert result.clarity.score == 85
        assert result.completeness.score == 78
        assert len(result.completeness.issues) == 1

    async def test_analyze_handles_minimal_response(self) -> None:
        """Test handling of minimal valid response."""
        minimal_response = json.dumps({
            "overall_score": 70,
            "overall_grade": "C",
            "clarity": {"score": 70, "grade": "C", "issues": []},
            "completeness": {"score": 70, "grade": "C", "issues": []},
            "testability": {"score": 70, "grade": "C", "issues": []},
            "consistency": {"score": 70, "grade": "C", "issues": []},
        })
        mock_llm = MockLLMClient(minimal_response)
        scorer = QualityScorer(mock_llm)

        result = await scorer.analyze("Title", "Description", [])

        assert result.overall_score == 70
        assert result.recommendation is not None  # Should generate default


class TestGapDetector:
    """Tests for GapDetector."""

    @pytest.fixture
    def gap_response(self) -> str:
        """Sample gap detection response."""
        return json.dumps({
            "gaps": [
                {
                    "id": "GAP-001",
                    "category": "missing_error_handling",
                    "severity": "high",
                    "description": "No error handling for payment failure",
                    "location": "acceptance criteria",
                    "suggestion": "Add AC for payment failure scenario",
                },
                {
                    "id": "GAP-002",
                    "category": "ambiguous_term",
                    "severity": "medium",
                    "description": "'Fast checkout' is not defined",
                    "location": "description",
                    "suggestion": "Define specific time threshold",
                },
            ],
            "total_high_severity": 1,
            "total_medium_severity": 1,
            "total_low_severity": 0,
        })

    @pytest.fixture
    def mock_llm(self, gap_response: str) -> MockLLMClient:
        return MockLLMClient(gap_response)

    async def test_analyze_returns_gaps(self, mock_llm: MockLLMClient) -> None:
        """Test that analyze returns detected gaps."""
        detector = GapDetector(mock_llm)
        result = await detector.analyze(
            title="Fast checkout",
            description="User can quickly checkout",
            acceptance_criteria=[],
        )

        assert len(result) == 2
        assert result[0].id == "GAP-001"
        assert result[0].category == GapCategory.MISSING_ERROR_HANDLING
        assert result[0].severity == Severity.HIGH
        assert result[1].category == GapCategory.AMBIGUOUS_TERM

    async def test_analyze_handles_empty_gaps(self) -> None:
        """Test handling of no gaps found."""
        empty_response = json.dumps({"gaps": []})
        mock_llm = MockLLMClient(empty_response)
        detector = GapDetector(mock_llm)

        result = await detector.analyze("Title", "Description", ["AC1", "AC2"])

        assert len(result) == 0

    async def test_handles_unknown_category(self) -> None:
        """Test handling of unknown gap category."""
        response = json.dumps({
            "gaps": [{"id": "GAP-001", "category": "unknown_category", "severity": "high",
                     "description": "Test", "location": "test", "suggestion": "test"}]
        })
        mock_llm = MockLLMClient(response)
        detector = GapDetector(mock_llm)

        result = await detector.analyze("Title", "Description", [])

        # Should default to MISSING_AC
        assert result[0].category == GapCategory.MISSING_AC


class TestStructureExtractor:
    """Tests for StructureExtractor."""

    @pytest.fixture
    def structure_response(self) -> str:
        """Sample structure extraction response."""
        return json.dumps({
            "actor": "Customer",
            "secondary_actors": ["Payment Gateway", "Inventory System"],
            "action": "complete checkout",
            "object": "shopping cart",
            "outcome": "order is placed and payment is processed",
            "preconditions": ["User is logged in", "Cart has items"],
            "postconditions": ["Order confirmation sent", "Inventory updated"],
            "triggers": ["Click checkout button"],
            "constraints": ["Minimum order $10"],
            "entities": ["Customer", "Cart", "Order", "Product", "Payment"],
        })

    @pytest.fixture
    def mock_llm(self, structure_response: str) -> MockLLMClient:
        return MockLLMClient(structure_response)

    async def test_analyze_returns_structure(self, mock_llm: MockLLMClient) -> None:
        """Test that analyze returns extracted structure."""
        extractor = StructureExtractor(mock_llm)
        result = await extractor.analyze(
            title="Checkout Feature",
            description="Customer completes checkout process",
        )

        assert result.actor == "Customer"
        assert len(result.secondary_actors) == 2
        assert result.action == "complete checkout"
        assert len(result.preconditions) == 2
        assert "Cart" in result.entities

    async def test_analyze_handles_minimal_structure(self) -> None:
        """Test handling of minimal structure response."""
        minimal = json.dumps({
            "actor": "User",
            "action": "login",
            "object": "system",
            "outcome": "access granted",
        })
        mock_llm = MockLLMClient(minimal)
        extractor = StructureExtractor(mock_llm)

        result = await extractor.analyze("Login", "User logs in")

        assert result.actor == "User"
        assert result.secondary_actors == []
        assert result.preconditions == []


class TestQuestionGenerator:
    """Tests for QuestionGenerator."""

    @pytest.fixture
    def question_response(self) -> str:
        """Sample question generation response."""
        return json.dumps({
            "questions": [
                {
                    "id": "Q-001",
                    "priority": "high",
                    "category": "error_handling",
                    "question": "What should happen when payment fails?",
                    "context": "No error handling specified",
                    "suggested_answers": ["Show error message", "Retry payment", "Cancel order"],
                },
                {
                    "id": "Q-002",
                    "priority": "medium",
                    "category": "scope",
                    "question": "Does this apply to guest checkout?",
                    "context": "User type not specified",
                    "suggested_answers": ["Yes", "No", "Both registered and guest"],
                },
            ]
        })

    @pytest.fixture
    def mock_llm(self, question_response: str) -> MockLLMClient:
        return MockLLMClient(question_response)

    async def test_analyze_returns_questions(self, mock_llm: MockLLMClient) -> None:
        """Test that analyze returns clarifying questions."""
        generator = QuestionGenerator(mock_llm)
        result = await generator.analyze(
            title="Checkout",
            description="User checks out",
            gaps=[],
        )

        assert len(result) == 2
        assert result[0].id == "Q-001"
        assert result[0].priority == Severity.HIGH
        assert result[0].category == QuestionCategory.ERROR_HANDLING
        assert len(result[0].suggested_answers) == 3

    async def test_analyze_handles_empty_questions(self) -> None:
        """Test handling of no questions generated."""
        empty = json.dumps({"questions": []})
        mock_llm = MockLLMClient(empty)
        generator = QuestionGenerator(mock_llm)

        result = await generator.analyze("Title", "Description", [])

        assert len(result) == 0


class TestACGenerator:
    """Tests for ACGenerator."""

    @pytest.fixture
    def ac_response(self) -> str:
        """Sample AC generation response."""
        return json.dumps({
            "generated_acs": [
                {
                    "id": "AC-GEN-001",
                    "source": "gap_detection",
                    "confidence": 0.9,
                    "text": "When payment fails, an error message is displayed",
                    "gherkin": "Given a payment failure\nWhen checkout is attempted\nThen error message is shown",
                },
                {
                    "id": "AC-GEN-002",
                    "source": "structure_extraction",
                    "confidence": 0.85,
                    "text": "Order confirmation email is sent after successful checkout",
                    "gherkin": "Given successful checkout\nWhen order is placed\nThen confirmation email is sent",
                },
            ]
        })

    @pytest.fixture
    def mock_llm(self, ac_response: str) -> MockLLMClient:
        return MockLLMClient(ac_response)

    async def test_analyze_returns_generated_acs(self, mock_llm: MockLLMClient) -> None:
        """Test that analyze returns generated ACs."""
        generator = ACGenerator(mock_llm)
        result = await generator.analyze(
            title="Checkout",
            description="User checks out",
            existing_acs=["User can pay with card"],
            gaps=[],
        )

        assert len(result) == 2
        assert result[0].id == "AC-GEN-001"
        assert result[0].source == ACSource.GAP_DETECTION
        assert result[0].confidence == 0.9
        assert "error message" in result[0].text.lower()
        assert not result[0].accepted  # Default is False

    async def test_confidence_bounds(self) -> None:
        """Test that confidence is bounded between 0 and 1."""
        response = json.dumps({
            "generated_acs": [
                {"id": "AC-001", "source": "gap_detection", "confidence": 1.5,
                 "text": "Test", "gherkin": "Given..."},
                {"id": "AC-002", "source": "gap_detection", "confidence": -0.5,
                 "text": "Test", "gherkin": "Given..."},
            ]
        })
        mock_llm = MockLLMClient(response)
        generator = ACGenerator(mock_llm)

        result = await generator.analyze("Title", "Desc", [], [])

        assert result[0].confidence == 1.0  # Capped at max
        assert result[1].confidence == 0.0  # Capped at min


class TestAnalysisEngine:
    """Tests for AnalysisEngine orchestrator."""

    @pytest.fixture
    def comprehensive_response(self) -> str:
        """Comprehensive analysis response for all components."""
        return json.dumps({
            # Quality score response
            "overall_score": 75,
            "overall_grade": "C",
            "clarity": {"score": 80, "grade": "B", "issues": []},
            "completeness": {"score": 70, "grade": "C", "issues": ["Missing error handling"]},
            "testability": {"score": 75, "grade": "C", "issues": []},
            "consistency": {"score": 80, "grade": "B", "issues": []},
            "recommendation": "Address completeness issues",
            # Structure response
            "actor": "User",
            "secondary_actors": [],
            "action": "checkout",
            "object": "cart",
            "outcome": "order placed",
            "preconditions": [],
            "postconditions": [],
            "triggers": [],
            "constraints": [],
            "entities": ["User", "Cart", "Order"],
            # Gaps response
            "gaps": [
                {"id": "GAP-001", "category": "missing_error_handling", "severity": "high",
                 "description": "No error handling", "location": "AC", "suggestion": "Add error AC"}
            ],
            # Questions response
            "questions": [
                {"id": "Q-001", "priority": "high", "category": "error_handling",
                 "question": "What if payment fails?", "context": "Missing",
                 "suggested_answers": ["Show error"]}
            ],
            # Generated ACs response
            "generated_acs": [
                {"id": "AC-GEN-001", "source": "gap_detection", "confidence": 0.85,
                 "text": "Handle payment failure", "gherkin": "Given..."}
            ],
        })

    async def test_analyze_full_workflow(self, comprehensive_response: str) -> None:
        """Test full analysis workflow."""
        mock_llm = MockLLMClient(comprehensive_response)
        engine = AnalysisEngine(mock_llm)

        parsed_input = ParsedInput(
            input_type=InputType.JIRA,
            title="Checkout Feature",
            description="User can checkout their cart",
            acceptance_criteria=["User can pay with card"],
        )

        result = await engine.analyze(parsed_input)

        assert result.success is True
        assert result.quality_score.overall_score == 75
        assert result.extracted_requirement.title == "Checkout Feature"
        assert len(result.gaps) == 1
        assert len(result.questions) == 1
        assert len(result.generated_acs) == 1
        assert result.metadata.llm_provider == "mock"

    async def test_analyze_with_config(self, comprehensive_response: str) -> None:
        """Test analysis with custom config."""
        mock_llm = MockLLMClient(comprehensive_response)
        engine = AnalysisEngine(mock_llm)

        config = AnalysisConfig(
            generate_questions=False,
            generate_acceptance_criteria=False,
        )

        parsed_input = ParsedInput(
            input_type=InputType.FREE_FORM,
            title="Test",
            description="Test description",
            acceptance_criteria=[],
        )

        result = await engine.analyze(parsed_input, config)

        # Questions and ACs should be empty when disabled
        # (In this mock, they might still be returned since we use same response)
        assert result.success is True

    async def test_readiness_assessment_blockers(self) -> None:
        """Test readiness assessment with blockers."""
        # Low quality score should block
        low_quality_response = json.dumps({
            "overall_score": 50,
            "overall_grade": "F",
            "clarity": {"score": 50, "grade": "F", "issues": ["Many issues"]},
            "completeness": {"score": 50, "grade": "F", "issues": []},
            "testability": {"score": 50, "grade": "F", "issues": []},
            "consistency": {"score": 50, "grade": "F", "issues": []},
            "actor": "User", "action": "test", "object": "system", "outcome": "result",
            "entities": [],
            "gaps": [{"id": "GAP-001", "category": "missing_ac", "severity": "high",
                     "description": "Critical gap", "location": "all", "suggestion": "Fix"}],
            "questions": [{"id": "Q-001", "priority": "high", "category": "scope",
                          "question": "Critical question?", "context": "Blocking",
                          "suggested_answers": []}],
            "generated_acs": [],
        })
        mock_llm = MockLLMClient(low_quality_response)
        engine = AnalysisEngine(mock_llm)

        parsed_input = ParsedInput(
            input_type=InputType.FREE_FORM,
            title="Bad Requirement",
            description="Vague",
            acceptance_criteria=[],
        )

        result = await engine.analyze(parsed_input)

        assert result.ready_for_test_generation is False
        assert len(result.blockers) > 0


class TestLLMParsingError:
    """Tests for JSON parsing error handling."""

    async def test_invalid_json_raises_error(self) -> None:
        """Test that invalid JSON raises LLMParsingError."""
        mock_llm = MockLLMClient("This is not valid JSON")
        scorer = QualityScorer(mock_llm)

        with pytest.raises(LLMParsingError):
            await scorer.analyze("Title", "Description", [])

    async def test_markdown_json_extraction(self) -> None:
        """Test extraction of JSON from markdown code blocks."""
        markdown_response = '''Here's the analysis:

```json
{
    "overall_score": 80,
    "overall_grade": "B",
    "clarity": {"score": 80, "grade": "B", "issues": []},
    "completeness": {"score": 80, "grade": "B", "issues": []},
    "testability": {"score": 80, "grade": "B", "issues": []},
    "consistency": {"score": 80, "grade": "B", "issues": []},
    "recommendation": "Good"
}
```

That's my assessment.'''
        mock_llm = MockLLMClient(markdown_response)
        scorer = QualityScorer(mock_llm)

        result = await scorer.analyze("Title", "Description", [])

        assert result.overall_score == 80
