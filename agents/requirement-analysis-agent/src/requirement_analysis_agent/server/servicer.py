"""gRPC Servicer implementation for Requirement Analysis Service."""

import uuid
from typing import Optional

import grpc

from requirement_analysis_agent.analysis import AnalysisEngine
from requirement_analysis_agent.clients import (
    DomainAgentClient,
    DomainValidator,
    TestCasesAgentClient,
)
from requirement_analysis_agent.config import Settings
from requirement_analysis_agent.exporters import JSONExporter, TextExporter
from requirement_analysis_agent.llm.anthropic_client import AnthropicClient
from requirement_analysis_agent.models import (
    AnalysisConfig,
    AnalysisResult,
    ExportConfig,
    ForwardTestCasesConfig,
    FreeFormInput,
    InputType,
    JiraStoryInput,
    TranscriptInput,
)
from requirement_analysis_agent.parsers import (
    FreeFormParser,
    JiraStoryParser,
    TranscriptParser,
)
from requirement_analysis_agent.parsers.base import ParsedInput
from requirement_analysis_agent.proto import requirement_analysis_pb2 as pb2
from requirement_analysis_agent.proto import requirement_analysis_pb2_grpc as pb2_grpc
from requirement_analysis_agent.storage import HistoryRepository, WeaviateClient
from requirement_analysis_agent.utils.logging import get_logger


logger = get_logger(__name__)


