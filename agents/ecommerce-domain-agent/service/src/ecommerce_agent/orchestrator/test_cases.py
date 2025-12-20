"""Test case generation orchestrator."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from ecommerce_agent.clients.test_case_generator import TestCaseGeneratorClient
from ecommerce_agent.domain.entities import get_entity
from ecommerce_agent.utils.logging import get_logger

logger = get_logger(__name__)

class TestCaseType(Enum):
    """Types of test cases."""
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    E2E = "e2e"
    REGRESSION = "regression"
    BOUNDARY = "boundary"
    NEGATIVE = "negative"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"

class TestCasePriority(Enum):
    """Test case priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TestCase:
    """Individual test case."""
    id: str
    name: str
    description: str
    type: TestCaseType
    priority: TestCasePriority
    preconditions: List[str]
    steps: List[Dict[str, str]]  # action, expected_result
    postconditions: List[str]
    test_data: Dict[str, Any]
    business_rules: List[str]
    expected_behavior: str
    edge_cases: List[str]
    automation_feasibility: bool
    estimated_duration: int  # minutes

@dataclass
class TestSuite:
    """Collection of test cases."""
    id: str
    name: str
    entity: str
    workflow: str
    test_cases: List[TestCase]
    total_cases: int
    coverage_percentage: float
    estimated_duration: int  # minutes
    business_context: Dict[str, Any]


class TestCaseOrchestrator:
    """Orchestrates test case generation with domain enrichment."""

    def __init__(self):
        self.client = TestCaseGeneratorClient()

    async def generate_test_cases(
        self,
        entity_name: str,
        workflow: Optional[str] = None,
        test_types: Optional[List[TestCaseType]] = None,
        generation_method: str = "llm",
        count: int = 10,
        include_edge_cases: bool = True,
        include_negative_tests: bool = True
    ) -> TestSuite:
        """
        Generate test cases for an entity or workflow.

        Args:
            entity_name: Name of the domain entity
            workflow: Specific workflow to test (e.g., "checkout", "return")
            test_types: Types of test cases to generate
            generation_method: Method to use (traditional, llm, rag, hybrid)
            count: Number of test cases to generate
            include_edge_cases: Include edge case scenarios
            include_negative_tests: Include negative test scenarios

        Returns:
            TestSuite with generated test cases
        """
        # Get entity definition for domain context
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found")

        # Default test types if not specified
        if not test_types:
            test_types = [
                TestCaseType.FUNCTIONAL,
                TestCaseType.INTEGRATION,
                TestCaseType.BOUNDARY
            ]

        # Build request with domain enrichment
        request = {
            "entity": entity_name,
            "workflow": workflow or f"{entity_name}_operations",
            "test_types": [t.value for t in test_types],
            "generation_method": generation_method,
            "count": count,
            "include_edge_cases": include_edge_cases,
            "include_negative_tests": include_negative_tests,
            "domain_context": {
                "entity_definition": {
                    "name": entity.name,
                    "description": entity.description,
                    "fields": [
                        {
                            "name": f.name,
                            "type": f.type,
                            "required": f.required,
                            "validations": f.validations
                        }
                        for f in entity.fields
                    ],
                    "relationships": [
                        {
                            "target": r.target,
                            "type": r.type,
                            "required": r.required
                        }
                        for r in entity.relationships
                    ],
                },
                "business_rules": entity.business_rules,
                "edge_cases": entity.edge_cases,
                "test_scenarios": entity.test_scenarios
            }
        }

        logger.info(
            "Generating test cases",
            entity=entity_name,
            workflow=workflow,
            test_types=[t.value for t in test_types],
            method=generation_method
        )

        try:
            # Call Test Case Generator agent
            result = await self.client.generate_test_cases(request)

            # Transform response to TestSuite
            test_suite = self._build_test_suite(result, entity_name, workflow)

            logger.info(
                "Test cases generated successfully",
                suite_id=test_suite.id,
                total_cases=test_suite.total_cases,
                coverage=test_suite.coverage_percentage
            )

            return test_suite

        except Exception as e:
            logger.error(
                "Failed to generate test cases",
                entity=entity_name,
                workflow=workflow,
                error=str(e)
            )
            raise

    def _build_test_suite(
        self,
        result: Dict[str, Any],
        entity_name: str,
        workflow: Optional[str]
    ) -> TestSuite:
        """Build TestSuite from Test Case Generator response."""
        test_cases = []

        for tc in result.get("test_cases", []):
            test_case = TestCase(
                id=tc.get("id"),
                name=tc.get("name"),
                description=tc.get("description"),
                type=TestCaseType(tc.get("type", "functional")),
                priority=TestCasePriority(tc.get("priority", "medium")),
                preconditions=tc.get("preconditions", []),
                steps=tc.get("steps", []),
                postconditions=tc.get("postconditions", []),
                test_data=tc.get("test_data", {}),
                business_rules=tc.get("business_rules", []),
                expected_behavior=tc.get("expected_behavior", ""),
                edge_cases=tc.get("edge_cases", []),
                automation_feasibility=tc.get("automation_feasibility", True),
                estimated_duration=tc.get("estimated_duration", 5)
            )
            test_cases.append(test_case)

        return TestSuite(
            id=result.get("suite_id"),
            name=result.get("suite_name", f"{entity_name} Test Suite"),
            entity=entity_name,
            workflow=workflow or f"{entity_name}_operations",
            test_cases=test_cases,
            total_cases=len(test_cases),
            coverage_percentage=result.get("coverage_percentage", 0.0),
            estimated_duration=sum(tc.estimated_duration for tc in test_cases),
            business_context=result.get("business_context", {})
        )

    async def analyze_test_coverage(
        self,
        entity_name: str,
        existing_tests: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze test coverage for an entity.

        Args:
            entity_name: Name of the entity
            existing_tests: List of existing test IDs

        Returns:
            Coverage analysis report
        """
        entity = get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entity '{entity_name}' not found")

        # Analyze what needs testing
        coverage_analysis = {
            "entity": entity_name,
            "total_fields": len(entity.fields),
            "total_relationships": len(entity.relationships),
            "total_business_rules": len(entity.business_rules),
            "total_edge_cases": len(entity.edge_cases),
            "coverage_gaps": [],
            "recommendations": []
        }

        # Identify coverage gaps
        if not existing_tests:
            coverage_analysis["coverage_gaps"].append("No existing tests found")
            coverage_analysis["recommendations"].append(
                "Generate comprehensive test suite covering all business rules"
            )

        # Add specific recommendations based on entity
        for rule in entity.business_rules:
            coverage_analysis["recommendations"].append(
                f"Test business rule: {rule}"
            )

        for edge_case in entity.edge_cases[:3]:  # Top 3 edge cases
            coverage_analysis["recommendations"].append(
                f"Test edge case: {edge_case}"
            )

        return coverage_analysis


def get_test_case_orchestrator() -> TestCaseOrchestrator:
    """Get test case orchestrator instance."""
    return TestCaseOrchestrator()