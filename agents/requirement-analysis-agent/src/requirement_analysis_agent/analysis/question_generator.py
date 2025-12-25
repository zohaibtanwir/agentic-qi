"""Question Generator - Generates clarifying questions for requirements."""

from requirement_analysis_agent.analysis.base import BaseAnalyzer
from requirement_analysis_agent.llm.base import LLMProvider, Message, MessageRole
from requirement_analysis_agent.llm.prompts import ANALYSIS_SYSTEM_PROMPT, build_question_generation_prompt
from requirement_analysis_agent.models import ClarifyingQuestion, Gap, QuestionCategory, Severity


class QuestionGenerator(BaseAnalyzer):
    """Generates clarifying questions for ambiguous requirements."""

    def __init__(self, llm_client: LLMProvider):
        """Initialize question generator."""
        super().__init__(llm_client)

    async def analyze(
        self,
        title: str,
        description: str,
        gaps: list[Gap],
    ) -> list[ClarifyingQuestion]:
        """
        Generate clarifying questions for a requirement.

        Args:
            title: Requirement title
            description: Requirement description
            gaps: List of detected gaps

        Returns:
            List of clarifying questions
        """
        self.logger.info("Generating clarifying questions", title=title, gaps_count=len(gaps))

        # Convert gaps to dict format for prompt
        gaps_dict = [
            {"id": gap.id, "description": gap.description, "category": gap.category.value}
            for gap in gaps
        ]

        # Build prompt
        prompt = build_question_generation_prompt(title, description, gaps_dict)

        # Generate response
        messages = [
            Message(role=MessageRole.SYSTEM, content=ANALYSIS_SYSTEM_PROMPT),
            Message(role=MessageRole.USER, content=prompt),
        ]

        response = await self.llm_client.generate(
            messages,
            self._get_generation_config(temperature=0.4),
        )

        # Parse response
        data = self._parse_json_response(response.content)
        questions_data = data.get("questions", [])

        # Convert to ClarifyingQuestion models
        questions = []
        for i, q_data in enumerate(questions_data):
            try:
                question = ClarifyingQuestion(
                    id=q_data.get("id", f"Q-{i+1:03d}"),
                    priority=self._parse_priority(q_data.get("priority", "medium")),
                    category=self._parse_category(q_data.get("category", "scope")),
                    question=q_data.get("question", ""),
                    context=q_data.get("context", ""),
                    suggested_answers=q_data.get("suggested_answers", []),
                )
                questions.append(question)
            except Exception as e:
                self.logger.warning(f"Failed to parse question: {e}", question_data=q_data)

        self.logger.info(
            "Question generation complete",
            total_questions=len(questions),
            high_priority=sum(1 for q in questions if q.priority == Severity.HIGH),
        )

        return questions

    def _parse_priority(self, priority: str) -> Severity:
        """Parse priority from string."""
        priority = priority.lower()
        try:
            return Severity(priority)
        except ValueError:
            return Severity.MEDIUM

    def _parse_category(self, category: str) -> QuestionCategory:
        """Parse question category from string."""
        category = category.lower().replace("-", "_").replace(" ", "_")
        try:
            return QuestionCategory(category)
        except ValueError:
            return QuestionCategory.SCOPE
