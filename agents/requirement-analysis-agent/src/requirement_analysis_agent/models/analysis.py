"""Pydantic models for requirement analysis."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InputType(str, Enum):
    """Type of requirement input."""

    JIRA = "jira"
    FREE_FORM = "free_form"
    TRANSCRIPT = "transcript"


class GapCategory(str, Enum):
    """Gap detection categories."""

    MISSING_AC = "missing_ac"
    AMBIGUOUS_TERM = "ambiguous_term"
    UNDEFINED_TERM = "undefined_term"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    MISSING_EDGE_CASE = "missing_edge_case"
    MISSING_PRECONDITION = "missing_precondition"
    MISSING_POSTCONDITION = "missing_postcondition"
    CONTRADICTION = "contradiction"


class Severity(str, Enum):
    """Severity levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Grade(str, Enum):
    """Quality grade letters."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class QuestionCategory(str, Enum):
    """Question categories."""

    ERROR_HANDLING = "error_handling"
    SCOPE = "scope"
    UX = "ux"
    SECURITY = "security"
    PERFORMANCE = "performance"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    DATA = "data"


class ACSource(str, Enum):
    """Sources for generated acceptance criteria."""

    GAP_DETECTION = "gap_detection"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    STRUCTURE_EXTRACTION = "structure_extraction"


class DimensionScore(BaseModel):
    """Score for a single quality dimension."""

    score: int = Field(ge=0, le=100, description="Dimension score 0-100")
    grade: Grade = Field(description="Letter grade A-F")
    issues: list[str] = Field(default_factory=list, description="Specific issues found")


class QualityScore(BaseModel):
    """Overall quality assessment of a requirement."""

    overall_score: int = Field(ge=0, le=100, description="Overall score 0-100")
    overall_grade: Grade = Field(description="Overall letter grade")
    clarity: DimensionScore = Field(description="Clarity dimension (25%)")
    completeness: DimensionScore = Field(description="Completeness dimension (30%)")
    testability: DimensionScore = Field(description="Testability dimension (25%)")
    consistency: DimensionScore = Field(description="Consistency dimension (20%)")
    recommendation: str = Field(description="Action recommendation based on score")


class RequirementStructure(BaseModel):
    """Extracted structure of a requirement."""

    actor: str = Field(description="Who performs the action")
    secondary_actors: list[str] = Field(default_factory=list, description="Other actors involved")
    action: str = Field(description="What is being done")
    object: str = Field(description="What is acted upon")
    outcome: str = Field(description="Expected result")
    preconditions: list[str] = Field(default_factory=list, description="Required starting state")
    postconditions: list[str] = Field(default_factory=list, description="Expected end state")
    triggers: list[str] = Field(default_factory=list, description="What initiates the action")
    constraints: list[str] = Field(default_factory=list, description="Limitations or rules")
    entities: list[str] = Field(default_factory=list, description="Domain entities mentioned")


class ExtractedRequirement(BaseModel):
    """Structured extraction of requirement content."""

    title: str = Field(description="Requirement title")
    description: str = Field(description="Full description")
    structure: RequirementStructure = Field(description="Parsed requirement structure")
    original_acs: list[str] = Field(default_factory=list, description="Original acceptance criteria")
    input_type: InputType = Field(description="Type of input source")


class Gap(BaseModel):
    """A detected gap in the requirement."""

    id: str = Field(description="Gap identifier (e.g., GAP-001)")
    category: GapCategory = Field(description="Gap category")
    severity: Severity = Field(description="Gap severity")
    description: str = Field(description="What's missing or unclear")
    location: str = Field(description="Where in the requirement")
    suggestion: str = Field(description="How to fix the gap")


class ClarifyingQuestion(BaseModel):
    """A question to clarify ambiguous requirements."""

    id: str = Field(description="Question identifier (e.g., Q-001)")
    priority: Severity = Field(description="Question priority")
    category: QuestionCategory = Field(description="Question category")
    question: str = Field(description="The question to ask")
    context: str = Field(description="Why this question matters")
    suggested_answers: list[str] = Field(default_factory=list, description="Possible answers")
    answer: Optional[str] = Field(default=None, description="Answer if provided")


class GeneratedAC(BaseModel):
    """An AI-generated acceptance criterion."""

    id: str = Field(description="Generated AC identifier (e.g., AC-GEN-001)")
    source: ACSource = Field(description="How the AC was generated")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    text: str = Field(description="Plain text acceptance criterion")
    gherkin: str = Field(description="Gherkin format version")
    accepted: bool = Field(default=False, description="Whether user accepted this AC")


class EntityMapping(BaseModel):
    """Mapping of a term to a domain entity."""

    term: str = Field(description="Term from requirement")
    mapped_entity: str = Field(description="Domain entity name")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    domain_description: str = Field(description="Entity description from domain")


class ApplicableRule(BaseModel):
    """A domain rule applicable to the requirement."""

    rule_id: str = Field(description="Rule identifier")
    rule: str = Field(description="Rule text")
    relevance: Severity = Field(description="How relevant the rule is")


class DomainWarning(BaseModel):
    """A warning from domain validation."""

    type: str = Field(description="Warning type (e.g., missing_entity)")
    message: str = Field(description="Warning message")
    suggestion: str = Field(description="How to address the warning")


class DomainValidation(BaseModel):
    """Result of validating requirement against domain knowledge."""

    valid: bool = Field(description="Whether requirement is valid against domain")
    entities_found: list[EntityMapping] = Field(
        default_factory=list, description="Mapped domain entities"
    )
    rules_applicable: list[ApplicableRule] = Field(
        default_factory=list, description="Applicable domain rules"
    )
    warnings: list[DomainWarning] = Field(
        default_factory=list, description="Domain-related warnings"
    )


class AnalysisMetadata(BaseModel):
    """Metadata about the analysis process."""

    llm_provider: str = Field(description="LLM provider used")
    llm_model: str = Field(description="Specific model used")
    tokens_used: int = Field(ge=0, description="Total tokens consumed")
    analysis_time_ms: float = Field(ge=0, description="Analysis time in milliseconds")
    input_type: InputType = Field(description="Type of input analyzed")
    agent_version: str = Field(description="Agent version")


class AnalysisResult(BaseModel):
    """Complete result of requirement analysis."""

    request_id: str = Field(description="Unique request identifier")
    success: bool = Field(description="Whether analysis succeeded")
    quality_score: QualityScore = Field(description="Quality assessment")
    extracted_requirement: ExtractedRequirement = Field(description="Extracted content")
    gaps: list[Gap] = Field(default_factory=list, description="Detected gaps")
    questions: list[ClarifyingQuestion] = Field(
        default_factory=list, description="Clarifying questions"
    )
    generated_acs: list[GeneratedAC] = Field(
        default_factory=list, description="Generated acceptance criteria"
    )
    domain_validation: Optional[DomainValidation] = Field(
        default=None, description="Domain validation results"
    )
    ready_for_test_generation: bool = Field(
        default=False, description="Whether ready for test case generation"
    )
    blockers: list[str] = Field(default_factory=list, description="Blocking issues")
    metadata: AnalysisMetadata = Field(description="Analysis metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")
