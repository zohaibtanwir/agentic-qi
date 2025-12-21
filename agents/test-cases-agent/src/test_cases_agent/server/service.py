"""gRPC service implementation for Test Cases Agent."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

import grpc
from google.protobuf import json_format

from test_cases_agent.generation import get_generation_engine
from test_cases_agent.knowledge import get_knowledge_retriever
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

            # Determine LLM provider
            llm_provider = None
            if request.generation_config and request.generation_config.llm_provider:
                provider_map = {
                    "anthropic": LLMProviderType.ANTHROPIC,
                    "openai": LLMProviderType.OPENAI,
                    "gemini": LLMProviderType.GEMINI,
                }
                llm_provider = provider_map.get(request.generation_config.llm_provider.lower())

            # Generate test cases
            generation_response = await self.generation_engine.generate(tc_request, llm_provider)

            # Convert to proto response
            proto_test_cases = []
            for tc in generation_response.test_cases:
                proto_tc = self._convert_to_proto_test_case(tc)
                proto_test_cases.append(proto_tc)
                # Store for later retrieval
                self.stored_test_cases[proto_tc.id] = proto_tc

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