class RequirementAnalysisServicer(pb2_grpc.RequirementAnalysisServiceServicer):
    """gRPC servicer implementation for requirement analysis."""

    def __init__(
        self,
        settings: Settings,
        llm_client: Optional[AnthropicClient] = None,
        domain_client: Optional[DomainAgentClient] = None,
        weaviate_client: Optional[WeaviateClient] = None,
        test_cases_client: Optional[TestCasesAgentClient] = None,
    ):
        """Initialize servicer.

        Args:
            settings: Application settings
            llm_client: Optional LLM client (creates new if not provided)
            domain_client: Optional Domain Agent client
            weaviate_client: Optional Weaviate client
            test_cases_client: Optional Test Cases Agent client
        """
        self.settings = settings

        # Initialize LLM client
        self.llm_client = llm_client or AnthropicClient(
            api_key=settings.anthropic_api_key,
            default_model=settings.llm_model,
        )

        # Initialize Domain client
        self.domain_client = domain_client
        self.domain_validator = None
        if domain_client:
            self.domain_validator = DomainValidator(domain_client)

        # Initialize Weaviate client
        self.weaviate_client = weaviate_client
        self.history_repo = None
        if weaviate_client:
            self.history_repo = HistoryRepository(weaviate_client)

        # Initialize Test Cases Agent client
        self.test_cases_client = test_cases_client

        # Initialize parsers
        self.jira_parser = JiraStoryParser()
        self.freeform_parser = FreeFormParser()
        self.transcript_parser = TranscriptParser()

        # Initialize analysis engine
        self.analysis_engine = AnalysisEngine(
            llm_client=self.llm_client,
            domain_validator=self.domain_validator,
        )

        logger.info("RequirementAnalysisServicer initialized")

    async def initialize(self) -> None:
        """Initialize async components."""
        await self.llm_client.initialize()
        if self.weaviate_client:
            await self.weaviate_client.connect()
        if self.domain_client:
            await self.domain_client.connect()
        if self.test_cases_client:
            await self.test_cases_client.connect()
        logger.info("Servicer async components initialized")

    async def shutdown(self) -> None:
        """Shutdown async components."""
        if self.weaviate_client:
            await self.weaviate_client.disconnect()
        if self.domain_client:
            await self.domain_client.disconnect()
        if self.test_cases_client:
            await self.test_cases_client.disconnect()
        logger.info("Servicer shutdown complete")

    async def AnalyzeRequirement(
        self,
        request: pb2.AnalyzeRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.AnalyzeResponse:
        """Analyze a requirement from any input type."""
        request_id = request.request_id or str(uuid.uuid4())
        logger.info("AnalyzeRequirement called", request_id=request_id)

        try:
            # Parse input based on type
            parsed_input = self._parse_input(request)
            if not parsed_input:
                return self._create_error_response(
                    request_id,
                    "No valid input provided. Must provide jira_story, free_form, or transcript.",
                )

            # Build analysis config
            config = self._build_config(request.config) if request.HasField("config") else None

            # Run analysis
            result = await self.analysis_engine.analyze(parsed_input, config)

            # Save to history
            if self.history_repo and result.success:
                await self.history_repo.save(result)

            return self._result_to_response(result)

        except Exception as e:
            logger.error("AnalyzeRequirement failed", request_id=request_id, error=str(e))
            return self._create_error_response(request_id, str(e))

    async def ReanalyzeRequirement(
        self,
        request: pb2.ReanalyzeRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.AnalyzeResponse:
        """Re-analyze with updates."""
        request_id = request.request_id or str(uuid.uuid4())
        logger.info(
            "ReanalyzeRequirement called",
            request_id=request_id,
            original_id=request.original_request_id,
        )

        try:
            # Retrieve original result
            if not self.history_repo:
                return self._create_error_response(
                    request_id,
                    "History storage not available for reanalysis",
                )

            original_result = await self.history_repo.get_by_request_id(
                request.original_request_id
            )
            if not original_result:
                return self._create_error_response(
                    request_id,
                    f"Original analysis not found: {request.original_request_id}",
                )

            # Build answered questions map
            answered_questions = {
                q.question_id: q.answer for q in request.answered_questions
            }

            # Build config
            config = self._build_config(request.config) if request.HasField("config") else None

            # Run reanalysis
            result = await self.analysis_engine.reanalyze(
                original_result=original_result,
                updated_title=request.updated_title or None,
                updated_description=request.updated_description or None,
                updated_acs=list(request.updated_acs) or None,
                answered_questions=answered_questions or None,
                config=config,
            )

            # Save updated result
            if result.success:
                await self.history_repo.save(result)

            return self._result_to_response(result)

        except Exception as e:
            logger.error("ReanalyzeRequirement failed", request_id=request_id, error=str(e))
            return self._create_error_response(request_id, str(e))

    async def HealthCheck(
        self,
        request: pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.HealthCheckResponse:
        """Health check endpoint."""
        components = {}

        # Check LLM
        components["llm"] = "healthy" if self.llm_client.is_available() else "unavailable"

        # Check Weaviate
        if self.weaviate_client:
            components["weaviate"] = "healthy" if self.weaviate_client.is_connected else "disconnected"
        else:
            components["weaviate"] = "not_configured"

        # Check Domain Agent
        if self.domain_client:
            try:
                is_healthy = await self.domain_client.health_check()
                components["domain_agent"] = "healthy" if is_healthy else "unhealthy"
            except Exception:
                components["domain_agent"] = "unavailable"
        else:
            components["domain_agent"] = "not_configured"

        # Determine overall status
        critical_components = ["llm"]
        all_healthy = all(
            components.get(c) == "healthy" for c in critical_components
        )
        status = "healthy" if all_healthy else "degraded"

        return pb2.HealthCheckResponse(
            status=status,
            components=components,
        )

    async def ExportAnalysis(
        self,
        request: pb2.ExportRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ExportResponse:
        """Export analysis result in specified format."""
        request_id = request.request_id or str(uuid.uuid4())
        logger.info(
            "ExportAnalysis called",
            request_id=request_id,
            analysis_request_id=request.analysis_request_id,
            format=request.format,
        )

        try:
            # Validate format
            export_format = request.format.lower() if request.format else "json"
            if export_format not in ("json", "text"):
                return pb2.ExportResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Unsupported format: {export_format}. Use 'json' or 'text'.",
                )

            # Retrieve the analysis
            if not self.history_repo:
                return pb2.ExportResponse(
                    request_id=request_id,
                    success=False,
                    error="History storage not available for export",
                )

            analysis_result = await self.history_repo.get_by_request_id(
                request.analysis_request_id
            )
            if not analysis_result:
                return pb2.ExportResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Analysis not found: {request.analysis_request_id}",
                )

            # Build export config
            export_config = ExportConfig(
                format=export_format,
                include_recommendations=request.include_recommendations,
                include_generated_acs=request.include_generated_acs,
            )

            # Create appropriate exporter
            if export_format == "json":
                exporter = JSONExporter(config=export_config)
            else:
                exporter = TextExporter(config=export_config)

            # Generate export content
            content = exporter.export(analysis_result)
            filename = exporter.generate_filename(analysis_result)

            logger.info(
                "ExportAnalysis completed",
                request_id=request_id,
                format=export_format,
                content_length=len(content),
            )

            return pb2.ExportResponse(
                request_id=request_id,
                success=True,
                format=export_format,
                content=content,
                filename=filename,
            )

        except Exception as e:
            logger.error("ExportAnalysis failed", request_id=request_id, error=str(e))
            return pb2.ExportResponse(
                request_id=request_id,
                success=False,
                error=str(e),
            )

    async def ForwardToTestCases(
        self,
        request: pb2.ForwardRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ForwardResponse:
        """Forward analyzed requirement to Test Cases Agent."""
        request_id = request.request_id or str(uuid.uuid4())
        logger.info(
            "ForwardToTestCases called",
            request_id=request_id,
            analysis_request_id=request.analysis_request_id,
        )

        try:
            # Check if Test Cases Agent is configured
            if not self.test_cases_client:
                return pb2.ForwardResponse(
                    request_id=request_id,
                    success=False,
                    error="Test Cases Agent not configured",
                )

            # Retrieve the analysis
            if not self.history_repo:
                return pb2.ForwardResponse(
                    request_id=request_id,
                    success=False,
                    error="History storage not available",
                )

            analysis_result = await self.history_repo.get_by_request_id(
                request.analysis_request_id
            )
            if not analysis_result:
                return pb2.ForwardResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Analysis not found: {request.analysis_request_id}",
                )

            # Check if ready for test generation
            if not analysis_result.ready_for_test_generation:
                blockers = ", ".join(analysis_result.blockers) if analysis_result.blockers else "Not ready"
                return pb2.ForwardResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Analysis not ready for test generation: {blockers}",
                )

            # Build structured requirement
            structured_req = self.test_cases_client.build_structured_requirement(
                analysis_result=analysis_result,
                include_generated_acs=request.include_generated_acs,
                include_domain_context=request.include_domain_context,
            )

            # Build forward config
            tc_config = request.test_cases_config if request.HasField("test_cases_config") else None
            forward_config = None
            if tc_config:
                forward_config = ForwardTestCasesConfig(
                    output_format=tc_config.output_format or "gherkin",
                    coverage_level=tc_config.coverage_level or "standard",
                    test_types=list(tc_config.test_types) or ["functional", "negative"],
                    llm_provider=tc_config.llm_provider or "anthropic",
                    check_duplicates=tc_config.check_duplicates,
                    max_test_cases=tc_config.max_test_cases or 20,
                )

            # Forward to Test Cases Agent
            result = await self.test_cases_client.generate_test_cases(
                structured_requirement=structured_req,
                config=forward_config,
            )

            # Serialize structured requirement for response
            structured_req_json = structured_req.model_dump_json()

            logger.info(
                "ForwardToTestCases completed",
                request_id=request_id,
                test_cases_count=result["test_cases_count"],
            )

            return pb2.ForwardResponse(
                request_id=request_id,
                success=True,
                test_cases_request_id=result["request_id"],
                test_cases_generated=result["test_cases_count"],
                structured_requirement_json=structured_req_json,
            )

        except Exception as e:
            logger.error("ForwardToTestCases failed", request_id=request_id, error=str(e))
            return pb2.ForwardResponse(
                request_id=request_id,
                success=False,
                error=str(e),
            )

    # =========================================================================
    # History Management Methods
    # =========================================================================

    async def ListHistory(
        self,
        request: pb2.ListHistoryRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ListHistoryResponse:
        """List analysis history with pagination and filters."""
        logger.info(
            "ListHistory called",
            limit=request.limit,
            offset=request.offset,
        )

        try:
            if not self.history_repo:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("History storage not available")
                return pb2.ListHistoryResponse()

            # Extract filters
            filters = request.filters if request.HasField("filters") else None
            input_type = filters.input_type if filters else None
            quality_grade = filters.quality_grade if filters else None
            ready_status = filters.ready_status if filters else None
            date_from = filters.date_from if filters else None
            date_to = filters.date_to if filters else None

            # Get results with filters
            limit = request.limit or 20
            offset = request.offset or 0

            summaries, total_count = await self.history_repo.list_with_filters(
                limit=limit,
                offset=offset,
                input_type=input_type or None,
                quality_grade=quality_grade or None,
                ready_status=ready_status or None,
                date_from=date_from or None,
                date_to=date_to or None,
            )

            # Convert to proto messages
            sessions = [
                pb2.HistorySessionSummary(
                    session_id=s["session_id"],
                    title=s["title"],
                    quality_score=s["quality_score"],
                    quality_grade=s["quality_grade"],
                    gaps_count=s["gaps_count"],
                    questions_count=s["questions_count"],
                    generated_acs_count=s["generated_acs_count"],
                    ready_for_tests=s["ready_for_tests"],
                    input_type=s["input_type"],
                    llm_model=s["llm_model"],
                    created_at=s["created_at"],
                )
                for s in summaries
            ]

            has_more = (offset + len(sessions)) < total_count

            logger.info(
                "ListHistory completed",
                count=len(sessions),
                total=total_count,
                has_more=has_more,
            )

            return pb2.ListHistoryResponse(
                sessions=sessions,
                total_count=total_count,
                has_more=has_more,
            )

        except Exception as e:
            logger.error("ListHistory failed", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.ListHistoryResponse()

    async def GetHistorySession(
        self,
        request: pb2.GetHistorySessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.GetHistorySessionResponse:
        """Get full details of a history session."""
        session_id = request.session_id
        logger.info("GetHistorySession called", session_id=session_id)

        try:
            if not self.history_repo:
                return pb2.GetHistorySessionResponse(
                    success=False,
                    error="History storage not available",
                )

            # Get full session
            session_data = await self.history_repo.get_full_session(session_id)
            if not session_data:
                return pb2.GetHistorySessionResponse(
                    success=False,
                    error=f"Session not found: {session_id}",
                )

            result = session_data["analysis_result"]

            # Build the full HistorySession proto
            session = pb2.HistorySession(
                session_id=session_id,
                quality_score=self._build_quality_score_proto(result.quality_score),
                extracted_requirement=self._build_extracted_proto(result.extracted_requirement),
                gaps=[self._build_gap_proto(g) for g in result.gaps],
                questions=[self._build_question_proto(q) for q in result.questions],
                generated_acs=[self._build_ac_proto(ac) for ac in result.generated_acs],
                domain_validation=self._build_domain_validation_proto(result.domain_validation) if result.domain_validation else None,
                ready_for_test_generation=result.ready_for_test_generation,
                blockers=result.blockers,
                input_type=result.metadata.input_type.value,
                llm_provider=result.metadata.llm_provider,
                llm_model=result.metadata.llm_model,
                tokens_used=result.metadata.tokens_used,
                analysis_time_ms=result.metadata.analysis_time_ms,
                created_at=session_data["created_at"],
                updated_at=session_data["updated_at"],
            )

            logger.info("GetHistorySession completed", session_id=session_id)

            return pb2.GetHistorySessionResponse(
                success=True,
                session=session,
            )

        except Exception as e:
            logger.error("GetHistorySession failed", session_id=session_id, error=str(e))
            return pb2.GetHistorySessionResponse(
                success=False,
                error=str(e),
            )

    async def DeleteHistorySession(
        self,
        request: pb2.DeleteHistorySessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.DeleteHistorySessionResponse:
        """Delete a history session."""
        session_id = request.session_id
        logger.info("DeleteHistorySession called", session_id=session_id)

        try:
            if not self.history_repo:
                return pb2.DeleteHistorySessionResponse(
                    success=False,
                    error="History storage not available",
                )

            deleted = await self.history_repo.delete(session_id)
            if not deleted:
                return pb2.DeleteHistorySessionResponse(
                    success=False,
                    error=f"Session not found or could not be deleted: {session_id}",
                )

            logger.info("DeleteHistorySession completed", session_id=session_id)

            return pb2.DeleteHistorySessionResponse(success=True)

        except Exception as e:
            logger.error("DeleteHistorySession failed", session_id=session_id, error=str(e))
            return pb2.DeleteHistorySessionResponse(
                success=False,
                error=str(e),
            )

    async def SearchHistory(
        self,
        request: pb2.SearchHistoryRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.SearchHistoryResponse:
        """Search history by keyword."""
        query = request.query
        limit = request.limit or 10
        logger.info("SearchHistory called", query=query, limit=limit)

        try:
            if not self.history_repo:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("History storage not available")
                return pb2.SearchHistoryResponse()

            # Validate query
            if not query or not query.strip():
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Search query is required")
                return pb2.SearchHistoryResponse()

            # Search
            summaries, total_count = await self.history_repo.search(query, limit=limit)

            # Convert to proto messages
            sessions = [
                pb2.HistorySessionSummary(
                    session_id=s["session_id"],
                    title=s["title"],
                    quality_score=s["quality_score"],
                    quality_grade=s["quality_grade"],
                    gaps_count=s["gaps_count"],
                    questions_count=s["questions_count"],
                    generated_acs_count=s["generated_acs_count"],
                    ready_for_tests=s["ready_for_tests"],
                    input_type=s["input_type"],
                    llm_model=s["llm_model"],
                    created_at=s["created_at"],
                )
                for s in summaries
            ]

            logger.info("SearchHistory completed", query=query, count=len(sessions))

            return pb2.SearchHistoryResponse(
                sessions=sessions,
                total_count=total_count,
            )

        except Exception as e:
            logger.error("SearchHistory failed", query=query, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SearchHistoryResponse()

    # =========================================================================
    # Helper Methods for History Proto Building
    # =========================================================================

    def _build_quality_score_proto(self, qs) -> pb2.QualityScore:
        """Build QualityScore proto from model."""
        return pb2.QualityScore(
            overall_score=qs.overall_score,
            overall_grade=qs.overall_grade.value,
            clarity=pb2.DimensionScore(
                score=qs.clarity.score,
                grade=qs.clarity.grade.value,
                issues=qs.clarity.issues,
            ),
            completeness=pb2.DimensionScore(
                score=qs.completeness.score,
                grade=qs.completeness.grade.value,
                issues=qs.completeness.issues,
            ),
            testability=pb2.DimensionScore(
                score=qs.testability.score,
                grade=qs.testability.grade.value,
                issues=qs.testability.issues,
            ),
            consistency=pb2.DimensionScore(
                score=qs.consistency.score,
                grade=qs.consistency.grade.value,
                issues=qs.consistency.issues,
            ),
            recommendation=qs.recommendation,
        )

    def _build_extracted_proto(self, er) -> pb2.ExtractedRequirement:
        """Build ExtractedRequirement proto from model."""
        structure = er.structure
        return pb2.ExtractedRequirement(
            title=er.title,
            description=er.description,
            structure=pb2.RequirementStructure(
                actor=structure.actor,
                secondary_actors=structure.secondary_actors,
                action=structure.action,
                object=structure.object,
                outcome=structure.outcome,
                preconditions=structure.preconditions,
                postconditions=structure.postconditions,
                triggers=structure.triggers,
                constraints=structure.constraints,
                entities=structure.entities,
            ),
            original_acs=er.original_acs,
            input_type=er.input_type.value,
        )

    def _build_gap_proto(self, g) -> pb2.Gap:
        """Build Gap proto from model."""
        return pb2.Gap(
            id=g.id,
            category=g.category.value,
            severity=g.severity.value,
            description=g.description,
            location=g.location,
            suggestion=g.suggestion,
        )

    def _build_question_proto(self, q) -> pb2.ClarifyingQuestion:
        """Build ClarifyingQuestion proto from model."""
        return pb2.ClarifyingQuestion(
            id=q.id,
            priority=q.priority.value,
            category=q.category.value,
            question=q.question,
            context=q.context,
            suggested_answers=q.suggested_answers,
            answer=q.answer or "",
        )

    def _build_ac_proto(self, ac) -> pb2.GeneratedAC:
        """Build GeneratedAC proto from model."""
        return pb2.GeneratedAC(
            id=ac.id,
            source=ac.source.value,
            confidence=ac.confidence,
            text=ac.text,
            gherkin=ac.gherkin,
            accepted=ac.accepted,
        )

    def _build_domain_validation_proto(self, dv) -> pb2.DomainValidation:
        """Build DomainValidation proto from model."""
        return pb2.DomainValidation(
            valid=dv.valid,
            entities_found=[
                pb2.EntityMapping(
                    term=e.term,
                    mapped_entity=e.mapped_entity,
                    confidence=e.confidence,
                    domain_description=e.domain_description,
                )
                for e in dv.entities_found
            ],
            rules_applicable=[
                pb2.ApplicableRule(
                    rule_id=r.rule_id,
                    rule=r.rule,
                    relevance=r.relevance.value,
                )
                for r in dv.rules_applicable
            ],
            warnings=[
                pb2.DomainWarning(
                    type=w.type,
                    message=w.message,
                    suggestion=w.suggestion,
                )
                for w in dv.warnings
            ],
        )

    # =========================================================================
    # Input Parsing and Config Building
    # =========================================================================

    def _parse_input(self, request: pb2.AnalyzeRequest) -> Optional[ParsedInput]:
        """Parse the input from request based on type."""
        input_type = request.WhichOneof("input")

        if input_type == "jira_story":
            jira = request.jira_story
            jira_input = JiraStoryInput(
                key=jira.key,
                summary=jira.summary,
                description=jira.description,
                acceptance_criteria=list(jira.acceptance_criteria),
                story_points=jira.story_points,
                labels=list(jira.labels),
                components=list(jira.components),
                priority=jira.priority,
                reporter=jira.reporter,
                assignee=jira.assignee,
                raw_json=jira.raw_json or None,
            )
            return self.jira_parser.parse(jira_input)

        elif input_type == "free_form":
            ff = request.free_form
            ff_input = FreeFormInput(
                text=ff.text,
                context=ff.context,
                title=ff.title,
            )
            return self.freeform_parser.parse(ff_input)

        elif input_type == "transcript":
            tr = request.transcript
            tr_input = TranscriptInput(
                transcript=tr.transcript,
                meeting_title=tr.meeting_title,
                meeting_date=tr.meeting_date,
                participants=list(tr.participants),
            )
            return self.transcript_parser.parse(tr_input)

        return None

    def _build_config(self, config: pb2.AnalysisConfig) -> AnalysisConfig:
        """Build AnalysisConfig from proto config."""
        return AnalysisConfig(
            include_domain_validation=config.include_domain_validation,
            generate_acceptance_criteria=config.generate_acceptance_criteria,
            generate_questions=config.generate_questions,
            llm_provider=config.llm_provider or "anthropic",
            domain=config.domain or "ecommerce",
        )

    def _result_to_response(self, result: AnalysisResult) -> pb2.AnalyzeResponse:
        """Convert AnalysisResult to proto response."""
        # Build quality score
        quality_score = pb2.QualityScore(
            overall_score=result.quality_score.overall_score,
            overall_grade=result.quality_score.overall_grade.value,
            clarity=pb2.DimensionScore(
                score=result.quality_score.clarity.score,
                grade=result.quality_score.clarity.grade.value,
                issues=result.quality_score.clarity.issues,
            ),
            completeness=pb2.DimensionScore(
                score=result.quality_score.completeness.score,
                grade=result.quality_score.completeness.grade.value,
                issues=result.quality_score.completeness.issues,
            ),
            testability=pb2.DimensionScore(
                score=result.quality_score.testability.score,
                grade=result.quality_score.testability.grade.value,
                issues=result.quality_score.testability.issues,
            ),
            consistency=pb2.DimensionScore(
                score=result.quality_score.consistency.score,
                grade=result.quality_score.consistency.grade.value,
                issues=result.quality_score.consistency.issues,
            ),
            recommendation=result.quality_score.recommendation,
        )

        # Build extracted requirement
        structure = result.extracted_requirement.structure
        extracted = pb2.ExtractedRequirement(
            title=result.extracted_requirement.title,
            description=result.extracted_requirement.description,
            structure=pb2.RequirementStructure(
                actor=structure.actor,
                secondary_actors=structure.secondary_actors,
                action=structure.action,
                object=structure.object,
                outcome=structure.outcome,
                preconditions=structure.preconditions,
                postconditions=structure.postconditions,
                triggers=structure.triggers,
                constraints=structure.constraints,
                entities=structure.entities,
            ),
            original_acs=result.extracted_requirement.original_acs,
            input_type=result.extracted_requirement.input_type.value,
        )

        # Build gaps
        gaps = [
            pb2.Gap(
                id=g.id,
                category=g.category.value,
                severity=g.severity.value,
                description=g.description,
                location=g.location,
                suggestion=g.suggestion,
            )
            for g in result.gaps
        ]

        # Build questions
        questions = [
            pb2.ClarifyingQuestion(
                id=q.id,
                priority=q.priority.value,
                category=q.category.value,
                question=q.question,
                context=q.context,
                suggested_answers=q.suggested_answers,
                answer=q.answer or "",
            )
            for q in result.questions
        ]

        # Build generated ACs
        generated_acs = [
            pb2.GeneratedAC(
                id=ac.id,
                source=ac.source.value,
                confidence=ac.confidence,
                text=ac.text,
                gherkin=ac.gherkin,
                accepted=ac.accepted,
            )
            for ac in result.generated_acs
        ]

        # Build domain validation
        domain_validation = None
        if result.domain_validation:
            dv = result.domain_validation
            domain_validation = pb2.DomainValidation(
                valid=dv.valid,
                entities_found=[
                    pb2.EntityMapping(
                        term=e.term,
                        mapped_entity=e.mapped_entity,
                        confidence=e.confidence,
                        domain_description=e.domain_description,
                    )
                    for e in dv.entities_found
                ],
                rules_applicable=[
                    pb2.ApplicableRule(
                        rule_id=r.rule_id,
                        rule=r.rule,
                        relevance=r.relevance.value,
                    )
                    for r in dv.rules_applicable
                ],
                warnings=[
                    pb2.DomainWarning(
                        type=w.type,
                        message=w.message,
                        suggestion=w.suggestion,
                    )
                    for w in dv.warnings
                ],
            )

        # Build metadata
        metadata = pb2.AnalysisMetadata(
            llm_provider=result.metadata.llm_provider,
            llm_model=result.metadata.llm_model,
            tokens_used=result.metadata.tokens_used,
            analysis_time_ms=result.metadata.analysis_time_ms,
            input_type=result.metadata.input_type.value,
            agent_version=result.metadata.agent_version,
        )

        return pb2.AnalyzeResponse(
            request_id=result.request_id,
            success=result.success,
            quality_score=quality_score,
            extracted_requirement=extracted,
            gaps=gaps,
            questions=questions,
            generated_acs=generated_acs,
            domain_validation=domain_validation,
            ready_for_test_generation=result.ready_for_test_generation,
            blockers=result.blockers,
            metadata=metadata,
            error=result.error or "",
        )

    def _create_error_response(self, request_id: str, error: str) -> pb2.AnalyzeResponse:
        """Create an error response."""
        return pb2.AnalyzeResponse(
            request_id=request_id,
            success=False,
            error=error,
        )
