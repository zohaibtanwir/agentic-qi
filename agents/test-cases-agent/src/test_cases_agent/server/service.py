"""gRPC service implementation for Test Cases Agent."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

import grpc
from google.protobuf import json_format

from test_cases_agent.generation import get_generation_engine
from test_cases_agent.knowledge import get_knowledge_retriever, get_history_repository
from test_cases_agent.llm import LLMProviderType
from test_cases_agent.models import TestCaseRequest, TestType, Priority
from test_cases_agent.proto import test_cases_pb2, test_cases_pb2_grpc
from test_cases_agent.utils.logging import (
    get_logger,
    log_grpc_error,
    log_grpc_request,
    log_grpc_response,
)


class TestCasesService(test_cases_pb2_grpc.TestCasesServiceServicer):
    """Test Cases Service implementation."""

    def __init__(self) -> None:
        """Initialize the service."""
        self.logger = get_logger(__name__)
        self.generation_engine = get_generation_engine()
        self.knowledge_retriever = get_knowledge_retriever()
        self.history_repository = get_history_repository()
        self.stored_test_cases: Dict[str, Any] = {}  # In-memory storage for now
        self.logger.info("TestCasesService initialized with all components")

    async def GenerateTestCases(
        self,
        request: test_cases_pb2.GenerateTestCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.GenerateTestCasesResponse:
        """
        Generate test cases from requirements.

        Args:
            request: GenerateTestCasesRequest with user story, API spec, or free-form
            context: gRPC context

        Returns:
            GenerateTestCasesResponse with generated test cases
        """
        start_time = time.time()
        method = "GenerateTestCases"
        log_grpc_request(method, request)

        try:
            # Build TestCaseRequest from proto
            tc_request = self._build_test_case_request(request)

            # Always use Anthropic (only supported provider)
            llm_provider = LLMProviderType.ANTHROPIC

            # Generate test cases
            generation_response = await self.generation_engine.generate(tc_request, llm_provider)

            # Convert to proto response
            proto_test_cases = []
            test_cases_for_history = []
            for tc in generation_response.test_cases:
                proto_tc = self._convert_to_proto_test_case(tc)
                proto_test_cases.append(proto_tc)
                # Store for later retrieval
                self.stored_test_cases[proto_tc.id] = proto_tc
                # Collect for history
                test_cases_for_history.append({
                    "id": tc.id,
                    "title": tc.title,
                    "description": tc.description,
                    "test_type": tc.test_type,
                    "priority": tc.priority,
                    "preconditions": tc.preconditions,
                    "postconditions": tc.postconditions,
                    "expected_results": tc.expected_results,
                    "steps": [{"step_number": s.step_number, "action": s.action, "expected_result": s.expected_result} for s in tc.steps],
                    "tags": tc.metadata.tags if tc.metadata else [],
                })

            # Extract user story and acceptance criteria for history
            user_story = ""
            acceptance_criteria = []
            if proto_request.HasField("user_story"):
                user_story = proto_request.user_story.story
                acceptance_criteria = list(proto_request.user_story.acceptance_criteria)
            elif proto_request.HasField("free_form"):
                user_story = proto_request.free_form.requirement

            # Determine test types
            test_types = [self._proto_to_model_test_type(tt).value for tt in proto_request.generation_config.test_types] if proto_request.generation_config.test_types else ["functional"]

            # Save to history (non-blocking, fire and forget)
            try:
                await self.history_repository.create_from_generation(
                    user_story=user_story,
                    acceptance_criteria=acceptance_criteria,
                    test_cases=test_cases_for_history,
                    domain=proto_request.domain_config.domain if proto_request.HasField("domain_config") else "",
                    test_types=test_types,
                    coverage_level=self._coverage_level_to_string(proto_request.generation_config.coverage_level),
                    generation_method="llm",
                    model_used=generation_response.llm_provider,
                    generation_time_ms=int(generation_response.generation_time_ms),
                    status="success" if generation_response.success else "failed",
                    error_message="" if generation_response.success else generation_response.error,
                )
            except Exception as history_error:
                self.logger.warning(f"Failed to save history: {history_error}")

            response = test_cases_pb2.GenerateTestCasesResponse(
                request_id=request.request_id or f"req_{int(time.time())}",
                success=generation_response.success,
                test_cases=proto_test_cases,
                metadata=test_cases_pb2.GenerationMetadata(
                    test_cases_generated=generation_response.count,
                    generation_time_ms=generation_response.generation_time_ms,
                    llm_provider=generation_response.llm_provider,
                    llm_model=getattr(generation_response, 'llm_model', ''),
                    llm_tokens_used=generation_response.tokens_used or 0,
                ),
                error_message=generation_response.error if not generation_response.success else "",
            )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error generating test cases: {str(e)}")
            raise

    async def GetTestCase(
        self,
        request: test_cases_pb2.GetTestCaseRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.GetTestCaseResponse:
        """
        Get a specific test case by ID.

        Args:
            request: GetTestCaseRequest with test case ID
            context: gRPC context

        Returns:
            GetTestCaseResponse with the test case
        """
        start_time = time.time()
        method = "GetTestCase"
        log_grpc_request(method, request)

        try:
            if not request.test_case_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("test_case_id is required")
                raise grpc.RpcError()

            # Check in-memory storage
            if request.test_case_id in self.stored_test_cases:
                response = test_cases_pb2.GetTestCaseResponse(
                    success=True,
                    test_case=self.stored_test_cases[request.test_case_id],
                )
            else:
                response = test_cases_pb2.GetTestCaseResponse(
                    success=False,
                    error_message=f"Test case {request.test_case_id} not found",
                )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            if not context.code():
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error retrieving test case: {str(e)}")
            raise

    async def ListTestCases(
        self,
        request: test_cases_pb2.ListTestCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.ListTestCasesResponse:
        """
        List test cases with optional filters.

        Args:
            request: ListTestCasesRequest with filters
            context: gRPC context

        Returns:
            ListTestCasesResponse with filtered test cases
        """
        start_time = time.time()
        method = "ListTestCases"
        log_grpc_request(method, request)

        try:
            # Get all stored test cases
            all_test_cases = list(self.stored_test_cases.values())

            # Apply filters if provided
            filtered_cases = all_test_cases
            if request.filter:
                # Simple filtering by test type or priority
                filtered_cases = [
                    tc for tc in all_test_cases
                    if (not request.filter.test_types or tc.test_type in request.filter.test_types) and
                       (not request.filter.priorities or tc.priority in request.filter.priorities)
                ]

            # Apply pagination
            page_size = request.page_size or 10
            page_num = request.page_number or 1
            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            paginated_cases = filtered_cases[start_idx:end_idx]

            total_pages = (len(filtered_cases) + page_size - 1) // page_size

            response = test_cases_pb2.ListTestCasesResponse(
                test_cases=paginated_cases,
                total_count=len(filtered_cases),
                page_info=test_cases_pb2.PageInfo(
                    current_page=page_num,
                    total_pages=total_pages,
                    page_size=page_size,
                ),
            )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing test cases: {str(e)}")
            raise

    async def StoreTestCases(
        self,
        request: test_cases_pb2.StoreTestCasesRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.StoreTestCasesResponse:
        """
        Store test cases for learning.

        Args:
            request: StoreTestCasesRequest with test cases to store
            context: gRPC context

        Returns:
            StoreTestCasesResponse with storage confirmation
        """
        start_time = time.time()
        method = "StoreTestCases"
        log_grpc_request(method, request)

        try:
            # TODO: Implement actual storage in Phase 4 (Knowledge Layer)
            if not request.test_cases:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("At least one test case is required")
                raise grpc.RpcError()

            response = test_cases_pb2.StoreTestCasesResponse(
                success=True,
                stored_count=len(request.test_cases),
                message="Test case storage not yet implemented (stub response)",
            )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            if not context.code():
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error storing test cases: {str(e)}")
            raise

    async def AnalyzeCoverage(
        self,
        request: test_cases_pb2.AnalyzeCoverageRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.AnalyzeCoverageResponse:
        """
        Analyze requirement coverage of test cases.

        Args:
            request: AnalyzeCoverageRequest with test cases and requirements
            context: gRPC context

        Returns:
            AnalyzeCoverageResponse with coverage analysis
        """
        start_time = time.time()
        method = "AnalyzeCoverage"
        log_grpc_request(method, request)

        try:
            # Convert proto test cases to internal models
            from test_cases_agent.generation import CoverageAnalyzer
            analyzer = CoverageAnalyzer()

            # Simple conversion - just use the proto test cases as dict
            test_cases_dict = []
            for tc in request.test_cases:
                # Create a simplified dict representation
                test_cases_dict.append({
                    "id": tc.id,
                    "title": tc.title,
                    "test_type": tc.test_type,
                    "priority": tc.priority,
                    "steps": [{"action": s.action, "expected_result": s.expected_result} for s in tc.steps],
                })

            # Run analysis
            analysis = analyzer.analyze(
                test_cases_dict,
                requirements=list(request.requirements) if request.requirements else None,
            )

            # Convert to proto response
            response = test_cases_pb2.AnalyzeCoverageResponse(
                overall_coverage=analysis["coverage_score"],
                requirement_coverage=[],  # TODO: Convert requirement coverage
                gaps=[
                    test_cases_pb2.CoverageGap(
                        requirement_id=f"gap_{i}",
                        description=gap,
                        severity=test_cases_pb2.GapSeverity.MEDIUM,
                        suggested_test_types=[],
                    )
                    for i, gap in enumerate(analysis.get("gaps", []))
                ],
                recommendations=analysis.get("recommendations", []),
            )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error analyzing coverage: {str(e)}")
            raise

    async def HealthCheck(
        self,
        request: test_cases_pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.HealthCheckResponse:
        """
        Health check endpoint.

        Args:
            request: HealthCheckRequest
            context: gRPC context

        Returns:
            HealthCheckResponse with service status
        """
        return test_cases_pb2.HealthCheckResponse(
            status=test_cases_pb2.HealthCheckStatus.SERVING,
            version="1.0.0"
        )

    # ============================================================
    # History Operations
    # ============================================================

    async def ListHistory(
        self,
        request: test_cases_pb2.ListHistoryRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.ListHistoryResponse:
        """
        List generation history sessions.

        Args:
            request: ListHistoryRequest with pagination and filters
            context: gRPC context

        Returns:
            ListHistoryResponse with session summaries
        """
        start_time = time.time()
        method = "ListHistory"
        log_grpc_request(method, request)

        try:
            # Get limit and offset with defaults
            limit = request.limit if request.limit > 0 else 20
            offset = request.offset if request.offset >= 0 else 0
            domain = request.domain if request.domain else None
            status = request.status if request.status else None

            # Fetch from repository
            sessions = await self.history_repository.list(
                limit=limit,
                offset=offset,
                domain=domain,
                status=status,
            )

            # Get total count for pagination
            total_count = await self.history_repository.count(
                domain=domain,
                status=status,
            )

            # Convert to proto summaries
            proto_sessions = []
            for session in sessions:
                proto_sessions.append(test_cases_pb2.HistorySessionSummary(
                    session_id=session.session_id,
                    user_story_preview=session.get_preview(),
                    domain=session.domain,
                    test_types=session.test_types,
                    coverage_level=session.coverage_level,
                    test_case_count=session.test_case_count,
                    status=session.status,
                    created_at=session.created_at,
                ))

            response = test_cases_pb2.ListHistoryResponse(
                sessions=proto_sessions,
                total_count=total_count,
            )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing history: {str(e)}")
            raise

    async def GetHistorySession(
        self,
        request: test_cases_pb2.GetHistorySessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.GetHistorySessionResponse:
        """
        Get a specific history session with full test cases.

        Args:
            request: GetHistorySessionRequest with session ID
            context: gRPC context

        Returns:
            GetHistorySessionResponse with full session
        """
        start_time = time.time()
        method = "GetHistorySession"
        log_grpc_request(method, request)

        try:
            if not request.session_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("session_id is required")
                return test_cases_pb2.GetHistorySessionResponse(found=False)

            # Fetch from repository
            session = await self.history_repository.get(request.session_id)

            if not session:
                response = test_cases_pb2.GetHistorySessionResponse(found=False)
            else:
                # Convert test cases from dict to proto
                proto_test_cases = []
                for tc_dict in session.generated_test_cases:
                    proto_tc = self._dict_to_proto_test_case(tc_dict)
                    proto_test_cases.append(proto_tc)

                # Convert metadata to string map
                metadata = {k: str(v) for k, v in session.metadata.items()}

                proto_session = test_cases_pb2.HistorySession(
                    session_id=session.session_id,
                    user_story=session.user_story,
                    acceptance_criteria=session.acceptance_criteria,
                    domain=session.domain,
                    test_types=session.test_types,
                    coverage_level=session.coverage_level,
                    test_cases=proto_test_cases,
                    test_case_count=session.test_case_count,
                    generation_method=session.generation_method,
                    model_used=session.model_used,
                    generation_time_ms=session.generation_time_ms,
                    status=session.status,
                    error_message=session.error_message,
                    metadata=metadata,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                )

                response = test_cases_pb2.GetHistorySessionResponse(
                    session=proto_session,
                    found=True,
                )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting history session: {str(e)}")
            raise

    async def DeleteHistorySession(
        self,
        request: test_cases_pb2.DeleteHistorySessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> test_cases_pb2.DeleteHistorySessionResponse:
        """
        Delete a history session.

        Args:
            request: DeleteHistorySessionRequest with session ID
            context: gRPC context

        Returns:
            DeleteHistorySessionResponse with status
        """
        start_time = time.time()
        method = "DeleteHistorySession"
        log_grpc_request(method, request)

        try:
            if not request.session_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("session_id is required")
                return test_cases_pb2.DeleteHistorySessionResponse(
                    success=False,
                    message="session_id is required",
                )

            # Delete from repository
            deleted = await self.history_repository.delete(request.session_id)

            if deleted:
                response = test_cases_pb2.DeleteHistorySessionResponse(
                    success=True,
                    message=f"Session {request.session_id} deleted successfully",
                )
            else:
                response = test_cases_pb2.DeleteHistorySessionResponse(
                    success=False,
                    message=f"Session {request.session_id} not found",
                )

            duration_ms = (time.time() - start_time) * 1000
            log_grpc_response(method, response, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_grpc_error(method, e, duration_ms)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error deleting history session: {str(e)}")
            raise

    def _dict_to_proto_test_case(self, tc_dict: Dict[str, Any]) -> test_cases_pb2.TestCase:
        """Convert a test case dictionary to proto TestCase."""
        proto_steps = []
        steps = tc_dict.get("steps", [])
        if isinstance(steps, list):
            for i, step in enumerate(steps):
                if isinstance(step, dict):
                    proto_steps.append(test_cases_pb2.TestStep(
                        order=step.get("step_number", step.get("order", i + 1)),
                        action=step.get("action", ""),
                        expected_result=step.get("expected_result", ""),
                        test_data=json.dumps(step.get("test_data", {})) if step.get("test_data") else "",
                    ))

        # Handle preconditions - could be string or list
        preconditions = tc_dict.get("preconditions", [])
        if isinstance(preconditions, str):
            preconditions = preconditions.split("\n") if preconditions else []

        # Handle postconditions - could be string or list
        postconditions = tc_dict.get("postconditions", [])
        if isinstance(postconditions, str):
            postconditions = postconditions.split("\n") if postconditions else []

        # Get test type and priority
        test_type = tc_dict.get("test_type", "functional")
        if isinstance(test_type, str):
            test_type = self._model_to_proto_test_type(test_type)

        priority = tc_dict.get("priority", "medium")
        if isinstance(priority, str):
            priority = self._model_to_proto_priority(priority)

        return test_cases_pb2.TestCase(
            id=tc_dict.get("id", ""),
            title=tc_dict.get("title", ""),
            description=tc_dict.get("description", ""),
            type=test_type,
            priority=priority,
            status=test_cases_pb2.TestCaseStatus.DRAFT,
            preconditions=preconditions,
            steps=proto_steps,
            postconditions=postconditions,
            expected_result=tc_dict.get("expected_results", tc_dict.get("expected_result", "")),
            tags=tc_dict.get("tags", []),
        )

    def _build_test_case_request(self, proto_request: test_cases_pb2.GenerateTestCasesRequest) -> TestCaseRequest:
        """Convert proto request to internal TestCaseRequest."""
        # Determine requirement and entity type
        requirement = ""
        entity_type = ""
        domain_context = {}

        if proto_request.HasField("user_story"):
            requirement = proto_request.user_story.story
            entity_type = "user_story"
            domain_context["acceptance_criteria"] = list(proto_request.user_story.acceptance_criteria)
            if proto_request.user_story.additional_context:
                domain_context["additional_context"] = proto_request.user_story.additional_context
        elif proto_request.HasField("api_spec"):
            requirement = f"API Spec ({proto_request.api_spec.spec_format})"
            entity_type = "api"
            domain_context["api_details"] = {
                "spec": proto_request.api_spec.spec,
                "spec_format": proto_request.api_spec.spec_format,
                "endpoints": list(proto_request.api_spec.endpoints) if proto_request.api_spec.endpoints else [],
            }
        elif proto_request.HasField("free_form"):
            requirement = proto_request.free_form.requirement
            entity_type = proto_request.free_form.context.get("entity_type", "general") if proto_request.free_form.context else "general"
            domain_context = dict(proto_request.free_form.context) if proto_request.free_form.context else {}

        # Build config
        config = proto_request.generation_config
        return TestCaseRequest(
            requirement=requirement,
            entity_type=entity_type,
            test_types=[self._proto_to_model_test_type(tt) for tt in config.test_types] if config.test_types else None,
            count=config.count or 5,
            priority_focus=self._proto_to_model_priority(config.priority_focus) if hasattr(config, 'priority_focus') and config.priority_focus else None,
            include_edge_cases=config.include_edge_cases if hasattr(config, 'include_edge_cases') else True,
            include_negative_tests=config.include_negative_tests if hasattr(config, 'include_negative_tests') else True,
            detail_level=config.detail_level or "medium",
            domain_context=domain_context,
        )

    def _convert_to_proto_test_case(self, tc) -> test_cases_pb2.TestCase:
        """Convert internal TestCase to proto TestCase."""
        proto_steps = []
        for step in tc.steps:
            proto_steps.append(test_cases_pb2.TestStep(
                order=step.step_number,
                action=step.action,
                expected_result=step.expected_result,
                test_data=json.dumps(step.test_data) if step.test_data else "",
            ))

        return test_cases_pb2.TestCase(
            id=tc.id,
            title=tc.title,
            description=tc.description,
            type=self._model_to_proto_test_type(tc.test_type),
            priority=self._model_to_proto_priority(tc.priority),
            status=test_cases_pb2.TestCaseStatus.DRAFT,
            preconditions=tc.preconditions.split("\n") if tc.preconditions else [],
            steps=proto_steps,
            postconditions=tc.postconditions.split("\n") if tc.postconditions else [],
            expected_result=tc.expected_results or "",
            tags=tc.metadata.tags if tc.metadata else [],
        )

    def _proto_to_model_test_type(self, proto_type: test_cases_pb2.TestType) -> TestType:
        """Convert proto TestType to model TestType."""
        mapping = {
            test_cases_pb2.TestType.FUNCTIONAL: TestType.FUNCTIONAL,
            test_cases_pb2.TestType.INTEGRATION: TestType.INTEGRATION,
            test_cases_pb2.TestType.UNIT: TestType.UNIT,
            test_cases_pb2.TestType.PERFORMANCE: TestType.PERFORMANCE,
            test_cases_pb2.TestType.SECURITY: TestType.SECURITY,
            test_cases_pb2.TestType.USABILITY: TestType.USABILITY,
            test_cases_pb2.TestType.REGRESSION: TestType.REGRESSION,
            test_cases_pb2.TestType.SMOKE: TestType.SMOKE,
            test_cases_pb2.TestType.ACCEPTANCE: TestType.ACCEPTANCE,
        }
        return mapping.get(proto_type, TestType.FUNCTIONAL)

    def _model_to_proto_test_type(self, model_type: str) -> test_cases_pb2.TestType:
        """Convert model TestType to proto TestType."""
        mapping = {
            "functional": test_cases_pb2.TestType.FUNCTIONAL,
            "integration": test_cases_pb2.TestType.INTEGRATION,
            "unit": test_cases_pb2.TestType.UNIT,
            "performance": test_cases_pb2.TestType.PERFORMANCE,
            "security": test_cases_pb2.TestType.SECURITY,
            "usability": test_cases_pb2.TestType.USABILITY,
            "regression": test_cases_pb2.TestType.REGRESSION,
            "smoke": test_cases_pb2.TestType.SMOKE,
            "acceptance": test_cases_pb2.TestType.ACCEPTANCE,
            "edge_case": test_cases_pb2.TestType.FUNCTIONAL,  # Map to functional
            "negative": test_cases_pb2.TestType.FUNCTIONAL,  # Map to functional
        }
        return mapping.get(model_type, test_cases_pb2.TestType.FUNCTIONAL)

    def _proto_to_model_priority(self, proto_priority) -> Priority:
        """Convert proto Priority to model Priority."""
        mapping = {
            test_cases_pb2.Priority.CRITICAL: Priority.CRITICAL,
            test_cases_pb2.Priority.HIGH: Priority.HIGH,
            test_cases_pb2.Priority.MEDIUM: Priority.MEDIUM,
            test_cases_pb2.Priority.LOW: Priority.LOW,
        }
        return mapping.get(proto_priority, Priority.MEDIUM)

    def _model_to_proto_priority(self, model_priority: str):
        """Convert model Priority to proto Priority."""
        mapping = {
            "critical": test_cases_pb2.Priority.CRITICAL,
            "high": test_cases_pb2.Priority.HIGH,
            "medium": test_cases_pb2.Priority.MEDIUM,
            "low": test_cases_pb2.Priority.LOW,
        }
        return mapping.get(model_priority.lower(), test_cases_pb2.Priority.MEDIUM)

    def _coverage_level_to_string(self, coverage_level: test_cases_pb2.CoverageLevel) -> str:
        """Convert proto CoverageLevel to string."""
        mapping = {
            test_cases_pb2.CoverageLevel.QUICK: "minimal",
            test_cases_pb2.CoverageLevel.STANDARD: "standard",
            test_cases_pb2.CoverageLevel.EXHAUSTIVE: "comprehensive",
        }
        return mapping.get(coverage_level, "standard")