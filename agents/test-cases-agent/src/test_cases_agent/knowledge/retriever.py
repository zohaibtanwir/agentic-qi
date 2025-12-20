"""Knowledge retrieval and management for test case generation."""

from typing import Any, Dict, List, Optional, Tuple

from test_cases_agent.knowledge.weaviate_client import WeaviateClient, get_weaviate_client
from test_cases_agent.utils.logging import get_logger


class KnowledgeRetriever:
    """
    Manages knowledge retrieval and learning from past test cases.

    This class provides high-level methods for:
    - Finding similar test cases
    - Learning from successful patterns
    - Suggesting test strategies
    - Managing coverage patterns
    """

    def __init__(self, weaviate_client: Optional[WeaviateClient] = None):
        """
        Initialize knowledge retriever.

        Args:
            weaviate_client: Optional Weaviate client instance
        """
        self.weaviate = weaviate_client or get_weaviate_client()
        self.logger = get_logger(__name__)

    async def find_similar_test_cases(
        self,
        context: str,
        entity_type: Optional[str] = None,
        test_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find similar test cases based on context.

        Args:
            context: Context description or requirements
            entity_type: Optional entity type filter
            test_type: Optional test type filter
            limit: Maximum number of results

        Returns:
            List of similar test cases
        """
        try:
            # Build filters
            filters = {}
            if entity_type:
                filters["domain_context"] = entity_type
            if test_type:
                filters["test_type"] = test_type

            # Search for similar test cases
            test_cases = await self.weaviate.search_test_cases(
                query=context,
                limit=limit,
                filters=filters,
            )

            self.logger.info(
                f"Found {len(test_cases)} similar test cases for context: {context[:100]}..."
            )

            return test_cases

        except Exception as e:
            self.logger.error(f"Failed to find similar test cases: {e}")
            return []

    async def get_test_patterns(
        self,
        requirement: str,
        domain: Optional[str] = None,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get relevant test patterns for a requirement.

        Args:
            requirement: Requirement or user story
            domain: Optional domain context
            limit: Maximum patterns to return

        Returns:
            List of test patterns
        """
        try:
            # Search for relevant patterns
            patterns = await self.weaviate.search_patterns(
                query=f"{requirement} {domain or ''}",
                pattern_type="test",
                limit=limit,
            )

            self.logger.info(f"Found {len(patterns)} test patterns for requirement")

            # Sort by success rate
            patterns.sort(key=lambda x: x.get("success_rate", 0), reverse=True)

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to get test patterns: {e}")
            return []

    async def get_coverage_strategy(
        self,
        requirement_type: str,
        complexity: str = "medium",
    ) -> Dict[str, Any]:
        """
        Get coverage strategy for requirement type.

        Args:
            requirement_type: Type of requirement
            complexity: Complexity level (low, medium, high)

        Returns:
            Coverage strategy dictionary
        """
        try:
            # Search for coverage patterns
            patterns = await self.weaviate.search_patterns(
                query=f"{requirement_type} {complexity} coverage",
                pattern_type="coverage",
                limit=1,
            )

            if patterns:
                pattern = patterns[0]
                return {
                    "strategy": pattern.get("coverage_strategy", "comprehensive"),
                    "test_types": pattern.get("test_types_required", ["functional"]),
                    "min_tests": pattern.get("minimum_test_count", 3),
                    "priority_distribution": pattern.get("priority_distribution", {}),
                    "edge_cases": pattern.get("edge_cases", []),
                    "validation_rules": pattern.get("validation_rules", []),
                }
            else:
                # Return default strategy
                return self._get_default_coverage_strategy(complexity)

        except Exception as e:
            self.logger.error(f"Failed to get coverage strategy: {e}")
            return self._get_default_coverage_strategy(complexity)

    async def learn_from_test_case(
        self,
        test_case: Dict[str, Any],
        feedback: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Learn from a test case execution.

        Args:
            test_case: Test case that was executed
            feedback: Optional feedback about the test case

        Returns:
            True if learning was successful
        """
        try:
            # Enrich test case with feedback if provided
            if feedback:
                test_case["coverage_score"] = feedback.get("coverage_score", 0.8)
                test_case["complexity_score"] = feedback.get("complexity_score", 0.5)
                test_case["effectiveness"] = feedback.get("effectiveness", "high")

            # Store the test case
            case_id = await self.weaviate.store_test_case(test_case)

            self.logger.info(f"Learned from test case: {case_id}")

            # Update pattern usage if pattern was used
            if "pattern_id" in test_case:
                success = feedback.get("success", True) if feedback else True
                await self.weaviate.update_pattern_usage(
                    pattern_id=test_case["pattern_id"],
                    pattern_type="test",
                    success=success,
                )

            return True

        except Exception as e:
            self.logger.error(f"Failed to learn from test case: {e}")
            return False

    async def suggest_edge_cases(
        self,
        entity_type: str,
        context: str,
        limit: int = 5,
    ) -> List[str]:
        """
        Suggest edge cases based on historical data.

        Args:
            entity_type: Type of entity
            context: Context or scenario
            limit: Maximum suggestions

        Returns:
            List of edge case descriptions
        """
        try:
            # Search for test cases with similar context
            similar_cases = await self.find_similar_test_cases(
                context=context,
                entity_type=entity_type,
                limit=limit * 2,
            )

            # Extract unique edge cases
            edge_cases = set()
            for case in similar_cases:
                if "domain_context" in case:
                    domain_ctx = case["domain_context"]
                    if isinstance(domain_ctx, dict) and "edge_cases" in domain_ctx:
                        edge_cases.update(domain_ctx["edge_cases"])

            # Also add common edge cases for the entity type
            edge_cases.update(self._get_common_edge_cases(entity_type))

            # Return top edge cases
            return list(edge_cases)[:limit]

        except Exception as e:
            self.logger.error(f"Failed to suggest edge cases: {e}")
            return self._get_common_edge_cases(entity_type)[:limit]

    async def analyze_test_gaps(
        self,
        requirements: List[str],
        existing_tests: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze gaps in test coverage.

        Args:
            requirements: List of requirements
            existing_tests: List of existing test cases

        Returns:
            Gap analysis results
        """
        try:
            gaps = {
                "uncovered_requirements": [],
                "missing_test_types": [],
                "suggested_tests": [],
                "coverage_percentage": 0.0,
            }

            # Analyze which requirements are covered
            covered_reqs = set()
            test_types = set()

            for test in existing_tests:
                if "requirements" in test:
                    covered_reqs.update(test["requirements"])
                if "test_type" in test:
                    test_types.add(test["test_type"])

            # Find uncovered requirements
            for req in requirements:
                if req not in covered_reqs:
                    gaps["uncovered_requirements"].append(req)

            # Determine missing test types
            recommended_types = {"functional", "edge_case", "negative", "performance"}
            gaps["missing_test_types"] = list(recommended_types - test_types)

            # Calculate coverage
            if requirements:
                gaps["coverage_percentage"] = (
                    len(covered_reqs) / len(requirements)
                ) * 100

            # Suggest tests for gaps
            for req in gaps["uncovered_requirements"][:3]:  # Limit suggestions
                patterns = await self.get_test_patterns(req)
                if patterns:
                    gaps["suggested_tests"].append({
                        "requirement": req,
                        "pattern": patterns[0]["name"],
                        "template": patterns[0].get("template", {}),
                    })

            return gaps

        except Exception as e:
            self.logger.error(f"Failed to analyze test gaps: {e}")
            return {
                "uncovered_requirements": [],
                "missing_test_types": [],
                "suggested_tests": [],
                "coverage_percentage": 0.0,
            }

    def _get_default_coverage_strategy(self, complexity: str) -> Dict[str, Any]:
        """
        Get default coverage strategy based on complexity.

        Args:
            complexity: Complexity level

        Returns:
            Default coverage strategy
        """
        strategies = {
            "low": {
                "strategy": "basic",
                "test_types": ["functional"],
                "min_tests": 2,
                "priority_distribution": {"high": 50, "medium": 30, "low": 20},
                "edge_cases": ["empty_input", "null_values"],
                "validation_rules": ["required_fields", "data_types"],
            },
            "medium": {
                "strategy": "comprehensive",
                "test_types": ["functional", "negative", "edge_case"],
                "min_tests": 5,
                "priority_distribution": {"high": 40, "medium": 40, "low": 20},
                "edge_cases": ["empty_input", "null_values", "boundary_values", "special_chars"],
                "validation_rules": ["required_fields", "data_types", "business_rules"],
            },
            "high": {
                "strategy": "exhaustive",
                "test_types": ["functional", "negative", "edge_case", "performance", "security"],
                "min_tests": 10,
                "priority_distribution": {"high": 30, "medium": 50, "low": 20},
                "edge_cases": [
                    "empty_input", "null_values", "boundary_values",
                    "special_chars", "concurrent_access", "large_data"
                ],
                "validation_rules": [
                    "required_fields", "data_types", "business_rules",
                    "state_transitions", "security_constraints"
                ],
            },
        }

        return strategies.get(complexity, strategies["medium"])

    def _get_common_edge_cases(self, entity_type: str) -> List[str]:
        """
        Get common edge cases for entity type.

        Args:
            entity_type: Type of entity

        Returns:
            List of common edge cases
        """
        edge_cases = {
            "order": [
                "Empty cart checkout",
                "Order with zero quantity",
                "Order exceeding inventory",
                "Concurrent order placement",
                "Order with invalid payment",
            ],
            "customer": [
                "Duplicate email registration",
                "Invalid email format",
                "Missing required fields",
                "Special characters in name",
                "Concurrent profile updates",
            ],
            "product": [
                "Product with no price",
                "Product with negative stock",
                "Product with expired promotion",
                "Product with circular dependencies",
                "Product with missing images",
            ],
            "payment": [
                "Insufficient funds",
                "Expired payment method",
                "Currency mismatch",
                "Payment timeout",
                "Duplicate payment attempt",
            ],
        }

        # Return entity-specific or generic edge cases
        return edge_cases.get(entity_type, [
            "Null or empty input",
            "Boundary value conditions",
            "Duplicate entries",
            "Concurrent operations",
            "Invalid state transitions",
        ])


# Singleton instance
_retriever_instance: Optional[KnowledgeRetriever] = None


def get_knowledge_retriever() -> KnowledgeRetriever:
    """
    Get singleton knowledge retriever instance.

    Returns:
        KnowledgeRetriever instance
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever()
    return _retriever_instance


__all__ = ["KnowledgeRetriever", "get_knowledge_retriever"]