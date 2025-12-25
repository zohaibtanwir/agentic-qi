"""Parser for Jira story inputs."""

import json
import re
from typing import Any

from requirement_analysis_agent.models import InputType, JiraStoryInput
from requirement_analysis_agent.parsers.base import BaseParser, ParsedInput


class JiraStoryParser(BaseParser[JiraStoryInput]):
    """Parser for Jira story inputs."""

    @property
    def input_type(self) -> InputType:
        """Return the input type."""
        return InputType.JIRA

    def validate(self, input_data: JiraStoryInput) -> list[str]:
        """
        Validate Jira story input.

        Args:
            input_data: JiraStoryInput to validate

        Returns:
            List of validation errors
        """
        errors = []

        if not input_data.key or not input_data.key.strip():
            errors.append("Jira key is required")
        elif not self._is_valid_jira_key(input_data.key):
            errors.append(f"Invalid Jira key format: {input_data.key}")

        if not input_data.summary or not input_data.summary.strip():
            errors.append("Summary is required")

        if not input_data.description or not input_data.description.strip():
            errors.append("Description is required")

        return errors

    def parse(self, input_data: JiraStoryInput) -> ParsedInput:
        """
        Parse Jira story input into normalized format.

        Args:
            input_data: JiraStoryInput to parse

        Returns:
            ParsedInput with normalized content
        """
        # Extract acceptance criteria
        acs = list(input_data.acceptance_criteria)

        # Try to extract additional ACs from description
        description_acs = self._extract_acs_from_description(input_data.description)
        for ac in description_acs:
            if ac not in acs:
                acs.append(ac)

        # Build context from Jira metadata
        context_parts = []
        if input_data.labels:
            context_parts.append(f"Labels: {', '.join(input_data.labels)}")
        if input_data.components:
            context_parts.append(f"Components: {', '.join(input_data.components)}")
        if input_data.priority:
            context_parts.append(f"Priority: {input_data.priority}")
        if input_data.story_points > 0:
            context_parts.append(f"Story Points: {input_data.story_points}")

        # Build metadata
        metadata = {
            "jira_key": input_data.key,
            "story_points": input_data.story_points,
            "priority": input_data.priority,
            "labels": input_data.labels,
            "components": input_data.components,
            "reporter": input_data.reporter,
            "assignee": input_data.assignee,
        }

        # Parse raw JSON if available
        if input_data.raw_json:
            try:
                raw_data = json.loads(input_data.raw_json)
                metadata["raw_fields"] = self._extract_relevant_fields(raw_data)
            except json.JSONDecodeError:
                pass

        return ParsedInput(
            input_type=self.input_type,
            title=f"[{input_data.key}] {input_data.summary}",
            description=input_data.description,
            acceptance_criteria=acs,
            context="\n".join(context_parts),
            metadata=metadata,
        )

    def _is_valid_jira_key(self, key: str) -> bool:
        """Check if a string is a valid Jira key format."""
        # Jira keys are typically PROJECT-NUMBER format
        pattern = r"^[A-Z][A-Z0-9]+-\d+$"
        return bool(re.match(pattern, key.upper()))

    def _extract_acs_from_description(self, description: str) -> list[str]:
        """
        Extract acceptance criteria from description text.

        Looks for common patterns like:
        - Numbered lists (1., 2., etc.)
        - Bulleted lists (*, -, etc.)
        - "Acceptance Criteria:" sections
        - "Given/When/Then" patterns

        Args:
            description: Description text to parse

        Returns:
            List of extracted acceptance criteria
        """
        acs = []

        # Look for Acceptance Criteria section
        ac_section_match = re.search(
            r"acceptance\s*criteria[:\s]*\n(.*?)(?:\n\n|\Z)",
            description,
            re.IGNORECASE | re.DOTALL,
        )

        if ac_section_match:
            ac_text = ac_section_match.group(1)
            # Extract bullet points or numbered items
            items = re.findall(r"[-*•]\s*(.+?)(?:\n|$)", ac_text)
            items.extend(re.findall(r"\d+[.)]\s*(.+?)(?:\n|$)", ac_text))
            acs.extend([item.strip() for item in items if item.strip()])

        # Look for Given/When/Then patterns
        gherkin_matches = re.findall(
            r"(Given\s+.+?(?:\n(?:And|When|Then)\s+.+?)*)",
            description,
            re.IGNORECASE | re.DOTALL,
        )
        for match in gherkin_matches:
            # Clean up and add as single AC
            cleaned = " ".join(match.split())
            if cleaned and cleaned not in acs:
                acs.append(cleaned)

        return acs

    def _extract_relevant_fields(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract relevant fields from raw Jira JSON.

        Args:
            raw_data: Raw Jira API response

        Returns:
            Dictionary with relevant extracted fields
        """
        relevant = {}

        # Handle standard Jira API structure
        fields = raw_data.get("fields", raw_data)

        # Extract useful fields
        field_mappings = {
            "issuetype": ("issue_type", lambda x: x.get("name") if isinstance(x, dict) else x),
            "status": ("status", lambda x: x.get("name") if isinstance(x, dict) else x),
            "created": ("created", str),
            "updated": ("updated", str),
            "resolution": (
                "resolution",
                lambda x: x.get("name") if isinstance(x, dict) else x,
            ),
            "fixVersions": (
                "fix_versions",
                lambda x: [v.get("name") for v in x] if isinstance(x, list) else [],
            ),
            "customfield_10014": ("epic_link", str),  # Common epic link field
        }

        for jira_field, (our_field, transformer) in field_mappings.items():
            if jira_field in fields and fields[jira_field]:
                try:
                    relevant[our_field] = transformer(fields[jira_field])
                except (TypeError, KeyError, AttributeError):
                    pass

        return relevant

    @classmethod
    def from_json(cls, json_data: str) -> tuple["JiraStoryParser", JiraStoryInput]:
        """
        Create parser and input from raw Jira JSON.

        Args:
            json_data: Raw Jira API JSON response

        Returns:
            Tuple of (parser instance, parsed JiraStoryInput)
        """
        parser = cls()
        data = json.loads(json_data)

        # Handle both direct fields and nested fields structure
        fields = data.get("fields", data)

        input_data = JiraStoryInput(
            key=data.get("key", ""),
            summary=fields.get("summary", ""),
            description=fields.get("description", ""),
            acceptance_criteria=cls._parse_acceptance_criteria_field(fields),
            story_points=fields.get("customfield_10016", 0) or 0,  # Common story points field
            labels=fields.get("labels", []),
            components=[c.get("name", "") for c in fields.get("components", [])],
            priority=fields.get("priority", {}).get("name", "Medium")
            if isinstance(fields.get("priority"), dict)
            else "Medium",
            reporter=fields.get("reporter", {}).get("emailAddress", "")
            if isinstance(fields.get("reporter"), dict)
            else "",
            assignee=fields.get("assignee", {}).get("emailAddress", "")
            if isinstance(fields.get("assignee"), dict)
            else "",
            raw_json=json_data,
        )

        return parser, input_data

    @staticmethod
    def _parse_acceptance_criteria_field(fields: dict[str, Any]) -> list[str]:
        """Parse acceptance criteria from Jira fields."""
        # Common custom field names for ACs
        ac_field_names = [
            "customfield_10020",  # Common AC field
            "acceptance_criteria",
            "acceptanceCriteria",
        ]

        for field_name in ac_field_names:
            ac_value = fields.get(field_name)
            if ac_value:
                if isinstance(ac_value, list):
                    return [str(ac) for ac in ac_value if ac]
                elif isinstance(ac_value, str):
                    # Split by newlines or bullet points
                    items = re.split(r"\n[-*•]\s*|\n\d+[.)]\s*|\n", ac_value)
                    return [item.strip() for item in items if item.strip()]

        return []
