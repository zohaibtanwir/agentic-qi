"""Pydantic models for requirement input types."""

from typing import Optional
from pydantic import BaseModel, Field


class JiraStoryInput(BaseModel):
    """Input from a Jira story."""

    key: str = Field(description="Jira ticket key (e.g., ECOM-1234)")
    summary: str = Field(description="Story title")
    description: str = Field(description="Full description")
    acceptance_criteria: list[str] = Field(
        default_factory=list, description="Existing acceptance criteria"
    )
    story_points: int = Field(default=0, description="Complexity estimate")
    labels: list[str] = Field(default_factory=list, description="Jira labels")
    components: list[str] = Field(default_factory=list, description="Jira components")
    priority: str = Field(default="Medium", description="Priority level")
    reporter: str = Field(default="", description="Reporter email")
    assignee: str = Field(default="", description="Assignee email")
    raw_json: Optional[str] = Field(default=None, description="Full Jira JSON if available")


class FreeFormInput(BaseModel):
    """Free-form text requirement input."""

    text: str = Field(description="Raw requirement text")
    context: str = Field(default="", description="Optional context")
    title: str = Field(default="", description="Optional title")


class TranscriptInput(BaseModel):
    """Meeting transcript input."""

    transcript: str = Field(description="Plain text with speaker labels")
    meeting_title: str = Field(default="", description="Meeting name")
    meeting_date: str = Field(default="", description="Date of meeting")
    participants: list[str] = Field(default_factory=list, description="List of participants")


class AnalysisConfig(BaseModel):
    """Configuration for requirement analysis."""

    include_domain_validation: bool = Field(
        default=True, description="Validate against Domain Agent"
    )
    generate_acceptance_criteria: bool = Field(
        default=True, description="Auto-generate missing ACs"
    )
    generate_questions: bool = Field(
        default=True, description="Generate clarifying questions"
    )
    llm_provider: str = Field(default="anthropic", description="LLM provider")
    domain: str = Field(default="ecommerce", description="Domain context")


class AnsweredQuestion(BaseModel):
    """An answered clarifying question."""

    question_id: str = Field(description="Question identifier")
    answer: str = Field(description="The answer provided")


class ACDecision(BaseModel):
    """User decision on a generated acceptance criterion."""

    ac_id: str = Field(description="AC identifier")
    accepted: bool = Field(description="Whether user accepted the AC")
    modified_text: str = Field(default="", description="Modified text if user edited it")


class ReanalyzeInput(BaseModel):
    """Input for reanalysis with updates."""

    original_request_id: str = Field(description="Link to original analysis")
    updated_title: str = Field(default="", description="Updated title")
    updated_description: str = Field(default="", description="Updated description")
    updated_acs: list[str] = Field(default_factory=list, description="Updated acceptance criteria")
    answered_questions: list[AnsweredQuestion] = Field(
        default_factory=list, description="Answered questions"
    )
    ac_decisions: list[ACDecision] = Field(
        default_factory=list, description="AC acceptance decisions"
    )
    additional_context: str = Field(default="", description="Additional context")
    config: Optional[AnalysisConfig] = Field(default=None, description="Analysis config override")


class ForwardTestCasesConfig(BaseModel):
    """Configuration for forwarding to Test Cases Agent."""

    output_format: str = Field(default="gherkin", description="Output format")
    coverage_level: str = Field(default="standard", description="Coverage level")
    test_types: list[str] = Field(
        default_factory=lambda: ["functional", "negative"],
        description="Types of test cases to generate",
    )
    llm_provider: str = Field(default="anthropic", description="LLM provider")
    check_duplicates: bool = Field(default=True, description="Check for duplicate tests")
    max_test_cases: int = Field(default=20, description="Maximum test cases to generate")


class ForwardInput(BaseModel):
    """Input for forwarding to Test Cases Agent."""

    analysis_request_id: str = Field(description="ID of the analysis to forward")
    include_generated_acs: bool = Field(
        default=True, description="Include agent-generated ACs"
    )
    include_domain_context: bool = Field(
        default=True, description="Include domain validation results"
    )
    test_cases_config: ForwardTestCasesConfig = Field(
        default_factory=ForwardTestCasesConfig, description="Test Cases Agent config"
    )


class ExportConfig(BaseModel):
    """Configuration for exporting analysis."""

    format: str = Field(default="json", description="Export format (json, text)")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    include_generated_acs: bool = Field(default=True, description="Include generated ACs")


class StructuredRequirement(BaseModel):
    """Structured requirement for forwarding to Test Cases Agent."""

    id: str = Field(description="Requirement ID")
    title: str = Field(description="Requirement title")
    description: str = Field(description="Full description")
    acceptance_criteria: list[str] = Field(description="All acceptance criteria")
    domain: str = Field(description="Domain context")
    entities: list[str] = Field(default_factory=list, description="Domain entities")
    preconditions: list[str] = Field(default_factory=list, description="Preconditions")
    additional_context: str = Field(default="", description="Additional context")
    quality_score: int = Field(ge=0, le=100, description="Quality score")
    gaps_addressed: bool = Field(default=False, description="Whether gaps were addressed")
    questions_answered: bool = Field(default=False, description="Whether questions were answered")
