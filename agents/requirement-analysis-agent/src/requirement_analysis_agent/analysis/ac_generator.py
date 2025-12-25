"""AC Generator - Generates acceptance criteria for requirements."""

from requirement_analysis_agent.analysis.base import BaseAnalyzer
from requirement_analysis_agent.llm.base import LLMProvider, Message, MessageRole
from requirement_analysis_agent.llm.prompts import ANALYSIS_SYSTEM_PROMPT, build_ac_generation_prompt
from requirement_analysis_agent.models import ACSource, Gap, GeneratedAC


class ACGenerator(BaseAnalyzer):
    """Generates acceptance criteria based on gaps and requirement structure."""

    def __init__(self, llm_client: LLMProvider):
        """Initialize AC generator."""
        super().__init__(llm_client)

    async def analyze(
        self,
        title: str,
        description: str,
        existing_acs: list[str],
        gaps: list[Gap],
    ) -> list[GeneratedAC]:
        """
        Generate acceptance criteria for a requirement.

        Args:
            title: Requirement title
            description: Requirement description
            existing_acs: Existing acceptance criteria
            gaps: Detected gaps

        Returns:
            List of generated acceptance criteria
        """
        self.logger.info(
            "Generating acceptance criteria",
            title=title,
            existing_acs_count=len(existing_acs),
            gaps_count=len(gaps),
        )

        # Convert gaps to dict format for prompt
        gaps_dict = [
            {"id": gap.id, "description": gap.description, "category": gap.category.value}
            for gap in gaps
        ]

        # Build prompt
        prompt = build_ac_generation_prompt(title, description, existing_acs, gaps_dict)

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
        acs_data = data.get("generated_acs", [])

        # Convert to GeneratedAC models
        generated_acs = []
        for i, ac_data in enumerate(acs_data):
            try:
                ac = GeneratedAC(
                    id=ac_data.get("id", f"AC-GEN-{i+1:03d}"),
                    source=self._parse_source(ac_data.get("source", "gap_detection")),
                    confidence=min(1.0, max(0.0, float(ac_data.get("confidence", 0.8)))),
                    text=ac_data.get("text", ""),
                    gherkin=ac_data.get("gherkin", ""),
                )
                generated_acs.append(ac)
            except Exception as e:
                self.logger.warning(f"Failed to parse AC: {e}", ac_data=ac_data)

        self.logger.info(
            "AC generation complete",
            total_generated=len(generated_acs),
            high_confidence=sum(1 for ac in generated_acs if ac.confidence >= 0.8),
        )

        return generated_acs

    def _parse_source(self, source: str) -> ACSource:
        """Parse AC source from string."""
        source = source.lower().replace("-", "_").replace(" ", "_")
        try:
            return ACSource(source)
        except ValueError:
            return ACSource.GAP_DETECTION
