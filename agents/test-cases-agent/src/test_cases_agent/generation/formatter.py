"""Formatter for test cases into various output formats."""

import csv
import io
import json
from typing import Any, Dict, List, Optional

import yaml

from test_cases_agent.models import TestCase
from test_cases_agent.utils.logging import get_logger


class TestCaseFormatter:
    """
    Format test cases into various output formats.

    Supported formats:
    - JSON
    - YAML
    - CSV
    - Markdown
    - HTML
    - Gherkin (BDD)
    - XML (JUnit/TestNG compatible)
    """

    def __init__(self):
        """Initialize formatter."""
        self.logger = get_logger(__name__)

    def format(
        self,
        test_cases: List[TestCase],
        output_format: str = "json",
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Format test cases into specified format.

        Args:
            test_cases: List of test cases to format
            output_format: Output format (json, yaml, csv, markdown, html, gherkin, xml)
            options: Optional formatting options

        Returns:
            Formatted string
        """
        options = options or {}

        formatters = {
            "json": self._format_json,
            "yaml": self._format_yaml,
            "csv": self._format_csv,
            "markdown": self._format_markdown,
            "html": self._format_html,
            "gherkin": self._format_gherkin,
            "xml": self._format_xml,
        }

        formatter = formatters.get(output_format.lower())
        if not formatter:
            self.logger.warning(f"Unknown format: {output_format}, using JSON")
            formatter = self._format_json

        try:
            return formatter(test_cases, options)
        except Exception as e:
            self.logger.error(f"Failed to format test cases: {e}")
            # Fallback to JSON
            return self._format_json(test_cases, {})

    def _format_json(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as JSON."""
        indent = options.get("indent", 2)
        include_metadata = options.get("include_metadata", True)

        data = []
        for tc in test_cases:
            tc_dict = tc.to_dict()
            if not include_metadata:
                tc_dict.pop("metadata", None)
            data.append(tc_dict)

        return json.dumps(data, indent=indent, ensure_ascii=False)

    def _format_yaml(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as YAML."""
        include_metadata = options.get("include_metadata", True)

        data = []
        for tc in test_cases:
            tc_dict = tc.to_dict()
            if not include_metadata:
                tc_dict.pop("metadata", None)
            data.append(tc_dict)

        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def _format_csv(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as CSV."""
        output = io.StringIO()

        # Define CSV columns
        fieldnames = [
            "ID", "Title", "Description", "Type", "Priority",
            "Preconditions", "Steps", "Expected Results", "Tags"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for tc in test_cases:
            # Format steps as numbered list
            steps_text = "\n".join(
                f"{step.step_number}. {step.action} -> {step.expected_result}"
                for step in tc.steps
            )

            # Format tags
            tags = ", ".join(tc.metadata.tags) if tc.metadata else ""

            writer.writerow({
                "ID": tc.id,
                "Title": tc.title,
                "Description": tc.description,
                "Type": tc.test_type,
                "Priority": tc.priority,
                "Preconditions": tc.preconditions or "",
                "Steps": steps_text,
                "Expected Results": tc.expected_results or "",
                "Tags": tags,
            })

        return output.getvalue()

    def _format_markdown(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as Markdown."""
        include_toc = options.get("include_toc", True)
        include_metadata = options.get("include_metadata", False)

        output = []

        # Add title
        output.append("# Test Cases\n")

        # Add table of contents
        if include_toc and len(test_cases) > 1:
            output.append("## Table of Contents\n")
            for i, tc in enumerate(test_cases, 1):
                output.append(f"{i}. [{tc.title}](#{tc.id.lower()})")
            output.append("")

        # Format each test case
        for tc in test_cases:
            output.append(f"## {tc.title} {{#{tc.id.lower()}}}\n")

            output.append(f"**ID:** {tc.id}")
            output.append(f"**Type:** {tc.test_type}")
            output.append(f"**Priority:** {tc.priority}\n")

            output.append(f"**Description:**")
            output.append(f"{tc.description}\n")

            if tc.preconditions:
                output.append(f"**Preconditions:**")
                output.append(f"{tc.preconditions}\n")

            output.append("**Test Steps:**")
            for step in tc.steps:
                output.append(f"{step.step_number}. **Action:** {step.action}")
                output.append(f"   **Expected:** {step.expected_result}")
                if step.test_data:
                    output.append(f"   **Data:** `{json.dumps(step.test_data)}`")
            output.append("")

            if tc.expected_results:
                output.append(f"**Expected Results:**")
                output.append(f"{tc.expected_results}\n")

            if tc.postconditions:
                output.append(f"**Postconditions:**")
                output.append(f"{tc.postconditions}\n")

            if include_metadata and tc.metadata:
                output.append("**Metadata:**")
                if tc.metadata.tags:
                    output.append(f"- Tags: {', '.join(tc.metadata.tags)}")
                if tc.metadata.categories:
                    output.append(f"- Categories: {', '.join(tc.metadata.categories)}")
                if tc.metadata.execution_time_estimate:
                    output.append(f"- Est. Time: {tc.metadata.execution_time_estimate} min")
                output.append("")

            output.append("---\n")

        return "\n".join(output)

    def _format_html(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as HTML."""
        include_styles = options.get("include_styles", True)

        html = []

        # Start HTML document
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("<meta charset='UTF-8'>")
        html.append("<title>Test Cases</title>")

        if include_styles:
            html.append("<style>")
            html.append("body { font-family: Arial, sans-serif; margin: 20px; }")
            html.append(".test-case { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; }")
            html.append(".test-header { background: #f5f5f5; padding: 10px; margin: -15px -15px 15px; }")
            html.append(".test-id { color: #666; font-size: 0.9em; }")
            html.append(".priority-high { color: #d9534f; }")
            html.append(".priority-medium { color: #f0ad4e; }")
            html.append(".priority-low { color: #5bc0de; }")
            html.append(".test-steps { margin-left: 20px; }")
            html.append(".step { margin: 10px 0; }")
            html.append(".step-action { font-weight: bold; }")
            html.append(".step-expected { color: #5cb85c; }")
            html.append("</style>")

        html.append("</head>")
        html.append("<body>")
        html.append("<h1>Test Cases</h1>")

        # Format each test case
        for tc in test_cases:
            html.append(f"<div class='test-case'>")
            html.append(f"<div class='test-header'>")
            html.append(f"<h2>{tc.title}</h2>")
            html.append(f"<span class='test-id'>ID: {tc.id}</span> | ")
            html.append(f"<span>Type: {tc.test_type}</span> | ")
            html.append(f"<span class='priority-{tc.priority}'>Priority: {tc.priority}</span>")
            html.append(f"</div>")

            html.append(f"<p><strong>Description:</strong> {tc.description}</p>")

            if tc.preconditions:
                html.append(f"<p><strong>Preconditions:</strong> {tc.preconditions}</p>")

            html.append("<div class='test-steps'>")
            html.append("<h3>Test Steps:</h3>")
            html.append("<ol>")
            for step in tc.steps:
                html.append("<li class='step'>")
                html.append(f"<div class='step-action'>Action: {step.action}</div>")
                html.append(f"<div class='step-expected'>Expected: {step.expected_result}</div>")
                html.append("</li>")
            html.append("</ol>")
            html.append("</div>")

            if tc.expected_results:
                html.append(f"<p><strong>Expected Results:</strong> {tc.expected_results}</p>")

            html.append("</div>")

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _format_gherkin(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as Gherkin (BDD format)."""
        output = []

        # Add feature header
        feature_name = options.get("feature_name", "Test Suite")
        output.append(f"Feature: {feature_name}")
        output.append("  Test cases for the application\n")

        for tc in test_cases:
            output.append(f"  @{tc.id}")
            if tc.metadata and tc.metadata.tags:
                for tag in tc.metadata.tags:
                    output.append(f"  @{tag}")

            output.append(f"  Scenario: {tc.title}")
            output.append(f"    # {tc.description}")

            if tc.preconditions:
                output.append(f"    Given {tc.preconditions}")

            for i, step in enumerate(tc.steps):
                if i == 0 and not tc.preconditions:
                    keyword = "Given"
                elif i == len(tc.steps) - 1:
                    keyword = "Then"
                else:
                    keyword = "When" if i == 1 else "And"

                output.append(f"    {keyword} {step.action}")

                # Add expected result as Then/And
                if step.expected_result and step.expected_result != "Step completes successfully":
                    output.append(f"    Then {step.expected_result}")

            output.append("")

        return "\n".join(output)

    def _format_xml(self, test_cases: List[TestCase], options: Dict[str, Any]) -> str:
        """Format as XML (JUnit/TestNG compatible)."""
        import xml.etree.ElementTree as ET

        # Create root element
        root = ET.Element("testsuite")
        root.set("name", options.get("suite_name", "Test Suite"))
        root.set("tests", str(len(test_cases)))

        for tc in test_cases:
            # Create test case element
            testcase = ET.SubElement(root, "testcase")
            testcase.set("id", tc.id)
            testcase.set("name", tc.title)
            testcase.set("classname", tc.test_type)

            # Add description as property
            properties = ET.SubElement(testcase, "properties")

            desc_prop = ET.SubElement(properties, "property")
            desc_prop.set("name", "description")
            desc_prop.set("value", tc.description)

            priority_prop = ET.SubElement(properties, "property")
            priority_prop.set("name", "priority")
            priority_prop.set("value", tc.priority)

            # Add steps as system-out
            system_out = ET.SubElement(testcase, "system-out")
            steps_text = []

            if tc.preconditions:
                steps_text.append(f"Preconditions: {tc.preconditions}")

            for step in tc.steps:
                steps_text.append(f"Step {step.step_number}: {step.action}")
                steps_text.append(f"  Expected: {step.expected_result}")

            if tc.expected_results:
                steps_text.append(f"Expected Results: {tc.expected_results}")

            system_out.text = "\n".join(steps_text)

        # Convert to string
        return ET.tostring(root, encoding="unicode", method="xml")


__all__ = ["TestCaseFormatter"]