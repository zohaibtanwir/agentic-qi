"""Structure Extractor - Extracts structured information from requirements."""

from requirement_analysis_agent.analysis.base import BaseAnalyzer
from requirement_analysis_agent.llm.base import LLMProvider, Message, MessageRole
from requirement_analysis_agent.llm.prompts import ANALYSIS_SYSTEM_PROMPT, build_structure_prompt
from requirement_analysis_agent.models import RequirementStructure


class StructureExtractor(BaseAnalyzer):
    """Extracts structured components from requirement text."""

    def __init__(self, llm_client: LLMProvider):
        """Initialize structure extractor."""
        super().__init__(llm_client)

    async def analyze(
        self,
        title: str,
        description: str,
    ) -> RequirementStructure:
        """
        Extract structured information from a requirement.

        Args:
            title: Requirement title
            description: Requirement description

        Returns:
            RequirementStructure with extracted components
        """
        self.logger.info("Extracting requirement structure", title=title)

        # Combine title and description for full context
        requirement_text = f"Title: {title}\n\nDescription: {description}"

        # Build prompt
        prompt = build_structure_prompt(requirement_text)

        # Generate response
        messages = [
            Message(role=MessageRole.SYSTEM, content=ANALYSIS_SYSTEM_PROMPT),
            Message(role=MessageRole.USER, content=prompt),
        ]

        response = await self.llm_client.generate(
            messages,
            self._get_generation_config(temperature=0.2),
        )

        # Parse response
        data = self._parse_json_response(response.content)

        # Build structure
        structure = RequirementStructure(
            actor=data.get("actor", "User"),
            secondary_actors=data.get("secondary_actors", []),
            action=data.get("action", ""),
            object=data.get("object", ""),
            outcome=data.get("outcome", ""),
            preconditions=data.get("preconditions", []),
            postconditions=data.get("postconditions", []),
            triggers=data.get("triggers", []),
            constraints=data.get("constraints", []),
            entities=data.get("entities", []),
        )

        self.logger.info(
            "Structure extraction complete",
            actor=structure.actor,
            entities_count=len(structure.entities),
        )

        return structure
