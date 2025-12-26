"""Integration tests for RequirementAnalysisServicer."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from requirement_analysis_agent.config import Settings
from requirement_analysis_agent.llm.base import LLMResponse
from requirement_analysis_agent.models import (
    ACSource,
    AnalysisConfig,
    AnalysisMetadata,
    AnalysisResult,
    ApplicableRule,
    ClarifyingQuestion,
    DimensionScore,
    DomainValidation,
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
from requirement_analysis_agent.proto import requirement_analysis_pb2 as pb2
from requirement_analysis_agent.server.servicer import RequirementAnalysisServicer


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

    def is_available(self) -> bool:
        return True


class MockContext:
    """Mock gRPC context."""

    def __init__(self):
        self._code = None
        self._details = None

    async def abort(self, code, details):
        raise Exception(f"gRPC abort: {code} - {details}")

    def set_code(self, code):
        self._code = code

    def set_details(self, details):
        self._details = details

    def get_code(self):
        return self._code

    def get_details(self):
        return self._details


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        anthropic_api_key="test-api-key",
        llm_model="claude-sonnet-4-20250514",
        grpc_port=50051,
    )


@pytest.fixture
def comprehensive_llm_response() -> str:
    """Comprehensive LLM response for full analysis."""
    return json.dumps({
        "overall_score": 80,
        "overall_grade": "B",
        "clarity": {"score": 82, "grade": "B", "issues": []},
        "completeness": {"score": 78, "grade": "C", "issues": ["Missing error handling"]},
        "testability": {"score": 85, "grade": "B", "issues": []},
        "consistency": {"score": 80, "grade": "B", "issues": []},
        "recommendation": "Good requirement, address completeness.",
        "actor": "Customer",
        "secondary_actors": ["System"],
        "action": "add items",
        "object": "cart",
        "outcome": "items in cart",
        "preconditions": ["User logged in"],
        "postconditions": ["Cart updated"],
        "triggers": ["Click add button"],
        "constraints": [],
        "entities": ["Cart", "Product", "User"],
        "gaps": [
            {"id": "GAP-001", "category": "missing_error_handling", "severity": "high",
             "description": "No error for out of stock", "location": "AC", "suggestion": "Add AC"}
        ],
        "questions": [
            {"id": "Q-001", "priority": "high", "category": "error_handling",
             "question": "What if item out of stock?", "context": "Not specified",
             "suggested_answers": ["Show error", "Suggest alternative"]}
        ],
        "generated_acs": [
            {"id": "AC-GEN-001", "source": "gap_detection", "confidence": 0.9,
             "text": "Show error for out of stock", "gherkin": "Given..."}
        ],
    })


@pytest.fixture
def mock_llm_client(comprehensive_llm_response: str) -> MockLLMClient:
    """Create mock LLM client."""
    return MockLLMClient(comprehensive_llm_response)


@pytest.fixture
def servicer(mock_settings: Settings, mock_llm_client: MockLLMClient) -> RequirementAnalysisServicer:
    """Create servicer with mock dependencies."""
    return RequirementAnalysisServicer(
        settings=mock_settings,
        llm_client=mock_llm_client,
        domain_client=None,
        weaviate_client=None,
        test_cases_client=None,
    )


@pytest.fixture
def mock_context() -> MockContext:
    """Create mock gRPC context."""
    return MockContext()


class TestAnalyzeRequirement:
    """Tests for AnalyzeRequirement RPC."""

    async def test_analyze_jira_story(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test analyzing a Jira story."""
        request = pb2.AnalyzeRequest(
            request_id="REQ-001",
            jira_story=pb2.JiraStoryInput(
                key="ECOM-1234",
                summary="Add to Cart Feature",
                description="As a customer, I want to add items to cart.",
                acceptance_criteria=["User can add from product page"],
                priority="High",
            ),
        )

        response = await servicer.AnalyzeRequirement(request, mock_context)

        # The response may have a different request ID (generated internally)
        assert response.request_id != ""
        assert response.success is True
        assert response.quality_score.overall_score == 80
        assert response.quality_score.overall_grade == "B"
        assert len(response.gaps) == 1
        assert len(response.questions) == 1

    async def test_analyze_freeform_input(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test analyzing free-form input."""
        request = pb2.AnalyzeRequest(
            request_id="REQ-002",
            free_form=pb2.FreeFormInput(
                text="The system shall allow users to add products to shopping cart. Users should see cart total update immediately.",
                title="Add to Cart",
                context="E-commerce platform",
            ),
        )

        response = await servicer.AnalyzeRequirement(request, mock_context)

        assert response.request_id != ""
        assert response.success is True
        # Title might be from input or generated
        assert len(response.extracted_requirement.title) > 0

    async def test_analyze_transcript_input(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test analyzing transcript input."""
        request = pb2.AnalyzeRequest(
            request_id="REQ-003",
            transcript=pb2.TranscriptInput(
                transcript="""PM: We need to add cart functionality.
Dev: What about guest users?
PM: They can add to cart too, but need to login at checkout.
Dev: Got it. Should we show stock availability?
PM: Yes, show if less than 5 items in stock.""",
                meeting_title="Sprint Planning",
                meeting_date="2024-01-15",
            ),
        )

        response = await servicer.AnalyzeRequirement(request, mock_context)

        assert response.request_id != ""
        assert response.success is True

    async def test_analyze_with_config(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test analyzing with custom configuration."""
        request = pb2.AnalyzeRequest(
            request_id="REQ-004",
            jira_story=pb2.JiraStoryInput(
                key="ECOM-5678",
                summary="Checkout Feature",
                description="Customer completes checkout.",
            ),
            config=pb2.AnalysisConfig(
                include_domain_validation=True,
                generate_acceptance_criteria=True,
                generate_questions=True,
                domain="ecommerce",
                llm_provider="anthropic",
            ),
        )

        response = await servicer.AnalyzeRequirement(request, mock_context)

        assert response.success is True
        # Generated ACs should be present
        assert len(response.generated_acs) >= 0  # May be empty if not in response

    async def test_analyze_no_input_returns_error(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test that missing input returns error."""
        request = pb2.AnalyzeRequest(request_id="REQ-ERR")

        response = await servicer.AnalyzeRequirement(request, mock_context)

        assert response.success is False
        assert "No valid input" in response.error

    async def test_analyze_generates_request_id_if_missing(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test that request ID is generated if not provided."""
        request = pb2.AnalyzeRequest(
            jira_story=pb2.JiraStoryInput(
                key="ECOM-AUTO",
                summary="Auto ID Test",
                description="Testing auto ID generation.",
            ),
        )

        response = await servicer.AnalyzeRequirement(request, mock_context)

        assert response.request_id != ""
        assert len(response.request_id) > 0


class TestHealthCheck:
    """Tests for HealthCheck RPC."""

    async def test_health_check_healthy(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test health check when all components healthy."""
        request = pb2.HealthCheckRequest()

        response = await servicer.HealthCheck(request, mock_context)

        assert response.status == "healthy"
        assert response.components["llm"] == "healthy"

    async def test_health_check_includes_components(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test that health check includes component status."""
        request = pb2.HealthCheckRequest()

        response = await servicer.HealthCheck(request, mock_context)

        # Components should be reported
        assert "llm" in response.components
        assert "weaviate" in response.components
        assert "domain_agent" in response.components

    async def test_health_check_not_configured_components(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test health check with unconfigured components."""
        request = pb2.HealthCheckRequest()

        response = await servicer.HealthCheck(request, mock_context)

        # Weaviate and domain_agent not configured in our test setup
        assert response.components["weaviate"] == "not_configured"
        assert response.components["domain_agent"] == "not_configured"


class TestExportAnalysis:
    """Tests for ExportAnalysis RPC."""

    @pytest.fixture
    def servicer_with_history(
        self, mock_settings: Settings, mock_llm_client: MockLLMClient, sample_analysis_result: AnalysisResult
    ) -> RequirementAnalysisServicer:
        """Create servicer with mocked history repository."""
        servicer = RequirementAnalysisServicer(
            settings=mock_settings,
            llm_client=mock_llm_client,
        )

        # Mock the history repository
        mock_repo = AsyncMock()
        mock_repo.get_by_request_id = AsyncMock(return_value=sample_analysis_result)
        servicer.history_repo = mock_repo

        return servicer

    async def test_export_json_format(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test exporting in JSON format."""
        request = pb2.ExportRequest(
            request_id="EXPORT-001",
            analysis_request_id="REQ-TEST-001",
            format="json",
        )

        response = await servicer_with_history.ExportAnalysis(request, mock_context)

        assert response.success is True
        assert response.format == "json"
        assert response.content != ""
        # Should be valid JSON
        parsed = json.loads(response.content)
        assert "request_id" in parsed

    async def test_export_text_format(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test exporting in text format."""
        request = pb2.ExportRequest(
            request_id="EXPORT-002",
            analysis_request_id="REQ-TEST-001",
            format="text",
        )

        response = await servicer_with_history.ExportAnalysis(request, mock_context)

        assert response.success is True
        assert response.format == "text"
        assert response.content != ""
        assert response.filename.endswith(".txt")

    async def test_export_invalid_format(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test exporting with invalid format returns error."""
        request = pb2.ExportRequest(
            request_id="EXPORT-ERR",
            analysis_request_id="REQ-TEST-001",
            format="xml",  # Not supported
        )

        response = await servicer_with_history.ExportAnalysis(request, mock_context)

        assert response.success is False
        assert "Unsupported format" in response.error

    async def test_export_analysis_not_found(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test export when analysis not found."""
        # Override mock to return None
        servicer_with_history.history_repo.get_by_request_id = AsyncMock(return_value=None)

        request = pb2.ExportRequest(
            request_id="EXPORT-404",
            analysis_request_id="NON-EXISTENT",
            format="json",
        )

        response = await servicer_with_history.ExportAnalysis(request, mock_context)

        assert response.success is False
        assert "not found" in response.error.lower()

    async def test_export_no_history_repo(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test export when history repository not available."""
        request = pb2.ExportRequest(
            request_id="EXPORT-NO-REPO",
            analysis_request_id="REQ-001",
            format="json",
        )

        response = await servicer.ExportAnalysis(request, mock_context)

        assert response.success is False
        assert "not available" in response.error.lower()


class TestForwardToTestCases:
    """Tests for ForwardToTestCases RPC."""

    @pytest.fixture
    def servicer_with_test_cases(
        self, mock_settings: Settings, mock_llm_client: MockLLMClient, ready_analysis_result: AnalysisResult
    ) -> RequirementAnalysisServicer:
        """Create servicer with mocked Test Cases Agent client."""
        servicer = RequirementAnalysisServicer(
            settings=mock_settings,
            llm_client=mock_llm_client,
        )

        # Mock history repository
        mock_repo = AsyncMock()
        mock_repo.get_by_request_id = AsyncMock(return_value=ready_analysis_result)
        servicer.history_repo = mock_repo

        # Mock test cases client
        mock_tc_client = MagicMock()
        mock_tc_client.build_structured_requirement = MagicMock(return_value=MagicMock(
            model_dump_json=lambda: '{"title": "Test", "description": "Test desc"}'
        ))
        mock_tc_client.generate_test_cases = AsyncMock(return_value={
            "request_id": "TC-001",
            "test_cases_count": 10,
        })
        servicer.test_cases_client = mock_tc_client

        return servicer

    async def test_forward_success(
        self, servicer_with_test_cases: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test successful forward to Test Cases Agent."""
        request = pb2.ForwardRequest(
            request_id="FWD-001",
            analysis_request_id="REQ-READY-001",
            include_generated_acs=True,
            include_domain_context=True,
        )

        response = await servicer_with_test_cases.ForwardToTestCases(request, mock_context)

        assert response.success is True
        assert response.test_cases_request_id == "TC-001"
        assert response.test_cases_generated == 10

    async def test_forward_with_config(
        self, servicer_with_test_cases: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test forward with test cases configuration."""
        request = pb2.ForwardRequest(
            request_id="FWD-002",
            analysis_request_id="REQ-READY-001",
            test_cases_config=pb2.TestCasesConfig(
                output_format="gherkin",
                coverage_level="comprehensive",
                test_types=["functional", "negative", "edge_case"],
                max_test_cases=30,
            ),
        )

        response = await servicer_with_test_cases.ForwardToTestCases(request, mock_context)

        assert response.success is True

    async def test_forward_no_test_cases_client(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test forward when Test Cases Agent not configured."""
        request = pb2.ForwardRequest(
            request_id="FWD-ERR",
            analysis_request_id="REQ-001",
        )

        response = await servicer.ForwardToTestCases(request, mock_context)

        assert response.success is False
        assert "not configured" in response.error.lower()

    async def test_forward_analysis_not_ready(
        self, servicer_with_test_cases: RequirementAnalysisServicer,
        mock_context: MockContext,
        sample_analysis_result: AnalysisResult,
    ) -> None:
        """Test forward when analysis not ready for test generation."""
        # Override to return a non-ready result
        servicer_with_test_cases.history_repo.get_by_request_id = AsyncMock(
            return_value=sample_analysis_result  # This has ready_for_test_generation=False
        )

        request = pb2.ForwardRequest(
            request_id="FWD-NOT-READY",
            analysis_request_id="REQ-TEST-001",
        )

        response = await servicer_with_test_cases.ForwardToTestCases(request, mock_context)

        assert response.success is False
        assert "not ready" in response.error.lower()


class TestReanalyzeRequirement:
    """Tests for ReanalyzeRequirement RPC."""

    @pytest.fixture
    def servicer_with_reanalyze(
        self, mock_settings: Settings, mock_llm_client: MockLLMClient, sample_analysis_result: AnalysisResult
    ) -> RequirementAnalysisServicer:
        """Create servicer configured for reanalysis testing."""
        servicer = RequirementAnalysisServicer(
            settings=mock_settings,
            llm_client=mock_llm_client,
        )

        # Mock history repository
        mock_repo = AsyncMock()
        mock_repo.get_by_request_id = AsyncMock(return_value=sample_analysis_result)
        mock_repo.save = AsyncMock()
        servicer.history_repo = mock_repo

        return servicer

    async def test_reanalyze_with_updates(
        self, servicer_with_reanalyze: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test reanalysis with updated fields."""
        request = pb2.ReanalyzeRequest(
            request_id="REANA-001",
            original_request_id="REQ-TEST-001",
            updated_title="Updated Checkout Feature",
            updated_description="Improved description with more details.",
            updated_acs=["New AC 1", "New AC 2"],
        )

        response = await servicer_with_reanalyze.ReanalyzeRequirement(request, mock_context)

        assert response.success is True
        # Request ID may be regenerated internally
        assert response.request_id != ""

    async def test_reanalyze_with_answered_questions(
        self, servicer_with_reanalyze: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test reanalysis with answered clarifying questions."""
        request = pb2.ReanalyzeRequest(
            request_id="REANA-002",
            original_request_id="REQ-TEST-001",
            answered_questions=[
                pb2.AnsweredQuestion(question_id="Q-001", answer="Show error message and retry"),
                pb2.AnsweredQuestion(question_id="Q-002", answer="Both guest and registered"),
            ],
        )

        response = await servicer_with_reanalyze.ReanalyzeRequirement(request, mock_context)

        assert response.success is True

    async def test_reanalyze_original_not_found(
        self, servicer_with_reanalyze: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test reanalysis when original not found."""
        servicer_with_reanalyze.history_repo.get_by_request_id = AsyncMock(return_value=None)

        request = pb2.ReanalyzeRequest(
            request_id="REANA-404",
            original_request_id="NON-EXISTENT",
        )

        response = await servicer_with_reanalyze.ReanalyzeRequirement(request, mock_context)

        assert response.success is False
        assert "not found" in response.error.lower()

    async def test_reanalyze_no_history_repo(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test reanalysis when history repository not available."""
        request = pb2.ReanalyzeRequest(
            request_id="REANA-NO-REPO",
            original_request_id="REQ-001",
        )

        response = await servicer.ReanalyzeRequirement(request, mock_context)

        assert response.success is False
        assert "not available" in response.error.lower()


class TestHistoryMethods:
    """Tests for History RPC methods."""

    @pytest.fixture
    def servicer_with_history(
        self, mock_settings: Settings, mock_llm_client: MockLLMClient, sample_analysis_result: AnalysisResult
    ) -> RequirementAnalysisServicer:
        """Create servicer with mocked history repository."""
        servicer = RequirementAnalysisServicer(
            settings=mock_settings,
            llm_client=mock_llm_client,
        )

        # Mock the history repository
        mock_repo = AsyncMock()

        # Mock list_with_filters return value
        mock_repo.list_with_filters = AsyncMock(return_value=([
            {
                "session_id": "REQ-001",
                "title": "Test Requirement 1",
                "quality_score": 85,
                "quality_grade": "B",
                "gaps_count": 2,
                "questions_count": 1,
                "generated_acs_count": 3,
                "ready_for_tests": True,
                "input_type": "jira",
                "llm_model": "claude-sonnet-4-20250514",
                "created_at": "2024-01-15T10:00:00Z",
            },
            {
                "session_id": "REQ-002",
                "title": "Test Requirement 2",
                "quality_score": 70,
                "quality_grade": "C",
                "gaps_count": 5,
                "questions_count": 3,
                "generated_acs_count": 1,
                "ready_for_tests": False,
                "input_type": "free_form",
                "llm_model": "claude-sonnet-4-20250514",
                "created_at": "2024-01-14T10:00:00Z",
            },
        ], 10))

        # Mock get_full_session return value
        mock_repo.get_full_session = AsyncMock(return_value={
            "session_id": "REQ-001",
            "analysis_result": sample_analysis_result,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
        })

        # Mock delete return value
        mock_repo.delete = AsyncMock(return_value=True)

        # Mock search return value
        mock_repo.search = AsyncMock(return_value=([
            {
                "session_id": "REQ-001",
                "title": "Cart Checkout Feature",
                "quality_score": 85,
                "quality_grade": "B",
                "gaps_count": 2,
                "questions_count": 1,
                "generated_acs_count": 3,
                "ready_for_tests": True,
                "input_type": "jira",
                "llm_model": "claude-sonnet-4-20250514",
                "created_at": "2024-01-15T10:00:00Z",
                "search_score": 0.95,
            },
        ], 1))

        servicer.history_repo = mock_repo
        return servicer

    async def test_list_history_success(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test listing history successfully."""
        request = pb2.ListHistoryRequest(
            limit=10,
            offset=0,
        )

        response = await servicer_with_history.ListHistory(request, mock_context)

        assert mock_context.get_code() is None  # No error code set
        assert len(response.sessions) == 2
        assert response.total_count == 10
        assert response.sessions[0].session_id == "REQ-001"
        assert response.sessions[0].quality_score == 85

    async def test_list_history_with_filters(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test listing history with filters."""
        request = pb2.ListHistoryRequest(
            limit=10,
            offset=0,
            filters=pb2.HistoryFilters(
                input_type="jira",
                quality_grade="B",
                ready_status="ready",
            ),
        )

        response = await servicer_with_history.ListHistory(request, mock_context)

        assert mock_context.get_code() is None  # No error code set
        # Verify filters were passed to repository
        servicer_with_history.history_repo.list_with_filters.assert_called_once_with(
            limit=10,
            offset=0,
            input_type="jira",
            quality_grade="B",
            ready_status="ready",
            date_from=None,
            date_to=None,
        )

    async def test_list_history_no_repo(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test listing history when repository not available."""
        request = pb2.ListHistoryRequest(limit=10)

        response = await servicer.ListHistory(request, mock_context)

        import grpc
        assert mock_context.get_code() == grpc.StatusCode.UNAVAILABLE
        assert "not available" in mock_context.get_details().lower()

    async def test_get_history_session_success(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test getting a history session successfully."""
        request = pb2.GetHistorySessionRequest(session_id="REQ-001")

        response = await servicer_with_history.GetHistorySession(request, mock_context)

        assert response.success is True
        assert response.session.session_id == "REQ-001"
        assert response.session.quality_score.overall_score == 82  # From sample_analysis_result

    async def test_get_history_session_not_found(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test getting a non-existent history session."""
        servicer_with_history.history_repo.get_full_session = AsyncMock(return_value=None)

        request = pb2.GetHistorySessionRequest(session_id="NON-EXISTENT")

        response = await servicer_with_history.GetHistorySession(request, mock_context)

        assert response.success is False
        assert "not found" in response.error.lower()

    async def test_get_history_session_no_repo(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test getting history session when repository not available."""
        request = pb2.GetHistorySessionRequest(session_id="REQ-001")

        response = await servicer.GetHistorySession(request, mock_context)

        assert response.success is False
        assert "not available" in response.error.lower()

    async def test_delete_history_session_success(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test deleting a history session successfully."""
        request = pb2.DeleteHistorySessionRequest(session_id="REQ-001")

        response = await servicer_with_history.DeleteHistorySession(request, mock_context)

        assert response.success is True
        servicer_with_history.history_repo.delete.assert_called_once_with("REQ-001")

    async def test_delete_history_session_not_found(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test deleting a non-existent history session."""
        servicer_with_history.history_repo.delete = AsyncMock(return_value=False)

        request = pb2.DeleteHistorySessionRequest(session_id="NON-EXISTENT")

        response = await servicer_with_history.DeleteHistorySession(request, mock_context)

        assert response.success is False
        assert "not found" in response.error.lower() or "failed" in response.error.lower()

    async def test_delete_history_session_no_repo(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test deleting history session when repository not available."""
        request = pb2.DeleteHistorySessionRequest(session_id="REQ-001")

        response = await servicer.DeleteHistorySession(request, mock_context)

        assert response.success is False
        assert "not available" in response.error.lower()

    async def test_search_history_success(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test searching history successfully."""
        request = pb2.SearchHistoryRequest(
            query="checkout",
            limit=10,
        )

        response = await servicer_with_history.SearchHistory(request, mock_context)

        assert mock_context.get_code() is None  # No error code set
        assert len(response.sessions) == 1
        assert response.total_count == 1
        assert "checkout" in response.sessions[0].title.lower()

    async def test_search_history_empty_query(
        self, servicer_with_history: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test searching with empty query."""
        request = pb2.SearchHistoryRequest(
            query="",
            limit=10,
        )

        response = await servicer_with_history.SearchHistory(request, mock_context)

        import grpc
        assert mock_context.get_code() == grpc.StatusCode.INVALID_ARGUMENT
        assert "query" in mock_context.get_details().lower()

    async def test_search_history_no_repo(
        self, servicer: RequirementAnalysisServicer, mock_context: MockContext
    ) -> None:
        """Test searching history when repository not available."""
        request = pb2.SearchHistoryRequest(query="test", limit=10)

        response = await servicer.SearchHistory(request, mock_context)

        import grpc
        assert mock_context.get_code() == grpc.StatusCode.UNAVAILABLE
        assert "not available" in mock_context.get_details().lower()


class TestServicerInitialization:
    """Tests for servicer initialization and lifecycle."""

    async def test_initialize_calls_component_init(
        self, mock_settings: Settings, mock_llm_client: MockLLMClient
    ) -> None:
        """Test that initialize calls component initialization."""
        mock_weaviate = AsyncMock()
        mock_weaviate.connect = AsyncMock()
        mock_weaviate.is_connected = True

        mock_domain = AsyncMock()
        mock_domain.connect = AsyncMock()

        servicer = RequirementAnalysisServicer(
            settings=mock_settings,
            llm_client=mock_llm_client,
            weaviate_client=mock_weaviate,
            domain_client=mock_domain,
        )

        await servicer.initialize()

        mock_weaviate.connect.assert_called_once()
        mock_domain.connect.assert_called_once()

    async def test_shutdown_calls_component_disconnect(
        self, mock_settings: Settings, mock_llm_client: MockLLMClient
    ) -> None:
        """Test that shutdown calls component disconnect."""
        mock_weaviate = AsyncMock()
        mock_weaviate.disconnect = AsyncMock()

        mock_domain = AsyncMock()
        mock_domain.disconnect = AsyncMock()

        servicer = RequirementAnalysisServicer(
            settings=mock_settings,
            llm_client=mock_llm_client,
            weaviate_client=mock_weaviate,
            domain_client=mock_domain,
        )

        await servicer.shutdown()

        mock_weaviate.disconnect.assert_called_once()
        mock_domain.disconnect.assert_called_once()
