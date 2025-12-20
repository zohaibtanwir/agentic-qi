"""Coverage analyzer for test case generation."""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from test_cases_agent.models import Priority, TestCase, TestType
from test_cases_agent.utils.logging import get_logger


class CoverageAnalyzer:
    """
    Analyze test coverage and identify gaps.

    Provides insights on:
    - Requirement coverage
    - Test type distribution
    - Priority distribution
    - Edge case coverage
    - Missing scenarios
    """

    def __init__(self):
        """Initialize coverage analyzer."""
        self.logger = get_logger(__name__)

    def analyze(
        self,
        test_cases: List[TestCase],
        requirements: Optional[List[str]] = None,
        target_coverage: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze test coverage.

        Args:
            test_cases: List of test cases to analyze
            requirements: Optional list of requirements to check
            target_coverage: Optional target coverage configuration

        Returns:
            Coverage analysis results
        """
        analysis = {
            "total_tests": len(test_cases),
            "coverage_score": 0.0,
            "test_type_distribution": self._analyze_test_types(test_cases),
            "priority_distribution": self._analyze_priorities(test_cases),
            "requirement_coverage": {},
            "edge_case_coverage": 0.0,
            "gaps": [],
            "recommendations": [],
            "metrics": {},
        }

        # Analyze requirement coverage if provided
        if requirements:
            analysis["requirement_coverage"] = self._analyze_requirements(
                test_cases, requirements
            )

        # Analyze edge case coverage
        analysis["edge_case_coverage"] = self._analyze_edge_cases(test_cases)

        # Compare with target coverage if provided
        if target_coverage:
            analysis["gaps"] = self._identify_gaps(test_cases, target_coverage)

        # Calculate overall coverage score
        analysis["coverage_score"] = self._calculate_coverage_score(analysis)

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        # Calculate additional metrics
        analysis["metrics"] = self._calculate_metrics(test_cases)

        return analysis

    def _analyze_test_types(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """
        Analyze distribution of test types.

        Args:
            test_cases: List of test cases

        Returns:
            Test type distribution
        """
        distribution = defaultdict(int)

        for tc in test_cases:
            distribution[tc.test_type] += 1

        return dict(distribution)

    def _analyze_priorities(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """
        Analyze distribution of priorities.

        Args:
            test_cases: List of test cases

        Returns:
            Priority distribution
        """
        distribution = defaultdict(int)

        for tc in test_cases:
            distribution[tc.priority] += 1

        return dict(distribution)

    def _analyze_requirements(
        self,
        test_cases: List[TestCase],
        requirements: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze requirement coverage.

        Args:
            test_cases: List of test cases
            requirements: List of requirements

        Returns:
            Requirement coverage analysis
        """
        coverage = {
            "total_requirements": len(requirements),
            "covered_requirements": 0,
            "uncovered_requirements": [],
            "coverage_percentage": 0.0,
            "requirement_test_map": {},
        }

        covered_reqs = set()
        req_test_map = defaultdict(list)

        for tc in test_cases:
            # Check metadata for related requirements
            if tc.metadata and tc.metadata.related_requirements:
                for req in tc.metadata.related_requirements:
                    if req in requirements:
                        covered_reqs.add(req)
                        req_test_map[req].append(tc.id)

            # Also check title and description for requirement mentions
            for req in requirements:
                if (
                    req.lower() in tc.title.lower()
                    or req.lower() in tc.description.lower()
                ):
                    covered_reqs.add(req)
                    req_test_map[req].append(tc.id)

        coverage["covered_requirements"] = len(covered_reqs)
        coverage["uncovered_requirements"] = [
            req for req in requirements if req not in covered_reqs
        ]
        coverage["coverage_percentage"] = (
            (len(covered_reqs) / len(requirements)) * 100 if requirements else 0
        )
        coverage["requirement_test_map"] = dict(req_test_map)

        return coverage

    def _analyze_edge_cases(self, test_cases: List[TestCase]) -> float:
        """
        Analyze edge case coverage.

        Args:
            test_cases: List of test cases

        Returns:
            Edge case coverage percentage
        """
        if not test_cases:
            return 0.0

        edge_case_count = sum(
            1
            for tc in test_cases
            if tc.test_type in [TestType.EDGE_CASE, TestType.NEGATIVE]
        )

        return (edge_case_count / len(test_cases)) * 100

    def _identify_gaps(
        self,
        test_cases: List[TestCase],
        target_coverage: Dict[str, Any],
    ) -> List[str]:
        """
        Identify coverage gaps.

        Args:
            test_cases: List of test cases
            target_coverage: Target coverage configuration

        Returns:
            List of identified gaps
        """
        gaps = []

        # Check test type coverage
        if "test_types" in target_coverage:
            current_types = {tc.test_type for tc in test_cases}
            expected_types = set(target_coverage["test_types"])
            missing_types = expected_types - current_types

            for test_type in missing_types:
                gaps.append(f"Missing {test_type} test cases")

        # Check minimum test count
        if "min_tests" in target_coverage:
            if len(test_cases) < target_coverage["min_tests"]:
                gaps.append(
                    f"Need {target_coverage['min_tests'] - len(test_cases)} more test cases"
                )

        # Check priority distribution
        if "priority_distribution" in target_coverage:
            priority_dist = self._analyze_priorities(test_cases)
            expected_dist = target_coverage["priority_distribution"]

            for priority, expected_pct in expected_dist.items():
                current_pct = (
                    (priority_dist.get(priority, 0) / len(test_cases)) * 100
                    if test_cases
                    else 0
                )

                if current_pct < expected_pct - 10:  # 10% tolerance
                    gaps.append(
                        f"Insufficient {priority} priority tests "
                        f"(current: {current_pct:.1f}%, expected: {expected_pct}%)"
                    )

        # Check edge case coverage
        if "edge_case_percentage" in target_coverage:
            edge_case_pct = self._analyze_edge_cases(test_cases)
            if edge_case_pct < target_coverage["edge_case_percentage"]:
                gaps.append(
                    f"Insufficient edge case coverage "
                    f"(current: {edge_case_pct:.1f}%, "
                    f"expected: {target_coverage['edge_case_percentage']}%)"
                )

        return gaps

    def _calculate_coverage_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall coverage score.

        Args:
            analysis: Coverage analysis data

        Returns:
            Coverage score (0-100)
        """
        scores = []

        # Test count score (max at 10+ tests)
        test_count_score = min(analysis["total_tests"] * 10, 100)
        scores.append(test_count_score)

        # Test type diversity score
        type_count = len(analysis["test_type_distribution"])
        type_score = min(type_count * 20, 100)
        scores.append(type_score)

        # Priority balance score
        priority_dist = analysis["priority_distribution"]
        if priority_dist:
            # Ideal distribution: high=30%, medium=50%, low=20%
            total = sum(priority_dist.values())
            high_pct = priority_dist.get(Priority.HIGH.value, 0) / total * 100
            medium_pct = priority_dist.get(Priority.MEDIUM.value, 0) / total * 100
            low_pct = priority_dist.get(Priority.LOW.value, 0) / total * 100

            balance_score = 100 - (
                abs(high_pct - 30) + abs(medium_pct - 50) + abs(low_pct - 20)
            )
            scores.append(max(balance_score, 0))

        # Requirement coverage score
        if analysis["requirement_coverage"]:
            scores.append(analysis["requirement_coverage"]["coverage_percentage"])

        # Edge case coverage score
        edge_score = min(analysis["edge_case_coverage"] * 5, 100)  # 20% is ideal
        scores.append(edge_score)

        # Return average score
        return sum(scores) / len(scores) if scores else 0.0

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate coverage improvement recommendations.

        Args:
            analysis: Coverage analysis data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check test count
        if analysis["total_tests"] < 5:
            recommendations.append("Add more test cases to improve coverage")

        # Check test type diversity
        type_dist = analysis["test_type_distribution"]
        if len(type_dist) < 3:
            recommendations.append("Add more test types (e.g., edge cases, negative tests)")

        if TestType.EDGE_CASE.value not in type_dist:
            recommendations.append("Add edge case tests to handle boundary conditions")

        if TestType.NEGATIVE.value not in type_dist:
            recommendations.append("Add negative tests to validate error handling")

        # Check priority balance
        priority_dist = analysis["priority_distribution"]
        if priority_dist:
            total = sum(priority_dist.values())
            high_pct = priority_dist.get(Priority.HIGH.value, 0) / total * 100

            if high_pct > 50:
                recommendations.append(
                    "Too many high priority tests - consider balancing priorities"
                )
            elif high_pct < 20:
                recommendations.append(
                    "Add more high priority tests for critical functionality"
                )

        # Check requirement coverage
        if analysis["requirement_coverage"]:
            req_coverage = analysis["requirement_coverage"]
            if req_coverage["coverage_percentage"] < 80:
                recommendations.append(
                    f"Improve requirement coverage - {len(req_coverage['uncovered_requirements'])} "
                    f"requirements not covered"
                )

        # Check edge case coverage
        if analysis["edge_case_coverage"] < 15:
            recommendations.append(
                "Increase edge case coverage to at least 15-20% of tests"
            )

        # Add gaps as recommendations
        for gap in analysis["gaps"]:
            recommendations.append(f"Gap: {gap}")

        return recommendations

    def _calculate_metrics(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        Calculate additional metrics.

        Args:
            test_cases: List of test cases

        Returns:
            Additional metrics
        """
        metrics = {
            "avg_steps_per_test": 0,
            "tests_with_preconditions": 0,
            "tests_with_postconditions": 0,
            "tests_with_test_data": 0,
            "complexity_score": 0.0,
            "unique_entities": set(),
        }

        if not test_cases:
            return metrics

        total_steps = 0
        precondition_count = 0
        postcondition_count = 0
        test_data_count = 0

        for tc in test_cases:
            total_steps += len(tc.steps)

            if tc.preconditions:
                precondition_count += 1

            if tc.postconditions:
                postcondition_count += 1

            if tc.test_data:
                test_data_count += 1

            # Extract entities from domain context
            if tc.domain_context and "entity_type" in tc.domain_context:
                metrics["unique_entities"].add(tc.domain_context["entity_type"])

        metrics["avg_steps_per_test"] = total_steps / len(test_cases)
        metrics["tests_with_preconditions"] = precondition_count
        metrics["tests_with_postconditions"] = postcondition_count
        metrics["tests_with_test_data"] = test_data_count

        # Calculate complexity score based on average steps and conditions
        metrics["complexity_score"] = min(
            (metrics["avg_steps_per_test"] * 10
            + (precondition_count / len(test_cases)) * 30
            + (test_data_count / len(test_cases)) * 20),
            100
        )

        # Convert set to list for JSON serialization
        metrics["unique_entities"] = list(metrics["unique_entities"])

        return metrics

    def compare_coverage(
        self,
        current: List[TestCase],
        previous: List[TestCase],
    ) -> Dict[str, Any]:
        """
        Compare coverage between two sets of test cases.

        Args:
            current: Current test cases
            previous: Previous test cases

        Returns:
            Comparison results
        """
        current_analysis = self.analyze(current)
        previous_analysis = self.analyze(previous)

        comparison = {
            "test_count_change": len(current) - len(previous),
            "coverage_score_change": (
                current_analysis["coverage_score"] - previous_analysis["coverage_score"]
            ),
            "new_test_types": [],
            "removed_test_types": [],
            "priority_changes": {},
            "improvement_areas": [],
            "regression_areas": [],
        }

        # Compare test types
        current_types = set(current_analysis["test_type_distribution"].keys())
        previous_types = set(previous_analysis["test_type_distribution"].keys())

        comparison["new_test_types"] = list(current_types - previous_types)
        comparison["removed_test_types"] = list(previous_types - current_types)

        # Compare priorities
        for priority in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            current_count = current_analysis["priority_distribution"].get(priority.value, 0)
            previous_count = previous_analysis["priority_distribution"].get(priority.value, 0)
            if current_count != previous_count:
                comparison["priority_changes"][priority.value] = current_count - previous_count

        # Identify improvements and regressions
        if comparison["coverage_score_change"] > 5:
            comparison["improvement_areas"].append("Overall coverage improved")

        if comparison["coverage_score_change"] < -5:
            comparison["regression_areas"].append("Overall coverage decreased")

        edge_case_change = (
            current_analysis["edge_case_coverage"] - previous_analysis["edge_case_coverage"]
        )

        if edge_case_change > 5:
            comparison["improvement_areas"].append("Edge case coverage improved")
        elif edge_case_change < -5:
            comparison["regression_areas"].append("Edge case coverage decreased")

        return comparison


__all__ = ["CoverageAnalyzer"]