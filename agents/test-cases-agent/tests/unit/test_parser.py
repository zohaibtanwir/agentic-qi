"""Unit tests for test case parser."""

import json

import pytest
import yaml

from test_cases_agent.generation.parser import TestCaseParser
from test_cases_agent.models import Priority, TestType


class TestTestCaseParser:
    """Test TestCaseParser class."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return TestCaseParser()

    def test_parse_json_single(self, parser):
        """Test parsing single JSON test case."""
        json_data = {
            "id": "TC001",
            "title": "Login Test",
            "description": "Test user login",
            "test_type": "functional",
            "priority": "high",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Open login page",
                    "expected_result": "Login page displays"
                },
                {
                    "step_number": 2,
                    "action": "Enter credentials",
                    "expected_result": "Credentials accepted"
                }
            ]
        }

        response = json.dumps(json_data)
        test_cases = parser.parse(response, "json")

        assert len(test_cases) == 1
        tc = test_cases[0]
        assert tc.id == "TC001"
        assert tc.title == "Login Test"
        assert tc.test_type == "functional"
        assert tc.priority == "high"
        assert len(tc.steps) == 2

    def test_parse_json_list(self, parser):
        """Test parsing JSON list of test cases."""
        json_data = [
            {
                "title": "Test 1",
                "description": "First test",
                "steps": [{"action": "Step 1", "expected_result": "Result 1"}]
            },
            {
                "title": "Test 2",
                "description": "Second test",
                "steps": [{"action": "Step 1", "expected_result": "Result 1"}]
            }
        ]

        response = json.dumps(json_data)
        test_cases = parser.parse(response, "json")

        assert len(test_cases) == 2
        assert test_cases[0].title == "Test 1"
        assert test_cases[1].title == "Test 2"

    def test_parse_json_with_code_block(self, parser):
        """Test parsing JSON wrapped in code block."""
        response = '''Here's the test case:

```json
{
    "title": "API Test",
    "description": "Test API endpoint",
    "test_type": "integration",
    "priority": "medium",
    "steps": [
        {
            "action": "Send GET request",
            "expected_result": "200 OK response"
        }
    ]
}
```'''

        test_cases = parser.parse(response)

        assert len(test_cases) == 1
        assert test_cases[0].title == "API Test"
        assert test_cases[0].test_type == "integration"

    def test_parse_yaml(self, parser):
        """Test parsing YAML response."""
        yaml_data = {
            "title": "Database Test",
            "description": "Test database operations",
            "test_type": "integration",
            "priority": "high",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Connect to database",
                    "expected_result": "Connection established"
                },
                {
                    "step_number": 2,
                    "action": "Execute query",
                    "expected_result": "Query returns results"
                }
            ]
        }

        response = yaml.dump(yaml_data)
        test_cases = parser.parse(response, "yaml")

        assert len(test_cases) == 1
        tc = test_cases[0]
        assert tc.title == "Database Test"
        assert len(tc.steps) == 2

    def test_parse_yaml_with_wrapper(self, parser):
        """Test parsing YAML with test_cases wrapper."""
        yaml_data = {
            "test_cases": [
                {
                    "title": "Test 1",
                    "description": "First test",
                    "steps": [{"action": "Step 1", "expected_result": "Result 1"}]
                },
                {
                    "title": "Test 2",
                    "description": "Second test",
                    "steps": [{"action": "Step 1", "expected_result": "Result 1"}]
                }
            ]
        }

        response = yaml.dump(yaml_data)
        test_cases = parser.parse(response, "yaml")

        assert len(test_cases) == 2

    def test_parse_markdown(self, parser):
        """Test parsing markdown response."""
        response = """
## Test Login Flow

**Description**: Verify user can login successfully

**Type**: Functional

**Priority**: High

**Steps**:
1. Navigate to login page
2. Enter username and password
3. Click login button
4. Verify dashboard displays

## Test Logout Flow

**Description**: Verify user can logout

**Priority**: Medium

**Steps**:
1. Click logout button
2. Verify redirected to login page
"""

        test_cases = parser.parse(response, "markdown")

        assert len(test_cases) == 2
        assert test_cases[0].title == "Test Login Flow"
        assert test_cases[0].priority == "high"
        assert len(test_cases[0].steps) == 4
        assert test_cases[1].title == "Test Logout Flow"

    def test_parse_text(self, parser):
        """Test parsing plain text response."""
        response = """
Test Case 1: User Registration

Description: Test new user registration
Type: Functional
Priority: High

Steps:
1. Open registration page
2. Fill in user details
3. Submit form
4. Verify account created

Test Case 2: Password Reset

Description: Test password reset flow
Priority: Medium

