"""gRPC client for Test Cases Agent."""

from typing import Optional

import grpc

from requirement_analysis_agent.models import AnalysisResult, ForwardTestCasesConfig, StructuredRequirement
from requirement_analysis_agent.proto import test_cases_pb2 as pb2
from requirement_analysis_agent.proto import test_cases_pb2_grpc as pb2_grpc
from requirement_analysis_agent.utils.logging import get_logger


class TestCasesAgentError(Exception):
    """Error communicating with Test Cases Agent."""
    pass


class TestCasesAgentClient:
    """gRPC client for Test Cases Agent service."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9003,
        timeout: int = 30,
    ):
        """Initialize Test Cases Agent client.

        Args:
            host: Test Cases Agent host
            port: Test Cases Agent port
            timeout: Default timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.address = f"{host}:{port}"
        self.logger = get_logger(__name__)
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[pb2_grpc.TestCasesServiceStub] = None

    async def connect(self) -> None:
        """Establish connection to Test Cases Agent."""
        try:
            self._channel = grpc.aio.insecure_channel(
                self.address,
                options=[
                    ("grpc.max_send_message_length", 50 * 1024 * 1024),
                    ("grpc.max_receive_message_length", 50 * 1024 * 1024),
                ],
            )
            self._stub = pb2_grpc.TestCasesServiceStub(self._channel)
            self.logger.info("Connected to Test Cases Agent", address=self.address)
        except Exception as e:
            self.logger.error("Failed to connect to Test Cases Agent", error=str(e))
            raise TestCasesAgentError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Close connection to Test Cases Agent."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
            self.logger.info("Disconnected from Test Cases Agent")

    async def health_check(self) -> bool:
        """Check if Test Cases Agent is healthy.

        Returns:
            True if healthy, False otherwise
        """
        if not self._stub:
            await self.connect()

        try:
            request = pb2.HealthCheckRequest()
            response = await self._stub.HealthCheck(request, timeout=5)
            return response.status == pb2.SERVING
        except grpc.aio.AioRpcError as e:
            self.logger.warning("Test Cases Agent health check failed", error=str(e))
            return False

    async def generate_test_cases(
        self,
        structured_requirement: StructuredRequirement,
        config: Optional[ForwardTestCasesConfig] = None,
    ) -> dict:
        """Generate test cases from a structured requirement.

        Args:
            structured_requirement: The structured requirement to generate tests for
            config: Test generation configuration

        Returns:
            Dictionary containing request_id, test_cases_count, and response data
        """
        if not self._stub:
            await self.connect()

        config = config or ForwardTestCasesConfig()

        try:
            # Build the request
            user_story = pb2.UserStoryInput(
                story=f"{structured_requirement.title}\n\n{structured_requirement.description}",
                acceptance_criteria=structured_requirement.acceptance_criteria,
                additional_context=structured_requirement.additional_context,
            )

            # Map test types to protobuf enums
            test_type_map = {
                "functional": pb2.FUNCTIONAL,
                "negative": pb2.NEGATIVE,
                "boundary": pb2.BOUNDARY,
                "edge_case": pb2.EDGE_CASE,
                "security": pb2.SECURITY,
                "performance": pb2.PERFORMANCE,
            }
            test_types = [
                test_type_map.get(t.lower(), pb2.FUNCTIONAL)
                for t in config.test_types
            ]

            # Map output format
            output_format_map = {
                "gherkin": pb2.GHERKIN,
                "traditional": pb2.TRADITIONAL,
                "json": pb2.JSON,
            }
            output_format = output_format_map.get(
                config.output_format.lower(), pb2.GHERKIN
            )

            # Map coverage level
            coverage_level_map = {
                "quick": pb2.QUICK,
                "standard": pb2.STANDARD,
                "exhaustive": pb2.EXHAUSTIVE,
            }
            coverage_level = coverage_level_map.get(
                config.coverage_level.lower(), pb2.STANDARD
            )

            generation_config = pb2.GenerationConfig(
                output_format=output_format,
                coverage_level=coverage_level,
                test_types=test_types,
                llm_provider=config.llm_provider,
                check_duplicates=config.check_duplicates,
                max_test_cases=config.max_test_cases,
            )

            domain_config = pb2.DomainConfig(
                domain=structured_requirement.domain,
                include_business_rules=True,
                include_edge_cases=True,
            )

            request = pb2.GenerateTestCasesRequest(
                request_id=structured_requirement.id,
                user_story=user_story,
                domain_config=domain_config,
                generation_config=generation_config,
            )

            response = await self._stub.GenerateTestCases(
                request, timeout=self.timeout
            )

            if not response.success:
                raise TestCasesAgentError(
                    f"Test case generation failed: {response.error_message}"
                )

            return {
                "request_id": response.request_id,
                "test_cases_count": len(response.test_cases),
                "test_cases": [
                    self._test_case_to_dict(tc) for tc in response.test_cases
                ],
                "metadata": {
                    "llm_provider": response.metadata.llm_provider,
                    "llm_model": response.metadata.llm_model,
                    "tokens_used": response.metadata.llm_tokens_used,
                    "generation_time_ms": response.metadata.generation_time_ms,
                    "duplicates_found": response.metadata.duplicates_found,
                },
            }

        except grpc.aio.AioRpcError as e:
            self.logger.error("Failed to generate test cases", error=str(e))
            raise TestCasesAgentError(f"Failed to generate test cases: {e}")

    def _test_case_to_dict(self, tc) -> dict:
        """Convert TestCase protobuf to dictionary."""
        return {
            "id": tc.id,
            "title": tc.title,
            "description": tc.description,
            "type": pb2.TestType.Name(tc.type),
            "priority": pb2.Priority.Name(tc.priority),
            "tags": list(tc.tags),
            "requirement_id": tc.requirement_id,
            "preconditions": list(tc.preconditions),
            "gherkin": tc.gherkin,
            "expected_result": tc.expected_result,
            "postconditions": list(tc.postconditions),
            "steps": [
                {
                    "order": step.order,
                    "action": step.action,
                    "expected_result": step.expected_result,
                    "test_data": step.test_data,
                }
                for step in tc.steps
            ],
        }

    def build_structured_requirement(
        self,
        analysis_result: AnalysisResult,
        include_generated_acs: bool = True,
        include_domain_context: bool = True,
    ) -> StructuredRequirement:
        """Build a StructuredRequirement from an AnalysisResult.

        Args:
            analysis_result: The analysis result to convert
            include_generated_acs: Whether to include AI-generated ACs
            include_domain_context: Whether to include domain validation info

        Returns:
            StructuredRequirement ready for test case generation
        """
        # Collect acceptance criteria
        acs = list(analysis_result.extracted_requirement.original_acs)

        if include_generated_acs:
            # Add accepted generated ACs
            for ac in analysis_result.generated_acs:
                if ac.accepted:
                    acs.append(ac.text)

        # Collect entities from structure and domain validation
        entities = list(analysis_result.extracted_requirement.structure.entities)

        if include_domain_context and analysis_result.domain_validation:
            for entity_mapping in analysis_result.domain_validation.entities_found:
                if entity_mapping.mapped_entity not in entities:
                    entities.append(entity_mapping.mapped_entity)

        # Build additional context
        context_parts = []

        if analysis_result.extracted_requirement.structure.outcome:
            context_parts.append(
                f"Expected outcome: {analysis_result.extracted_requirement.structure.outcome}"
            )

        if analysis_result.extracted_requirement.structure.constraints:
            context_parts.append(
                f"Constraints: {', '.join(analysis_result.extracted_requirement.structure.constraints)}"
            )

        if include_domain_context and analysis_result.domain_validation:
            applicable_rules = [
                r.rule for r in analysis_result.domain_validation.rules_applicable
                if r.relevance.value == "high"
            ]
            if applicable_rules:
                context_parts.append(f"Business rules: {'; '.join(applicable_rules)}")

        # Check if gaps were addressed (all high severity gaps have suggestions implemented)
        gaps_addressed = not any(
            g.severity.value == "high" for g in analysis_result.gaps
        )

        # Check if questions were answered
        questions_answered = all(
            q.answer is not None for q in analysis_result.questions
        )

        return StructuredRequirement(
            id=analysis_result.request_id,
            title=analysis_result.extracted_requirement.title,
            description=analysis_result.extracted_requirement.description,
            acceptance_criteria=acs,
            domain="ecommerce",  # Could be extracted from analysis config
            entities=entities,
            preconditions=analysis_result.extracted_requirement.structure.preconditions,
            additional_context="\n".join(context_parts),
            quality_score=analysis_result.quality_score.overall_score,
            gaps_addressed=gaps_addressed,
            questions_answered=questions_answered,
        )

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._channel is not None and self._stub is not None
