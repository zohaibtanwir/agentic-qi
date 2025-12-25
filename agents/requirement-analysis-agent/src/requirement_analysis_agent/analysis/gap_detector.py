"""Gap Detector - Identifies gaps and missing information in requirements."""

from requirement_analysis_agent.analysis.base import BaseAnalyzer
from requirement_analysis_agent.llm.base import LLMProvider, Message, MessageRole
from requirement_analysis_agent.llm.prompts import ANALYSIS_SYSTEM_PROMPT, build_gap_detection_prompt
from requirement_analysis_agent.models import Gap, GapCategory, Severity


class GapDetector(BaseAnalyzer):
    """Detects gaps and missing information in requirements."""

    def __init__(self, llm_client: LLMProvider):
        """Initialize gap detector."""
        super().__init__(llm_client)

    async def analyze(
        self,
        title: str,
        description: str,
        acceptance_criteria: list[str],
    ) -> list[Gap]:
        """
        Detect gaps in a requirement.

        Args:
            title: Requirement title
            description: Requirement description
            acceptance_criteria: List of acceptance criteria

        Returns:
            List of detected gaps
        """
        self.logger.info("Detecting gaps in requirement", title=title)

        # Build prompt
        prompt = build_gap_detection_prompt(title, description, acceptance_criteria)

        # Generate response
        messages = [
            Message(role=MessageRole.SYSTEM, content=ANALYSIS_SYSTEM_PROMPT),
            Message(role=MessageRole.USER, content=prompt),
        ]

        response = await self.llm_client.generate(
            messages,
            self._get_generation_config(temperature=0.3),
        )

        # Parse response
        data = self._parse_json_response(response.content)
        gaps_data = data.get("gaps", [])

        # Convert to Gap models
        gaps = []
        for i, gap_data in enumerate(gaps_data):
            try:
                gap = Gap(
                    id=gap_data.get("id", f"GAP-{i+1:03d}"),
                    category=self._parse_category(gap_data.get("category", "missing_ac")),
                    severity=self._parse_severity(gap_data.get("severity", "medium")),
                    description=gap_data.get("description", ""),
                    location=gap_data.get("location", "requirement"),
                    suggestion=gap_data.get("suggestion", ""),
                )
                gaps.append(gap)
            except Exception as e:
                self.logger.warning(f"Failed to parse gap: {e}", gap_data=gap_data)

        self.logger.info(
            "Gap detection complete",
            total_gaps=len(gaps),
            high_severity=sum(1 for g in gaps if g.severity == Severity.HIGH),
        )

        return gaps

    def _parse_category(self, category: str) -> GapCategory:
        """Parse gap category from string."""
        category = category.lower().replace("-", "_").replace(" ", "_")
        try:
            return GapCategory(category)
        except ValueError:
            # Default to missing_ac if unknown category
            return GapCategory.MISSING_AC

    def _parse_severity(self, severity: str) -> Severity:
        """Parse severity from string."""
        severity = severity.lower()
        try:
            return Severity(severity)
        except ValueError:
            return Severity.MEDIUM