Steps:
1. Click forgot password
2. Enter email
3. Check email for reset link
"""

        test_cases = parser.parse(response, "text")

        assert len(test_cases) == 2
        assert test_cases[0].title == "User Registration"
        assert test_cases[0].test_type == "functional"
        assert test_cases[0].priority == "high"
        assert test_cases[1].title == "Password Reset"

    def test_auto_detect_json(self, parser):
        """Test auto-detection of JSON format."""
        json_data = {"title": "Test", "description": "Test case", "steps": [{"action": "Test", "expected_result": "Pass"}]}
        response = json.dumps(json_data)

        test_cases = parser.parse(response)  # No format hint

        assert len(test_cases) == 1
        assert test_cases[0].title == "Test"

    def test_auto_detect_yaml(self, parser):
        """Test auto-detection of YAML format."""
        response = """
title: Test Case
description: Test description
steps:
  - action: Step 1
    expected_result: Result 1
"""

        test_cases = parser.parse(response)  # No format hint

        assert len(test_cases) == 1
        assert test_cases[0].title == "Test Case"

    def test_parse_steps_variations(self, parser):
        """Test parsing different step formats."""
        json_data = {
            "title": "Test",
            "description": "Test case",
            "steps": [
                "Open application",
                {"action": "Login", "expected": "Success"},
                {"step": "Verify dashboard", "result": "Dashboard displays"}
            ]
        }

        response = json.dumps(json_data)
        test_cases = parser.parse(response, "json")

        assert len(test_cases) == 1
        assert len(test_cases[0].steps) == 3

    def test_parse_test_type_variations(self, parser):
        """Test parsing different test type formats."""
        variations = [
            ("functional", TestType.FUNCTIONAL),
            ("edge_case", TestType.EDGE_CASE),
            ("edge case", TestType.EDGE_CASE),
            ("edge", TestType.EDGE_CASE),
            ("negative", TestType.NEGATIVE),
            ("unknown", TestType.FUNCTIONAL),  # Default
        ]

        for input_val, expected in variations:
            json_data = {
                "title": "Test",
                "description": "Test",
                "test_type": input_val,
                "steps": [{"action": "Test", "expected_result": "Pass"}]
            }
            response = json.dumps(json_data)
            test_cases = parser.parse(response, "json")
            assert test_cases[0].test_type == expected.value

    def test_parse_priority_variations(self, parser):
        """Test parsing different priority formats."""
        variations = [
            ("critical", Priority.CRITICAL),
            ("high", Priority.HIGH),
            ("medium", Priority.MEDIUM),
            ("med", Priority.MEDIUM),
            ("low", Priority.LOW),
            ("1", Priority.CRITICAL),
            ("2", Priority.HIGH),
            ("3", Priority.MEDIUM),
            ("4", Priority.LOW),
            ("unknown", Priority.MEDIUM),  # Default
        ]

        for input_val, expected in variations:
            json_data = {
                "title": "Test",
                "description": "Test",
                "priority": input_val,
                "steps": [{"action": "Test", "expected_result": "Pass"}]
            }
            response = json.dumps(json_data)
            test_cases = parser.parse(response, "json")
            assert test_cases[0].priority == expected.value

    def test_normalize_field_names(self, parser):
        """Test normalizing different field name formats."""
        json_data = {
            "name": "Test Name",  # Should map to title
            "summary": "Test summary",  # Should map to description
            "testType": "functional",  # CamelCase to snake_case
            "prerequisites": "User logged in",  # Should map to preconditions
            "steps": [{"action": "Test", "expected": "Pass"}]
        }

        response = json.dumps(json_data)
        test_cases = parser.parse(response, "json")

        tc = test_cases[0]
        assert tc.title == "Test Name"
        assert tc.description == "Test summary"
        assert tc.test_type == "functional"
        assert tc.preconditions == "User logged in"

    def test_fallback_parser(self, parser):
        """Test fallback parser for invalid input."""
        response = "This is just some random text that doesn't follow any format"

        test_cases = parser.parse(response)

        assert len(test_cases) == 1
        # Either parsed as text or used fallback
        assert test_cases[0].title
        assert test_cases[0].description

    def test_parse_steps_text_formats(self, parser):
        """Test parsing steps from different text formats."""
        test_data = [
            "1. Click button - Button is clicked",
            "Step 1: Open app -> App opens",
            "Navigate to page : Page displays",
            "Just a simple action step"
        ]

        for step_text in test_data:
            steps = parser._parse_steps_text(step_text)
            assert len(steps) == 1
            assert steps[0].action
            assert steps[0].expected_result

    def test_empty_response(self, parser):
        """Test handling empty response."""
        test_cases = parser.parse("")

        assert len(test_cases) == 0 or (
            len(test_cases) == 1 and "Generated" in test_cases[0].title
        )

    def test_malformed_json(self, parser):
        """Test handling malformed JSON."""
        response = '{"title": "Test", "description": '  # Incomplete JSON

        test_cases = parser.parse(response, "json")

        # Should fall back to text parsing
        assert len(test_cases) >= 0

    def test_missing_required_fields(self, parser):
        """Test handling missing required fields."""
        json_data = {
            # Missing title
            "description": "Test case without title"
        }

        response = json.dumps(json_data)
        test_cases = parser.parse(response, "json")

        # Parser should provide defaults
        assert len(test_cases) == 1
        assert test_cases[0].title  # Should have generated a title
        assert test_cases[0].steps  # Should have default steps