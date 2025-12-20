"""Parser for LLM responses into test case models."""

import json
import re
from typing import Any, Dict, List, Optional, Union

import yaml

from test_cases_agent.models import Priority, TestCase, TestStep, TestType
from test_cases_agent.utils.logging import get_logger


class TestCaseParser:
    """
    Parse LLM responses into structured test case models.

    Supports multiple formats:
    - JSON
    - YAML
    - Structured text
    - Markdown
    """

    def __init__(self):
        """Initialize parser."""
        self.logger = get_logger(__name__)

    def parse(self, response: str, format_hint: Optional[str] = None) -> List[TestCase]:
        """
        Parse LLM response into test cases.

        Args:
            response: LLM response string
            format_hint: Optional format hint (json, yaml, markdown, text)

        Returns:
            List of parsed test cases
        """
        try:
            # Clean response
            response = self._clean_response(response)

            # Try to detect format if not provided
            if not format_hint:
                format_hint = self._detect_format(response)

            self.logger.debug(f"Parsing response with format: {format_hint}")

            # Parse based on format
            if format_hint == "json":
                return self._parse_json(response)
            elif format_hint == "yaml":
                return self._parse_yaml(response)
            elif format_hint == "markdown":
                return self._parse_markdown(response)
            else:
                return self._parse_text(response)

        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            # Try fallback parsing
            return self._fallback_parse(response)

    def _clean_response(self, response: str) -> str:
        """
        Clean LLM response.

        Args:
            response: Raw response

        Returns:
            Cleaned response
        """
        # Remove code blocks if present
        if "```json" in response:
            match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                return match.group(1)
        elif "```yaml" in response or "```yml" in response:
            match = re.search(r"```(?:yaml|yml)\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                return match.group(1)
        elif "```" in response:
            # Generic code block
            match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                return match.group(1)

        return response.strip()

    def _detect_format(self, response: str) -> str:
        """
        Detect response format.

        Args:
            response: Response string

        Returns:
            Format type
        """
        # Check for JSON
        if response.startswith("[") or response.startswith("{"):
            try:
                json.loads(response)
                return "json"
            except:
                pass

        # Check for YAML
        if ":" in response and ("\n-" in response or "\n  " in response):
            try:
                yaml.safe_load(response)
                return "yaml"
            except:
                pass

        # Check for markdown patterns
        if "##" in response or "**Test Case" in response:
            return "markdown"

        # Default to text
        return "text"

    def _parse_json(self, response: str) -> List[TestCase]:
        """
        Parse JSON response.

        Args:
            response: JSON string

        Returns:
            List of test cases
        """
        try:
            data = json.loads(response)

            # Handle both single test case and list
            if isinstance(data, dict):
                data = [data]

            test_cases = []
            for item in data:
                test_case = self._dict_to_test_case(item)
                if test_case:
                    test_cases.append(test_case)

            return test_cases

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            raise

    def _parse_yaml(self, response: str) -> List[TestCase]:
        """
        Parse YAML response.

        Args:
            response: YAML string

        Returns:
            List of test cases
        """
        try:
            data = yaml.safe_load(response)

            # Handle both single test case and list
            if isinstance(data, dict):
                # Check if it's a wrapper with test_cases key
                if "test_cases" in data:
                    data = data["test_cases"]
                else:
                    data = [data]

            test_cases = []
            for item in data:
                test_case = self._dict_to_test_case(item)
                if test_case:
                    test_cases.append(test_case)

            return test_cases

        except yaml.YAMLError as e:
            self.logger.error(f"YAML parse error: {e}")
            raise

    def _parse_markdown(self, response: str) -> List[TestCase]:
        """
        Parse markdown formatted response.

        Args:
            response: Markdown string

        Returns:
            List of test cases
        """
        test_cases = []

        # Split by test case headers
        sections = re.split(r"(?:^|\n)(?:##|Test Case:?)\s*", response)

        for section in sections[1:]:  # Skip first empty section
            if not section.strip():
                continue

            test_case = self._parse_markdown_section(section)
            if test_case:
                test_cases.append(test_case)

        return test_cases

    def _parse_markdown_section(self, section: str) -> Optional[TestCase]:
        """
        Parse a markdown section into a test case.

        Args:
            section: Markdown section

        Returns:
            TestCase or None
        """
        try:
            lines = section.strip().split("\n")

            # Extract title (first line)
            title = lines[0].strip()

            # Initialize fields
            tc_data = {
                "title": title,
                "id": self._generate_id(title),
                "description": title,  # Use title as default description
                "test_type": TestType.FUNCTIONAL,
                "priority": Priority.MEDIUM,
                "steps": [],
            }

            current_field = None
            current_content = []

            for line in lines[1:]:
                line = line.strip()

                # Check for field headers
                if "**" in line and ":" in line:
                    # Extract field and value from same line (e.g., **Description**: Value)
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        field = parts[0].strip("*").strip().lower()
                        value = parts[1].strip()
                        if value:
                            self._set_field(tc_data, field, value)
                            current_field = None
                            current_content = []
                        else:
                            current_field = field
                            current_content = []
                elif line.startswith("**") and line.endswith("**"):
                    # Save previous field
                    if current_field and current_content:
                        self._set_field(tc_data, current_field, "\n".join(current_content))

                    # Start new field
                    current_field = line.strip("*").strip(":").lower()
                    current_content = []

                elif line.startswith("###"):
                    # Sub-header
                    current_field = line.strip("#").strip().lower()
                    current_content = []

                elif line:
                    current_content.append(line)

            # Save last field
            if current_field and current_content:
                self._set_field(tc_data, current_field, "\n".join(current_content))

            # Parse steps if present
            if "steps" in tc_data and isinstance(tc_data["steps"], str):
                tc_data["steps"] = self._parse_steps_text(tc_data["steps"])

            # Ensure we have at least one step
            if not tc_data["steps"]:
                tc_data["steps"] = [TestStep(
                    step_number=1,
                    action="Execute test",
                    expected_result="Test passes",
                )]

            return TestCase(**tc_data)

        except Exception as e:
            self.logger.error(f"Failed to parse markdown section: {e}")
            return None

    def _parse_text(self, response: str) -> List[TestCase]:
        """
        Parse plain text response.

        Args:
            response: Plain text string

        Returns:
            List of test cases
        """
        test_cases = []

        # Try to find test case boundaries
        sections = re.split(r"(?:Test Case|TC)\s*\d*:?\s*", response, flags=re.IGNORECASE)

        for section in sections[1:]:  # Skip first empty section
            if not section.strip():
                continue

            test_case = self._parse_text_section(section)
            if test_case:
                test_cases.append(test_case)

        # If no clear sections, treat whole response as one test case
        if not test_cases and response.strip():
            test_case = self._parse_text_section(response)
            if test_case:
                test_cases.append(test_case)

        return test_cases

    def _parse_text_section(self, section: str) -> Optional[TestCase]:
        """
        Parse a text section into a test case.

        Args:
            section: Text section

        Returns:
            TestCase or None
        """
        try:
            lines = [l.strip() for l in section.strip().split("\n") if l.strip()]

            if not lines:
                return None

            # Extract title (first non-empty line)
            title = lines[0]

            tc_data = {
                "id": self._generate_id(title),
                "title": title,
                "description": "",
                "test_type": TestType.FUNCTIONAL,
                "priority": Priority.MEDIUM,
                "steps": [],
            }

            # Parse remaining lines
            for i, line in enumerate(lines[1:], 1):
                lower_line = line.lower()

                # Look for field indicators
                if "description:" in lower_line:
                    tc_data["description"] = line.split(":", 1)[1].strip()
                elif "type:" in lower_line:
                    tc_data["test_type"] = self._parse_test_type(line.split(":", 1)[1].strip())
                elif "priority:" in lower_line:
                    tc_data["priority"] = self._parse_priority(line.split(":", 1)[1].strip())
                elif "precondition" in lower_line:
                    tc_data["preconditions"] = line.split(":", 1)[1].strip() if ":" in line else lines[i+1] if i+1 < len(lines) else ""
                elif "step" in lower_line or re.match(r"^\d+\.", line):
                    # Parse as step
                    step = self._parse_step_line(line)
                    if step:
                        # Set correct step number
                        step.step_number = len(tc_data["steps"]) + 1
                        tc_data["steps"].append(step)

            # Ensure we have a description
            if not tc_data["description"]:
                tc_data["description"] = f"Test case for {title}"

            # Ensure we have steps
            if not tc_data["steps"]:
                tc_data["steps"] = [TestStep(
                    step_number=1,
                    action=title,
                    expected_result="Test passes successfully",
                )]

            return TestCase(**tc_data)

        except Exception as e:
            self.logger.error(f"Failed to parse text section: {e}")
            return None

    def _dict_to_test_case(self, data: Dict[str, Any]) -> Optional[TestCase]:
        """
        Convert dictionary to TestCase.

        Args:
            data: Dictionary data

        Returns:
            TestCase or None
        """
        try:
            # Normalize field names
            normalized = {}

            for key, value in data.items():
                # Convert camelCase or snake_case to our expected names
                normalized_key = self._normalize_key(key)
                normalized[normalized_key] = value

            # Ensure required fields
            if "id" not in normalized:
                normalized["id"] = self._generate_id(normalized.get("title", "TC"))

            if "title" not in normalized:
                normalized["title"] = normalized.get("name", "Test Case")

            if "description" not in normalized:
                normalized["description"] = normalized.get("summary", normalized["title"])

            # Parse test type
            if "test_type" in normalized:
                normalized["test_type"] = self._parse_test_type(normalized["test_type"])
            else:
                normalized["test_type"] = TestType.FUNCTIONAL

            # Parse priority
            if "priority" in normalized:
                normalized["priority"] = self._parse_priority(normalized["priority"])
            else:
                normalized["priority"] = Priority.MEDIUM

            # Parse steps
            if "steps" in normalized:
                normalized["steps"] = self._parse_steps(normalized["steps"])
            else:
                # Create default step
                normalized["steps"] = [TestStep(
                    step_number=1,
                    action=normalized["title"],
                    expected_result="Test completes successfully",
                )]

            return TestCase(**normalized)

        except Exception as e:
            self.logger.error(f"Failed to convert dict to TestCase: {e}")
            return None

    def _parse_steps(self, steps_data: Union[str, List]) -> List[TestStep]:
        """
        Parse steps data.

        Args:
            steps_data: Steps data (string or list)

        Returns:
            List of TestStep objects
        """
        if isinstance(steps_data, str):
            return self._parse_steps_text(steps_data)

        steps = []
        for i, step_data in enumerate(steps_data, 1):
            if isinstance(step_data, dict):
                step = self._parse_step_dict(step_data, i)
            else:
                step = self._parse_step_line(str(step_data))

            if step:
                steps.append(step)

        return steps

    def _parse_steps_text(self, text: str) -> List[TestStep]:
        """
        Parse steps from text.

        Args:
            text: Steps text

        Returns:
            List of TestStep objects
        """
        steps = []
        lines = text.strip().split("\n")

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Remove numbering if present
            line = re.sub(r"^\d+[\.\)]\s*", "", line)

            # Split by common delimiters
            if " - " in line:
                parts = line.split(" - ", 1)
                action = parts[0]
                expected = parts[1] if len(parts) > 1 else "Step completes"
            elif " -> " in line:
                parts = line.split(" -> ", 1)
                action = parts[0]
                expected = parts[1] if len(parts) > 1 else "Step completes"
            elif " : " in line:
                parts = line.split(" : ", 1)
                action = parts[0]
                expected = parts[1] if len(parts) > 1 else "Step completes"
            else:
                action = line
                expected = "Step completes successfully"

            steps.append(TestStep(
                step_number=len(steps) + 1,
                action=action.strip(),
                expected_result=expected.strip(),
            ))

        return steps

    def _parse_step_dict(self, step_data: Dict[str, Any], index: int) -> Optional[TestStep]:
        """
        Parse step from dictionary.

        Args:
            step_data: Step dictionary
            index: Step index

        Returns:
            TestStep or None
        """
        try:
            return TestStep(
                step_number=step_data.get("step_number", step_data.get("number", index)),
                action=step_data.get("action", step_data.get("step", "")),
                expected_result=step_data.get("expected_result",
                                             step_data.get("expected",
                                                         step_data.get("result", "Step completes"))),
                test_data=step_data.get("test_data", step_data.get("data")),
                validation=step_data.get("validation"),
                notes=step_data.get("notes"),
            )
        except Exception as e:
            self.logger.error(f"Failed to parse step dict: {e}")
            return None

    def _parse_step_line(self, line: str) -> Optional[TestStep]:
        """
        Parse step from line of text.

        Args:
            line: Step line

        Returns:
            TestStep or None
        """
        try:
            # Remove step numbering
            line = re.sub(r"^(?:step\s+)?\d+[\.\):\s]*", "", line, flags=re.IGNORECASE).strip()

            # Default step
            return TestStep(
                step_number=1,
                action=line,
                expected_result="Step completes successfully",
            )
        except:
            return None

    def _parse_test_type(self, value: str) -> TestType:
        """
        Parse test type from string.

        Args:
            value: Test type string

        Returns:
            TestType enum value
        """
        value = value.lower().strip()

        # Map common variations
        type_map = {
            "functional": TestType.FUNCTIONAL,
            "integration": TestType.INTEGRATION,
            "unit": TestType.UNIT,
            "performance": TestType.PERFORMANCE,
            "security": TestType.SECURITY,
            "usability": TestType.USABILITY,
            "edge": TestType.EDGE_CASE,
            "edge_case": TestType.EDGE_CASE,
            "edge case": TestType.EDGE_CASE,
            "negative": TestType.NEGATIVE,
            "regression": TestType.REGRESSION,
            "smoke": TestType.SMOKE,
            "acceptance": TestType.ACCEPTANCE,
        }

        return type_map.get(value, TestType.FUNCTIONAL)

    def _parse_priority(self, value: str) -> Priority:
        """
        Parse priority from string.

        Args:
            value: Priority string

        Returns:
            Priority enum value
        """
        value = value.lower().strip()

        # Map common variations
        priority_map = {
            "critical": Priority.CRITICAL,
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "med": Priority.MEDIUM,
            "low": Priority.LOW,
            "1": Priority.CRITICAL,
            "2": Priority.HIGH,
            "3": Priority.MEDIUM,
            "4": Priority.LOW,
        }

        return priority_map.get(value, Priority.MEDIUM)

    def _normalize_key(self, key: str) -> str:
        """
        Normalize dictionary key.

        Args:
            key: Original key

        Returns:
            Normalized key
        """
        # Convert camelCase to snake_case
        key = re.sub(r"([A-Z])", r"_\1", key).lower()

        # Remove leading underscore if present
        key = key.lstrip("_")

        # Map common variations
        key_map = {
            "name": "title",
            "summary": "description",
            "desc": "description",
            "type": "test_type",
            "testtype": "test_type",
            "prereq": "preconditions",
            "prerequisites": "preconditions",
            "postreq": "postconditions",
            "expected": "expected_results",
            "expect": "expected_results",
        }

        return key_map.get(key, key)

    def _set_field(self, data: Dict[str, Any], field: str, value: str) -> None:
        """
        Set field in test case data.

        Args:
            data: Test case data dictionary
            field: Field name
            value: Field value
        """
        field = field.lower().replace(" ", "_")

        if field in ["description", "desc"]:
            data["description"] = value
        elif field in ["type", "test_type"]:
            data["test_type"] = self._parse_test_type(value)
        elif field == "priority":
            data["priority"] = self._parse_priority(value)
        elif field in ["preconditions", "prerequisites"]:
            data["preconditions"] = value
        elif field in ["postconditions"]:
            data["postconditions"] = value
        elif field in ["steps", "test_steps"]:
            data["steps"] = value  # Will be parsed later
        elif field in ["expected", "expected_results"]:
            data["expected_results"] = value

    def _generate_id(self, title: str) -> str:
        """
        Generate test case ID from title.

        Args:
            title: Test case title

        Returns:
            Generated ID
        """
        # Clean title
        clean = re.sub(r"[^a-zA-Z0-9]+", "_", title)
        clean = clean.strip("_").upper()[:20]

        # Add timestamp for uniqueness
        import time
        timestamp = int(time.time() * 1000) % 100000

        return f"TC_{clean}_{timestamp}"

    def _fallback_parse(self, response: str) -> List[TestCase]:
        """
        Fallback parsing when other methods fail.

        Args:
            response: Response string

        Returns:
            List with single generic test case
        """
        self.logger.warning("Using fallback parser")

        # Create a generic test case from the response
        return [TestCase(
            id=self._generate_id("Fallback"),
            title="Generated Test Case",
            description=response[:200] + "..." if len(response) > 200 else response,
            test_type=TestType.FUNCTIONAL,
            priority=Priority.MEDIUM,
            steps=[TestStep(
                step_number=1,
                action="Execute test as described",
                expected_result="Test completes successfully",
            )],
        )]


__all__ = ["TestCaseParser"]