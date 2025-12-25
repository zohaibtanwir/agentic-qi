"""Parser for free-form text requirement inputs."""

import re

from requirement_analysis_agent.models import InputType, FreeFormInput
from requirement_analysis_agent.parsers.base import BaseParser, ParsedInput


class FreeFormParser(BaseParser[FreeFormInput]):
    """Parser for free-form text requirement inputs."""

    # Minimum text length for a valid requirement
    MIN_TEXT_LENGTH = 20

    @property
    def input_type(self) -> InputType:
        """Return the input type."""
        return InputType.FREE_FORM

    def validate(self, input_data: FreeFormInput) -> list[str]:
        """
        Validate free-form text input.

        Args:
            input_data: FreeFormInput to validate

        Returns:
            List of validation errors
        """
        errors = []

        if not input_data.text or not input_data.text.strip():
            errors.append("Requirement text is required")
        elif len(input_data.text.strip()) < self.MIN_TEXT_LENGTH:
            errors.append(
                f"Requirement text is too short (minimum {self.MIN_TEXT_LENGTH} characters)"
            )

        return errors

    def parse(self, input_data: FreeFormInput) -> ParsedInput:
        """
        Parse free-form text input into normalized format.

        Args:
            input_data: FreeFormInput to parse

        Returns:
            ParsedInput with normalized content
        """
        text = input_data.text.strip()

        # Try to extract a title
        title = self._extract_title(text, input_data.title)

        # Extract any embedded acceptance criteria
        acs = self._extract_acceptance_criteria(text)

        # Clean description (remove already extracted parts)
        description = self._clean_description(text, acs)

        # Build context
        context = input_data.context.strip() if input_data.context else ""

        # Extract metadata from text structure
        metadata = self._extract_metadata(text)

        return ParsedInput(
            input_type=self.input_type,
            title=title,
            description=description,
            acceptance_criteria=acs,
            context=context,
            metadata=metadata,
        )

    def _extract_title(self, text: str, provided_title: str) -> str:
        """
        Extract or derive a title from the requirement text.

        Args:
            text: Full requirement text
            provided_title: Optional explicitly provided title

        Returns:
            Title string
        """
        # Use provided title if available
        if provided_title and provided_title.strip():
            return provided_title.strip()

        # Try to extract from first line if it looks like a title
        lines = text.split("\n")
        first_line = lines[0].strip()

        # Check if first line looks like a title (short, no punctuation at end except ?)
        if len(first_line) < 100 and not first_line.endswith((".", ":", ",")):
            # Remove common prefixes
            title = re.sub(r"^(feature|requirement|story|epic|task)[:\s-]+", "", first_line, flags=re.IGNORECASE)
            if title:
                return title.strip()

        # Look for "As a... I want..." pattern
        user_story_match = re.search(
            r"as\s+(?:a|an)\s+(.+?),?\s+i\s+want\s+(?:to\s+)?(.+?)(?:\s+so\s+that|\s*$)",
            text,
            re.IGNORECASE,
        )
        if user_story_match:
            action = user_story_match.group(2).strip()
            # Capitalize first letter and limit length
            return (action[0].upper() + action[1:])[:80]

        # Fallback: use first 60 chars
        return first_line[:60] + ("..." if len(first_line) > 60 else "")

    def _extract_acceptance_criteria(self, text: str) -> list[str]:
        """
        Extract acceptance criteria from free-form text.

        Args:
            text: Requirement text to parse

        Returns:
            List of acceptance criteria strings
        """
        acs = []

        # Look for explicit AC section
        ac_section = self._find_ac_section(text)
        if ac_section:
            acs.extend(self._parse_list_items(ac_section))

        # Look for Given/When/Then patterns
        gherkin_acs = self._extract_gherkin_scenarios(text)
        for ac in gherkin_acs:
            if ac not in acs:
                acs.append(ac)

        # Look for "should" statements that could be ACs
        should_statements = self._extract_should_statements(text)
        for statement in should_statements:
            if statement not in acs:
                acs.append(statement)

        return acs

    def _find_ac_section(self, text: str) -> str:
        """Find acceptance criteria section in text."""
        patterns = [
            r"acceptance\s*criteria[:\s]*\n(.*?)(?:\n\n|\n[A-Z]|\Z)",
            r"criteria[:\s]*\n(.*?)(?:\n\n|\n[A-Z]|\Z)",
            r"requirements[:\s]*\n(.*?)(?:\n\n|\n[A-Z]|\Z)",
            r"must\s+(?:have|meet)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)

        return ""

    def _parse_list_items(self, text: str) -> list[str]:
        """Parse list items from text."""
        items = []

        # Match bullet points
        bullet_matches = re.findall(r"[-*•]\s*(.+?)(?:\n|$)", text)
        items.extend([m.strip() for m in bullet_matches if m.strip()])

        # Match numbered items
        numbered_matches = re.findall(r"\d+[.)]\s*(.+?)(?:\n|$)", text)
        items.extend([m.strip() for m in numbered_matches if m.strip()])

        # Match checkbox items
        checkbox_matches = re.findall(r"\[[ x]\]\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        items.extend([m.strip() for m in checkbox_matches if m.strip()])

        return items

    def _extract_gherkin_scenarios(self, text: str) -> list[str]:
        """Extract Gherkin-style scenarios from text."""
        scenarios = []

        # Match complete scenarios
        scenario_pattern = r"((?:Given|Scenario)[^\n]*(?:\n(?:And|When|Then|But)[^\n]*)*)"
        matches = re.findall(scenario_pattern, text, re.IGNORECASE)

        for match in matches:
            # Clean up and normalize
            cleaned = " ".join(match.split())
            if len(cleaned) > 20:  # Meaningful scenario
                scenarios.append(cleaned)

        return scenarios

    def _extract_should_statements(self, text: str) -> list[str]:
        """Extract 'should' statements that could be acceptance criteria."""
        statements = []

        # Match sentences containing "should"
        should_pattern = r"(?:The\s+)?(?:system|user|application|feature|it)\s+should\s+([^.]+\.)"
        matches = re.findall(should_pattern, text, re.IGNORECASE)

        for match in matches:
            cleaned = match.strip()
            if len(cleaned) > 10:
                statements.append(f"System should {cleaned}")

        return statements

    def _clean_description(self, text: str, extracted_acs: list[str]) -> str:
        """
        Clean the description by removing already extracted content.

        Args:
            text: Original text
            extracted_acs: ACs that were extracted

        Returns:
            Cleaned description
        """
        description = text

        # Remove AC section headers
        description = re.sub(
            r"acceptance\s*criteria[:\s]*\n",
            "",
            description,
            flags=re.IGNORECASE,
        )

        # The actual AC content removal would be too aggressive,
        # so we keep it in the description for now
        return description.strip()

    def _extract_metadata(self, text: str) -> dict:
        """Extract metadata from text structure."""
        metadata = {}

        # Detect if it's a user story format
        if re.search(r"as\s+(?:a|an)\s+", text, re.IGNORECASE):
            metadata["format"] = "user_story"

        # Detect if it has Gherkin
        if re.search(r"\b(?:given|when|then)\b", text, re.IGNORECASE):
            metadata["has_gherkin"] = True

        # Count potential requirements
        bullet_count = len(re.findall(r"[-*•]\s+", text))
        numbered_count = len(re.findall(r"\d+[.)]\s+", text))
        metadata["list_items_count"] = bullet_count + numbered_count

        # Estimate word count
        metadata["word_count"] = len(text.split())

        return metadata
