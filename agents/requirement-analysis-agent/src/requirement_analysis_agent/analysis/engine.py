"""Analysis Engine - Orchestrates all analysis components."""

import asyncio
import time
import uuid
from typing import Optional

from requirement_analysis_agent.analysis.ac_generator import ACGenerator
from requirement_analysis_agent.analysis.base import AnalyzerError
from requirement_analysis_agent.analysis.gap_detector import GapDetector
from requirement_analysis_agent.analysis.quality_scorer import QualityScorer
from requirement_analysis_agent.analysis.question_generator import QuestionGenerator
from requirement_analysis_agent.analysis.structure_extractor import StructureExtractor
from requirement_analysis_agent.llm.base import LLMProvider
from requirement_analysis_agent.models import (
    AnalysisConfig,
    AnalysisMetadata,
    AnalysisResult,
    DimensionScore,
    DomainValidation,
    ExtractedRequirement,
    Grade,
    InputType,
    QualityScore,
    RequirementStructure,
)
from requirement_analysis_agent.parsers.base import ParsedInput
from requirement_analysis_agent.utils.logging import get_logger


class AnalysisEngine:
    """
    Main analysis engine that orchestrates all analysis components.

    The engine coordinates:
    - Quality scoring
    - Structure extraction
    - Gap detection
    - Question generation
    - AC generation
    - Domain validation (optional)
    """

    VERSION = "1.0.0"

    def __init__(
        self,
        llm_client: LLMProvider,
        domain_validator: Optional[object] = None,  # Will be typed when domain integration is added
    ):
        """
        Initialize analysis engine.

        Args:
            llm_client: LLM client for analysis
            domain_validator: Optional domain validator for domain-specific validation
        """
        self.llm_client = llm_client
        self.domain_validator = domain_validator
        self.logger = get_logger(__name__)

        # Initialize analyzers
        self.quality_scorer = QualityScorer(llm_client)
        self.structure_extractor = StructureExtractor(llm_client)
        self.gap_detector = GapDetector(llm_client)
        self.question_generator = QuestionGenerator(llm_client)
        self.ac_generator = ACGenerator(llm_client)

    async def analyze(
        self,
        parsed_input: ParsedInput,
        config: Optional[AnalysisConfig] = None,
    ) -> AnalysisResult:
        """
        Perform comprehensive analysis on a parsed requirement.

        Args:
            parsed_input: Parsed requirement input
            config: Analysis configuration

        Returns:
            Complete AnalysisResult
        """
        config = config or AnalysisConfig()
        request_id = str(uuid.uuid4())
        start_time = time.time()
        # Reset token count at the start to track tokens for this request
        self.llm_client.reset_token_count()

        self.logger.info(
            "Starting requirement analysis",
            request_id=request_id,
            title=parsed_input.title,
            input_type=parsed_input.input_type.value,
        )

        try:
            # Step 1: Run quality scoring and structure extraction in parallel
            self.logger.debug("Running quality scoring and structure extraction")
            quality_task = self.quality_scorer.analyze(
                parsed_input.title,
                parsed_input.description,
                parsed_input.acceptance_criteria,
            )
            structure_task = self.structure_extractor.analyze(
                parsed_input.title,
                parsed_input.description,
            )

            quality_score, structure = await asyncio.gather(quality_task, structure_task)

            # Step 2: Detect gaps
            self.logger.debug("Detecting gaps")
            gaps = await self.gap_detector.analyze(
                parsed_input.title,
                parsed_input.description,
                parsed_input.acceptance_criteria,
            )

            # Step 3: Generate questions and ACs in parallel (if configured)
            questions = []
            generated_acs = []

            tasks = []
            if config.generate_questions:
                tasks.append(("questions", self.question_generator.analyze(
                    parsed_input.title,
                    parsed_input.description,
                    gaps,
                )))

            if config.generate_acceptance_criteria:
                tasks.append(("acs", self.ac_generator.analyze(
                    parsed_input.title,
                    parsed_input.description,
                    parsed_input.acceptance_criteria,
                    gaps,
                )))

            if tasks:
                results = await asyncio.gather(*[t[1] for t in tasks])
                for i, (name, _) in enumerate(tasks):
                    if name == "questions":
                        questions = results[i]
                    elif name == "acs":
                        generated_acs = results[i]

            # Step 4: Domain validation (if configured and validator available)
            domain_validation = None
            if config.include_domain_validation and self.domain_validator:
                self.logger.debug("Running domain validation")
                domain_validation = await self._run_domain_validation(
                    structure.entities,
                    config.domain,
                )

            # Calculate analysis time
            analysis_time_ms = (time.time() - start_time) * 1000

            # Determine if ready for test generation
            ready_for_tests, blockers = self._assess_readiness(
                quality_score,
                gaps,
                questions,
            )

            # Build extracted requirement
            extracted_requirement = ExtractedRequirement(
                title=parsed_input.title,
                description=parsed_input.description,
                structure=structure,
                original_acs=parsed_input.acceptance_criteria,
                input_type=parsed_input.input_type,
            )

            # Build metadata - get total tokens from LLM client
            total_tokens = self.llm_client.get_total_tokens()
            metadata = AnalysisMetadata(
                llm_provider=self.llm_client.provider_name,
                llm_model=self.llm_client.default_model,
                tokens_used=total_tokens,
                analysis_time_ms=analysis_time_ms,
                input_type=parsed_input.input_type,
                agent_version=self.VERSION,
            )

            result = AnalysisResult(
                request_id=request_id,
                success=True,
                quality_score=quality_score,
                extracted_requirement=extracted_requirement,
                gaps=gaps,
                questions=questions,
                generated_acs=generated_acs,
                domain_validation=domain_validation,
                ready_for_test_generation=ready_for_tests,
                blockers=blockers,
                metadata=metadata,
            )

            self.logger.info(
                "Analysis complete",
                request_id=request_id,
                quality_score=quality_score.overall_score,
                gaps_count=len(gaps),
                questions_count=len(questions),
                ready_for_tests=ready_for_tests,
                duration_ms=analysis_time_ms,
            )

            return result

        except AnalyzerError as e:
            self.logger.error("Analysis failed", request_id=request_id, error=str(e))
            return self._create_error_result(
                request_id,
                parsed_input.input_type,
                str(e),
                time.time() - start_time,
            )
        except Exception as e:
            self.logger.error("Unexpected analysis error", request_id=request_id, error=str(e))
            return self._create_error_result(
                request_id,
                parsed_input.input_type,
                f"Unexpected error: {e}",
                time.time() - start_time,
            )

    async def reanalyze(
        self,
        original_result: AnalysisResult,
        updated_title: Optional[str] = None,
        updated_description: Optional[str] = None,
        updated_acs: Optional[list[str]] = None,
        answered_questions: Optional[dict[str, str]] = None,
        config: Optional[AnalysisConfig] = None,
    ) -> AnalysisResult:
        """
        Reanalyze a requirement with updates.

        Args:
            original_result: Previous analysis result
            updated_title: Updated title (optional)
            updated_description: Updated description (optional)
            updated_acs: Updated acceptance criteria (optional)
            answered_questions: Map of question_id to answer (optional)
            config: Analysis configuration

        Returns:
            Updated AnalysisResult
        """
        # Create updated parsed input
        parsed_input = ParsedInput(
            input_type=original_result.extracted_requirement.input_type,
            title=updated_title or original_result.extracted_requirement.title,
            description=updated_description or original_result.extracted_requirement.description,
            acceptance_criteria=updated_acs or original_result.extracted_requirement.original_acs,
        )

        # Add context from answered questions
        if answered_questions:
            context_additions = []
            for q in original_result.questions:
                if q.id in answered_questions:
                    context_additions.append(f"Q: {q.question}\nA: {answered_questions[q.id]}")
            if context_additions:
                parsed_input.context = "\n\n".join(context_additions)

        # Run full analysis with updated input
        return await self.analyze(parsed_input, config)

    def _assess_readiness(
        self,
        quality_score: QualityScore,
        gaps: list,
        questions: list,
    ) -> tuple[bool, list[str]]:
        """
        Assess if requirement is ready for test generation.

        Returns:
            Tuple of (ready_for_tests, list_of_blockers)
        """
        blockers = []

        # Check overall quality
        if quality_score.overall_score < 60:
            blockers.append(f"Quality score too low ({quality_score.overall_score}/100)")

        # Check for high-severity gaps
        high_gaps = [g for g in gaps if g.severity.value == "high"]
        if high_gaps:
            blockers.append(f"{len(high_gaps)} high-severity gap(s) need resolution")

        # Check for high-priority unanswered questions
        high_questions = [q for q in questions if q.priority.value == "high" and not q.answer]
        if high_questions:
            blockers.append(f"{len(high_questions)} high-priority question(s) need answers")

        return len(blockers) == 0, blockers

    async def _run_domain_validation(
        self,
        entities: list[str],
        domain: str,
    ) -> Optional[DomainValidation]:
        """Run domain validation if validator is available."""
        if not self.domain_validator:
            return None

        try:
            # This will be implemented when domain integration is added
            return await self.domain_validator.validate(entities, domain)
        except Exception as e:
            self.logger.warning("Domain validation failed", error=str(e))
            return None

    def _create_error_result(
        self,
        request_id: str,
        input_type: InputType,
        error: str,
        elapsed_time: float,
    ) -> AnalysisResult:
        """Create an error result."""
        # Create empty quality score
        empty_dimension = DimensionScore(score=0, grade=Grade.F, issues=[])
        quality_score = QualityScore(
            overall_score=0,
            overall_grade=Grade.F,
            clarity=empty_dimension,
            completeness=empty_dimension,
            testability=empty_dimension,
            consistency=empty_dimension,
            recommendation="Analysis failed - please retry",
        )

        # Create empty structure
        structure = RequirementStructure(
            actor="",
            action="",
            object="",
            outcome="",
        )

        # Create empty extracted requirement
        extracted = ExtractedRequirement(
            title="",
            description="",
            structure=structure,
            input_type=input_type,
        )

        # Create metadata
        metadata = AnalysisMetadata(
            llm_provider=self.llm_client.provider_name,
            llm_model=self.llm_client.default_model,
            tokens_used=0,
            analysis_time_ms=elapsed_time * 1000,
            input_type=input_type,
            agent_version=self.VERSION,
        )

        return AnalysisResult(
            request_id=request_id,
            success=False,
            quality_score=quality_score,
            extracted_requirement=extracted,
            metadata=metadata,
            error=error,
        )
