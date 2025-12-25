"""Parser for meeting transcript inputs."""

import re
from dataclasses import dataclass

from requirement_analysis_agent.models import InputType, TranscriptInput
from requirement_analysis_agent.parsers.base import BaseParser, ParsedInput


@dataclass
class TranscriptLine:
    """A single line from a transcript with speaker identification."""

    speaker: str
    content: str
    line_number: int


class TranscriptParser(BaseParser[TranscriptInput]):
    """Parser for meeting transcript inputs."""

    # Minimum transcript length
    MIN_TRANSCRIPT_LENGTH = 50

    # Common speaker patterns in transcripts
    SPEAKER_PATTERNS = [
        r"^([A-Za-z][A-Za-z\s]+):\s*(.+)$",  # "John Doe: text"
        r"^\[([A-Za-z][A-Za-z\s]+)\]\s*(.+)$",  # "[John Doe] text"
        r"^([A-Za-z]+)\s*>\s*(.+)$",  # "John> text"
        r"^\(([A-Za-z][A-Za-z\s]+)\)\s*(.+)$",  # "(John Doe) text"
    ]

    # Keywords that indicate requirements
    REQUIREMENT_KEYWORDS = [
        "need", "must", "should", "want", "require",
        "feature", "functionality", "capability",
        "user can", "users can", "able to",
        "has to", "have to", "necessary",
        "acceptance criteria", "ac", "criteria",
    ]

    # Keywords that indicate decisions
    DECISION_KEYWORDS = [
        "decided", "agreed", "will do", "let's go with",
        "final", "conclusion", "action item",
    ]

    @property
    def input_type(self) -> InputType:
        """Return the input type."""
        return InputType.TRANSCRIPT

    def validate(self, input_data: TranscriptInput) -> list[str]:
        """
        Validate transcript input.

        Args:
            input_data: TranscriptInput to validate

        Returns:
            List of validation errors
        """
        errors = []

        if not input_data.transcript or not input_data.transcript.strip():
            errors.append("Transcript text is required")
        elif len(input_data.transcript.strip()) < self.MIN_TRANSCRIPT_LENGTH:
            errors.append(
                f"Transcript is too short (minimum {self.MIN_TRANSCRIPT_LENGTH} characters)"
            )

        return errors

    def parse(self, input_data: TranscriptInput) -> ParsedInput:
        """
        Parse transcript input into normalized format.

        This extracts requirements from meeting transcripts by:
        1. Parsing speaker turns
        2. Identifying requirement-related statements
        3. Extracting decisions and action items
        4. Building a consolidated requirement description

        Args:
            input_data: TranscriptInput to parse

        Returns:
            ParsedInput with extracted requirements
        """
        transcript = input_data.transcript.strip()

        # Parse transcript into structured lines
        parsed_lines = self._parse_transcript_lines(transcript)

        # Extract requirement-related statements
        requirement_statements = self._extract_requirement_statements(parsed_lines)

        # Extract decisions and action items
        decisions = self._extract_decisions(parsed_lines)

        # Build title from meeting context
        title = self._build_title(input_data, requirement_statements)

        # Build description from requirement statements
        description = self._build_description(requirement_statements)

        # Convert decisions to acceptance criteria
        acs = self._build_acceptance_criteria(decisions, requirement_statements)

        # Build context
        context = self._build_context(input_data, parsed_lines)

        # Build metadata
        metadata = self._build_metadata(input_data, parsed_lines, requirement_statements)

        return ParsedInput(
            input_type=self.input_type,
            title=title,
            description=description,
            acceptance_criteria=acs,
            context=context,
            metadata=metadata,
        )

    def _parse_transcript_lines(self, transcript: str) -> list[TranscriptLine]:
        """Parse transcript into structured lines with speaker identification."""
        lines = transcript.split("\n")
        parsed: list[TranscriptLine] = []
        current_speaker = "Unknown"

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Try to match speaker patterns
            speaker = None
            content = line

            for pattern in self.SPEAKER_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    speaker = match.group(1).strip()
                    content = match.group(2).strip()
                    break

            if speaker:
                current_speaker = speaker

            if content:
                parsed.append(TranscriptLine(
                    speaker=current_speaker,
                    content=content,
                    line_number=i + 1,
                ))

        return parsed

    def _extract_requirement_statements(
        self, lines: list[TranscriptLine]
    ) -> list[TranscriptLine]:
        """Extract lines that contain requirement-related content."""
        requirement_lines = []

        for line in lines:
            content_lower = line.content.lower()
            if any(keyword in content_lower for keyword in self.REQUIREMENT_KEYWORDS):
                requirement_lines.append(line)

        return requirement_lines

    def _extract_decisions(self, lines: list[TranscriptLine]) -> list[TranscriptLine]:
        """Extract lines that contain decisions or action items."""
        decision_lines = []

        for line in lines:
            content_lower = line.content.lower()
            if any(keyword in content_lower for keyword in self.DECISION_KEYWORDS):
                decision_lines.append(line)

        return decision_lines

    def _build_title(
        self,
        input_data: TranscriptInput,
        requirement_statements: list[TranscriptLine],
    ) -> str:
        """Build a title for the requirement."""
        # Use meeting title if available
        if input_data.meeting_title:
            return f"Requirements from: {input_data.meeting_title}"

        # Try to derive from first requirement statement
        if requirement_statements:
            first = requirement_statements[0].content
            # Extract the key phrase
            match = re.search(
                r"(?:need|want|require)s?\s+(?:to\s+)?(.+?)(?:\.|$)",
                first,
                re.IGNORECASE,
            )
            if match:
                phrase = match.group(1).strip()[:60]
                return phrase[0].upper() + phrase[1:] if phrase else "Requirement from transcript"

        return "Requirement extracted from meeting transcript"

    def _build_description(self, requirement_statements: list[TranscriptLine]) -> str:
        """Build a description from requirement statements."""
        if not requirement_statements:
            return "No specific requirements extracted from transcript."

        # Group by speaker to show context
        description_parts = []

        for line in requirement_statements:
            description_parts.append(f"- [{line.speaker}]: {line.content}")

        return "Extracted requirements from transcript:\n" + "\n".join(description_parts)

    def _build_acceptance_criteria(
        self,
        decisions: list[TranscriptLine],
        requirement_statements: list[TranscriptLine],
    ) -> list[str]:
        """Build acceptance criteria from decisions and requirements."""
        acs = []

        # Convert decisions to ACs
        for decision in decisions:
            # Clean up the decision statement
            content = decision.content
            # Remove common prefixes
            content = re.sub(
                r"^(?:we\s+)?(?:decided|agreed|will)\s+(?:to\s+)?",
                "",
                content,
                flags=re.IGNORECASE,
            )
            if content and len(content) > 10:
                acs.append(content.strip())

        # If no decisions, try to convert strong requirement statements
        if not acs:
            for line in requirement_statements:
                content = line.content
                # Look for "must" or "should" statements
                match = re.search(
                    r"(?:system|user|it)?\s*(?:must|should)\s+(.+?)(?:\.|$)",
                    content,
                    re.IGNORECASE,
                )
                if match:
                    acs.append(match.group(1).strip())

        return acs[:10]  # Limit to reasonable number

    def _build_context(
        self,
        input_data: TranscriptInput,
        lines: list[TranscriptLine],
    ) -> str:
        """Build context information."""
        context_parts = []

        if input_data.meeting_title:
            context_parts.append(f"Meeting: {input_data.meeting_title}")

        if input_data.meeting_date:
            context_parts.append(f"Date: {input_data.meeting_date}")

        if input_data.participants:
            context_parts.append(f"Participants: {', '.join(input_data.participants)}")

        # Identify unique speakers from transcript
        speakers = set(line.speaker for line in lines if line.speaker != "Unknown")
        if speakers:
            context_parts.append(f"Speakers in transcript: {', '.join(sorted(speakers))}")

        return "\n".join(context_parts)

    def _build_metadata(
        self,
        input_data: TranscriptInput,
        lines: list[TranscriptLine],
        requirement_statements: list[TranscriptLine],
    ) -> dict:
        """Build metadata about the transcript."""
        # Count unique speakers
        speakers = set(line.speaker for line in lines if line.speaker != "Unknown")

        return {
            "meeting_title": input_data.meeting_title,
            "meeting_date": input_data.meeting_date,
            "participants": input_data.participants,
            "total_lines": len(lines),
            "requirement_statements_count": len(requirement_statements),
            "speakers_identified": list(speakers),
            "speaker_count": len(speakers),
        }

    def get_requirement_density(self, input_data: TranscriptInput) -> float:
        """
        Calculate the density of requirement-related content.

        Returns a score from 0.0 to 1.0 indicating how much of the
        transcript is about requirements.
        """
        if not input_data.transcript:
            return 0.0

        lines = self._parse_transcript_lines(input_data.transcript)
        if not lines:
            return 0.0

        requirement_lines = self._extract_requirement_statements(lines)
        return len(requirement_lines) / len(lines)
