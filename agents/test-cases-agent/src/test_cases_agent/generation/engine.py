"""Test case generation engine - orchestrates the generation process."""

import time
from typing import Any, Dict, List, Optional

from test_cases_agent.clients import get_domain_agent_client, get_test_data_agent_client
from test_cases_agent.generation.coverage_analyzer import CoverageAnalyzer
from test_cases_agent.generation.formatter import TestCaseFormatter
from test_cases_agent.generation.parser import TestCaseParser
from test_cases_agent.generation.prompt_builder import PromptBuilder
from test_cases_agent.knowledge import get_knowledge_retriever
from test_cases_agent.llm import GenerationConfig, LLMProviderType, Message, get_llm_router
from test_cases_agent.models import TestCase, TestCaseRequest, TestCaseResponse
from test_cases_agent.utils.logging import get_logger


class GenerationEngine:
    """
    Main engine for test case generation.

    Orchestrates:
    - Context gathering from domain and knowledge
    - Prompt building
    - LLM generation
    - Response parsing
    - Coverage analysis
    - Formatting
    """

    def __init__(self):
        """Initialize generation engine."""
        self.logger = get_logger(__name__)

        # Initialize components
        self.llm_router = get_llm_router()
        self.knowledge_retriever = get_knowledge_retriever()
        self.domain_client = get_domain_agent_client()
        self.test_data_client = get_test_data_agent_client()
        self.prompt_builder = PromptBuilder()
        self.parser = TestCaseParser()
        self.coverage_analyzer = CoverageAnalyzer()
        self.formatter = TestCaseFormatter()

        # Track if test data agent is available (to avoid repeated connection attempts)
        self._test_data_agent_available: Optional[bool] = None

    async def generate(
        self,
        request: TestCaseRequest,
        llm_provider: Optional[LLMProviderType] = None,
    ) -> TestCaseResponse:
        """
        Generate test cases from request.

        Args:
            request: Test case generation request
            llm_provider: Optional specific LLM provider

        Returns:
            Test case response with generated cases
        """
        start_time = time.time()

        try:
            # 1. Gather context
            context = await self._gather_context(request)

            # 2. Build prompt
            prompt = self.prompt_builder.build(request, context)

            # 3. Generate with LLM
            llm_response = await self._generate_with_llm(prompt, llm_provider)

            # 4. Parse response
            test_cases = self.parser.parse(llm_response, request.format_style)

            # 5. Enrich test cases
            test_cases = await self._enrich_test_cases(test_cases, request, context)

            # 6. Analyze coverage
            coverage_analysis = self.coverage_analyzer.analyze(
                test_cases,
                request.domain_context.get("requirements", [])
                if request.domain_context
                else None,
            )

            # 7. Learn from generation
            await self._learn_from_generation(test_cases, request)

            # 8. Build response
            response = TestCaseResponse(
                success=True,
                test_cases=test_cases,
                count=len(test_cases),
                generation_time_ms=int((time.time() - start_time) * 1000),
                llm_provider=llm_provider.value if llm_provider else "auto",
                coverage_summary=coverage_analysis,
                test_type_distribution=coverage_analysis["test_type_distribution"],
                priority_distribution=coverage_analysis["priority_distribution"],
                warnings=coverage_analysis.get("gaps", []),
                suggestions=coverage_analysis.get("recommendations", []),
            )

            self.logger.info(
                f"Generated {len(test_cases)} test cases in "
                f"{response.generation_time_ms}ms"
            )

            return response

        except Exception as e:
            self.logger.error(f"Test case generation failed: {e}")
            return TestCaseResponse(
                success=False,
                test_cases=[],
                count=0,
                generation_time_ms=int((time.time() - start_time) * 1000),
                llm_provider=llm_provider.value if llm_provider else "auto",
                error=str(e),
                error_details={"type": type(e).__name__, "details": str(e)},
            )

    async def _gather_context(self, request: TestCaseRequest) -> Dict[str, Any]:
        """
        Gather context from various sources.

        Args:
            request: Test case request

        Returns:
            Context dictionary
        """
        context = {}

        try:
            # Get domain context if not provided
            if not request.domain_context and self.domain_client:
                try:
                    await self.domain_client.connect()
                    domain_context = await self.domain_client.get_domain_context(
                        entity_type=request.entity_type,
                        scenario=request.workflow,
                    )
                    context["domain_context"] = domain_context

                    # Get entity details
                    entity = await self.domain_client.get_entity(request.entity_type)
                    context["entity_details"] = entity

                    # Get workflow if specified
                    if request.workflow:
                        workflow = await self.domain_client.get_workflow(request.workflow)
                        context["workflow_steps"] = workflow.get("steps", [])

                    # Get edge cases
                    edge_cases = await self.domain_client.get_edge_cases(
                        entity_type=request.entity_type
                    )
                    context["edge_cases"] = [ec.get("description") for ec in edge_cases]

                except Exception as e:
                    self.logger.warning(f"Failed to get domain context: {e}")

            # Find similar test cases
            similar_tests = await self.knowledge_retriever.find_similar_test_cases(
                context=request.requirement,
                entity_type=request.entity_type,
                test_type=request.test_types[0] if request.test_types else None,
                limit=3,
            )
            if similar_tests:
                context["similar_tests"] = similar_tests

            # Get test patterns
            test_patterns = await self.knowledge_retriever.get_test_patterns(
                requirement=request.requirement,
                domain=request.entity_type,
                limit=2,
            )
            if test_patterns:
                context["test_patterns"] = test_patterns

            # Get coverage strategy
            coverage_strategy = await self.knowledge_retriever.get_coverage_strategy(
                requirement_type="user_story",
                complexity=request.detail_level,
            )
            context["coverage_strategy"] = coverage_strategy

            # Suggest edge cases
            if request.include_edge_cases:
                suggested_edge_cases = await self.knowledge_retriever.suggest_edge_cases(
                    entity_type=request.entity_type,
                    context=request.requirement,
                    limit=5,
                )
                context["suggested_edge_cases"] = suggested_edge_cases

        except Exception as e:
            self.logger.error(f"Failed to gather context: {e}")

        return context

    async def _generate_with_llm(
        self,
        prompt: str,
        provider: Optional[LLMProviderType] = None,
    ) -> str:
        """
        Generate response using LLM.

        Args:
            prompt: Generation prompt
            provider: Optional LLM provider

        Returns:
            LLM response string
        """
        messages = [
            Message(
                role="system",
                content="You are an expert QA engineer. Generate comprehensive test cases in JSON format.",
            ),
            Message(role="user", content=prompt),
        ]

        config = GenerationConfig(
            max_tokens=4000,
            temperature=0.7,
        )

        response = await self.llm_router.generate(
            messages=messages,
            provider=provider,
            config=config,
        )

        return response.content

    async def _enrich_test_cases(
        self,
        test_cases: List[TestCase],
        request: TestCaseRequest,
        context: Dict[str, Any],
    ) -> List[TestCase]:
        """
        Enrich test cases with additional data.

        Args:
            test_cases: Parsed test cases
            request: Original request
            context: Gathered context

        Returns:
            Enriched test cases
        """
        for tc in test_cases:
            # Add domain context
            if context.get("domain_context"):
                tc.domain_context = context["domain_context"]

            # Add metadata
            if request.domain_context and "requirements" in request.domain_context:
                tc.metadata.related_requirements = request.domain_context["requirements"]

            # Generate test data if needed (skip if agent was previously unavailable)
            if tc.test_data is None and self.test_data_client and self._test_data_agent_available is not False:
                try:
                    await self.test_data_client.connect()
                    self._test_data_agent_available = True
                    test_data_response = await self.test_data_client.generate_data(
                        entity=request.entity_type,
                        count=1,
                        context=f"Test case: {tc.title}",
                    )
                    if test_data_response.get("success") and test_data_response.get("data"):
                        tc.test_data = test_data_response["data"][0]
                except Exception as e:
                    self._test_data_agent_available = False
                    self.logger.info(f"Test Data Agent not available, skipping enrichment: {e}")

        return test_cases

    async def _learn_from_generation(
        self,
        test_cases: List[TestCase],
        request: TestCaseRequest,
    ) -> None:
        """
        Learn from generated test cases.

        Args:
            test_cases: Generated test cases
            request: Original request
        """
        try:
            for tc in test_cases:
                # Store in knowledge base
                await self.knowledge_retriever.learn_from_test_case(
                    test_case=tc.to_dict(),
                    feedback={
                        "generation_request": request.dict(),
                        "auto_generated": True,
                    },
                )
        except Exception as e:
            self.logger.error(f"Failed to learn from generation: {e}")

    async def refine(
        self,
        test_cases: List[TestCase],
        feedback: Dict[str, Any],
        llm_provider: Optional[LLMProviderType] = None,
    ) -> TestCaseResponse:
        """
        Refine existing test cases based on feedback.

        Args:
            test_cases: Existing test cases
            feedback: Refinement feedback
            llm_provider: Optional LLM provider

        Returns:
            Refined test cases response
        """
        start_time = time.time()

        try:
            # Build refinement prompt
            prompt = self.prompt_builder.build_refinement_prompt(
                [tc.to_dict() for tc in test_cases],
                feedback,
            )

            # Generate with LLM
            llm_response = await self._generate_with_llm(prompt, llm_provider)

            # Parse refined test cases
            refined_cases = self.parser.parse(llm_response, "json")

            # Build response
            response = TestCaseResponse(
                success=True,
                test_cases=refined_cases,
                count=len(refined_cases),
                generation_time_ms=int((time.time() - start_time) * 1000),
                llm_provider=llm_provider.value if llm_provider else "auto",
            )

            return response

        except Exception as e:
            self.logger.error(f"Test case refinement failed: {e}")
            return TestCaseResponse(
                success=False,
                test_cases=test_cases,  # Return original
                count=len(test_cases),
                generation_time_ms=int((time.time() - start_time) * 1000),
                llm_provider=llm_provider.value if llm_provider else "auto",
                error=str(e),
            )

    async def fill_gaps(
        self,
        requirements: List[str],
        existing_tests: List[TestCase],
        llm_provider: Optional[LLMProviderType] = None,
    ) -> TestCaseResponse:
        """
        Generate test cases to fill coverage gaps.

        Args:
            requirements: List of requirements
            existing_tests: Existing test cases
            llm_provider: Optional LLM provider

        Returns:
            New test cases to fill gaps
        """
        start_time = time.time()

        try:
            # Analyze gaps
            gap_analysis = await self.knowledge_retriever.analyze_test_gaps(
                requirements,
                [tc.to_dict() for tc in existing_tests],
            )

            if not gap_analysis["uncovered_requirements"]:
                return TestCaseResponse(
                    success=True,
                    test_cases=[],
                    count=0,
                    generation_time_ms=int((time.time() - start_time) * 1000),
                    llm_provider="none",
                    warnings=["No coverage gaps found"],
                )

            # Build gap-filling prompt
            prompt = self.prompt_builder.build_coverage_prompt(
                requirements,
                [tc.to_dict() for tc in existing_tests],
                gap_analysis["uncovered_requirements"],
            )

            # Generate with LLM
            llm_response = await self._generate_with_llm(prompt, llm_provider)

            # Parse test cases
            new_cases = self.parser.parse(llm_response, "json")

            # Build response
            response = TestCaseResponse(
                success=True,
                test_cases=new_cases,
                count=len(new_cases),
                generation_time_ms=int((time.time() - start_time) * 1000),
                llm_provider=llm_provider.value if llm_provider else "auto",
                coverage_summary=gap_analysis,
            )

            return response

        except Exception as e:
            self.logger.error(f"Gap filling failed: {e}")
            return TestCaseResponse(
                success=False,
                test_cases=[],
                count=0,
                generation_time_ms=int((time.time() - start_time) * 1000),
                llm_provider=llm_provider.value if llm_provider else "auto",
                error=str(e),
            )

    def format_test_cases(
        self,
        test_cases: List[TestCase],
        output_format: str = "json",
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Format test cases for output.

        Args:
            test_cases: Test cases to format
            output_format: Output format
            options: Formatting options

        Returns:
            Formatted string
        """
        return self.formatter.format(test_cases, output_format, options)


# Singleton instance
_engine_instance: Optional[GenerationEngine] = None


def get_generation_engine() -> GenerationEngine:
    """
    Get singleton generation engine instance.

    Returns:
        GenerationEngine instance
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = GenerationEngine()
    return _engine_instance


__all__ = ["GenerationEngine", "get_generation_engine"]