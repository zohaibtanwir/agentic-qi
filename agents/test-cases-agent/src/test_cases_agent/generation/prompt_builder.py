"""Prompt builder for test case generation."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template

from test_cases_agent.models import TestCaseRequest
from test_cases_agent.utils.logging import get_logger


class PromptBuilder:
    """
    Build prompts for LLM test case generation.

    Uses Jinja2 templates for flexible prompt construction.
    """

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize prompt builder.

        Args:
            template_dir: Optional custom template directory
        """
        self.logger = get_logger(__name__)

        # Set template directory
        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            # Use default templates directory
            self.template_dir = Path(__file__).parent / "templates"

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Load default template
        self.default_template = self._load_template("base.j2")

    def build(
        self,
        request: TestCaseRequest,
        context: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
    ) -> str:
        """
        Build prompt from request.

        Args:
            request: Test case generation request
            context: Additional context (domain info, similar tests, etc.)
            template_name: Optional custom template name

        Returns:
            Generated prompt string
        """
        # Prepare template variables
        variables = self._prepare_variables(request, context)

        # Select template
        if template_name:
            template = self._load_template(template_name)
        else:
            template = self._select_template(request)

        # Render template
        try:
            prompt = template.render(**variables)
            self.logger.debug(f"Generated prompt with {len(prompt)} characters")
            return prompt
        except Exception as e:
            self.logger.error(f"Failed to render template: {e}")
            # Fallback to simple prompt
            return self._build_fallback_prompt(request)

    def _prepare_variables(
        self,
        request: TestCaseRequest,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Prepare template variables.

        Args:
            request: Test case request
            context: Additional context

        Returns:
            Template variables dictionary
        """
        variables = {
            # Request fields
            "requirement": request.requirement,
            "entity_type": request.entity_type,
            "workflow": request.workflow,
            "test_types": request.test_types or ["functional", "edge_case"],
            "priority_focus": request.priority_focus or "medium",
            "count": request.count,
            "include_edge_cases": request.include_edge_cases,
            "include_negative_tests": request.include_negative_tests,
            "domain_context": request.domain_context,
            "existing_tests": request.existing_tests,
            "detail_level": request.detail_level,
            "language": request.language,
            "format_style": request.format_style,
        }

        # Add context if provided
        if context:
            variables.update({
                "similar_tests": context.get("similar_tests", []),
                "test_patterns": context.get("test_patterns", []),
                "coverage_strategy": context.get("coverage_strategy", {}),
                "edge_cases": context.get("edge_cases", []),
                "business_rules": context.get("business_rules", []),
                "entity_details": context.get("entity_details", {}),
                "workflow_steps": context.get("workflow_steps", []),
            })

        return variables

    def _select_template(self, request: TestCaseRequest) -> Template:
        """
        Select appropriate template based on request.

        Args:
            request: Test case request

        Returns:
            Selected template
        """
        # Check for format-specific templates
        if request.format_style == "bdd":
            template = self._try_load_template("bdd.j2")
            if template:
                return template

        # Check for detail-level templates
        if request.detail_level == "high":
            template = self._try_load_template("detailed.j2")
            if template:
                return template
        elif request.detail_level == "low":
            template = self._try_load_template("minimal.j2")
            if template:
                return template

        # Use default template
        return self.default_template

    def _load_template(self, template_name: str) -> Template:
        """
        Load template by name.

        Args:
            template_name: Template file name

        Returns:
            Loaded template

        Raises:
            Exception if template not found
        """
        try:
            return self.env.get_template(template_name)
        except Exception as e:
            self.logger.error(f"Failed to load template {template_name}: {e}")
            raise

    def _try_load_template(self, template_name: str) -> Optional[Template]:
        """
        Try to load template, return None if not found.

        Args:
            template_name: Template file name

        Returns:
            Template or None
        """
        try:
            return self.env.get_template(template_name)
        except:
            return None

    def _build_fallback_prompt(self, request: TestCaseRequest) -> str:
        """
        Build simple fallback prompt.

        Args:
            request: Test case request

        Returns:
            Fallback prompt string
        """
        prompt = f"""Generate {request.count} test cases for the following requirement:

Requirement: {request.requirement}
Entity Type: {request.entity_type}

Please include:
- Clear test steps with expected results
- Test data where applicable
- Both positive and negative test cases if requested

Format the output as a JSON array of test cases."""

        return prompt

    def build_refinement_prompt(
        self,
        test_cases: List[Dict[str, Any]],
        feedback: Dict[str, Any],
    ) -> str:
        """
        Build prompt for refining test cases.

        Args:
            test_cases: Existing test cases
            feedback: Feedback on what to improve

        Returns:
            Refinement prompt
        """
        template = self._try_load_template("refinement.j2")

        if not template:
            # Use inline template
            template_str = """Review and improve the following test cases based on the feedback:

## Current Test Cases
{{ test_cases | tojson(indent=2) }}

## Feedback
{% for key, value in feedback.items() %}
- {{ key }}: {{ value }}
{% endfor %}

Please provide improved versions of the test cases addressing the feedback."""

            template = self.env.from_string(template_str)

        return template.render(test_cases=test_cases, feedback=feedback)

    def build_coverage_prompt(
        self,
        requirements: List[str],
        existing_tests: List[Dict[str, Any]],
        gaps: List[str],
    ) -> str:
        """
        Build prompt for filling coverage gaps.

        Args:
            requirements: List of requirements
            existing_tests: Existing test cases
            gaps: Identified coverage gaps

        Returns:
            Coverage gap prompt
        """
        template = self._try_load_template("coverage_gaps.j2")

        if not template:
            # Use inline template
            template_str = """Generate test cases to fill the following coverage gaps:

## Requirements
{% for req in requirements %}
- {{ req }}
{% endfor %}

## Coverage Gaps
{% for gap in gaps %}
- {{ gap }}
{% endfor %}

## Existing Test Summary
We have {{ existing_tests | length }} existing test cases covering:
{% for test in existing_tests[:5] %}
- {{ test.title }} ({{ test.test_type }}, {{ test.priority }})
{% endfor %}
{% if existing_tests | length > 5 %}
... and {{ existing_tests | length - 5 }} more
{% endif %}

Generate test cases specifically to address the identified gaps."""

            template = self.env.from_string(template_str)

        return template.render(
            requirements=requirements,
            existing_tests=existing_tests,
            gaps=gaps,
        )

    def build_edge_case_prompt(
        self,
        entity_type: str,
        context: str,
        suggested_cases: List[str],
    ) -> str:
        """
        Build prompt for edge case generation.

        Args:
            entity_type: Entity type
            context: Context or scenario
            suggested_cases: Suggested edge cases

        Returns:
            Edge case prompt
        """
        template = self._try_load_template("edge_cases.j2")

        if not template:
            # Use inline template
            template_str = """Generate comprehensive edge case test scenarios for:

Entity: {{ entity_type }}
Context: {{ context }}

## Suggested Edge Cases to Consider
{% for case in suggested_cases %}
- {{ case }}
{% endfor %}

Generate test cases that:
1. Test boundary conditions
2. Handle invalid/unexpected inputs
3. Test concurrent operations
4. Verify error handling
5. Test resource limits

Format as JSON array of test cases with detailed steps."""

            template = self.env.from_string(template_str)

        return template.render(
            entity_type=entity_type,
            context=context,
            suggested_cases=suggested_cases,
        )


__all__ = ["PromptBuilder"]