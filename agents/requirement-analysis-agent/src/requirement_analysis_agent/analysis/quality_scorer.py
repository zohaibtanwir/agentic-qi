"""Quality Scorer - Assesses requirement quality across multiple dimensions."""

from typing import Optional

from requirement_analysis_agent.analysis.base import BaseAnalyzer, LLMParsingError
from requirement_analysis_agent.llm.base import LLMProvider, Message, MessageRole
from requirement_analysis_agent.llm.prompts import ANALYSIS_SYSTEM_PROMPT
from requirement_analysis_agent.models import (
    DimensionScore,
    Grade,
    QualityScore,
)


QUALITY_SCORING_PROMPT = """Analyze the quality of this requirement and provide scores.

## Requirement
**Title:** {title}
**Description:** {description}
**Acceptance Criteria:** {acceptance_criteria}

## Scoring Instructions

Score each dimension from 0-100 and assign a letter grade:
- **A (90-100)**: Excellent - ready for development
- **B (80-89)**: Good - minor improvements needed
- **C (70-79)**: Acceptable - some gaps to address
- **D (60-69)**: Poor - significant issues
- **F (0-59)**: Inadequate - major revision needed

### Dimensions to Score:

1. **Clarity (25%)**: Is the requirement unambiguous and well-defined?
   - Clear language without jargon
   - No ambiguous terms like "should", "might", "fast", "easy"
   - Specific and measurable outcomes

2. **Completeness (30%)**: Are all necessary details included?
   - User/actor defined
   - Actions and outcomes specified
   - Edge cases considered
   - Error handling mentioned

3. **Testability (25%)**: Can the requirement be verified through testing?
   - Measurable acceptance criteria
   - Clear pass/fail conditions
   - Observable outcomes

4. **Consistency (20%)**: Is the requirement internally consistent?
   - No contradictions
   - Aligned terminology
   - Logical flow

Respond with a JSON object:

```json
{{
  "overall_score": <0-100>,
  "overall_grade": "<A|B|C|D|F>",
  "clarity": {{
    "score": <0-100>,
    "grade": "<A|B|C|D|F>",
    "issues": ["list of clarity issues found"]
  }},
  "completeness": {{
    "score": <0-100>,
    "grade": "<A|B|C|D|F>",
    "issues": ["list of completeness issues found"]
  }},
  "testability": {{
    "score": <0-100>,
    "grade": "<A|B|C|D|F>",
    "issues": ["list of testability issues found"]
  }},
  "consistency": {{
    "score": <0-100>,
    "grade": "<A|B|C|D|F>",
    "issues": ["list of consistency issues found"]
  }},
  "recommendation": "action recommendation based on overall score"
}}
```

Respond ONLY with the JSON object."""


class QualityScorer(BaseAnalyzer):
    """Scores requirement quality across multiple dimensions."""

    def __init__(self, llm_client: LLMProvider):
        """Initialize quality scorer."""
        super().__init__(llm_client)

    async def analyze(
        self,
        title: str,
        description: str,
        acceptance_criteria: list[str],
    ) -> QualityScore:
        """
        Score the quality of a requirement.

        Args:
            title: Requirement title
            description: Requirement description
            acceptance_criteria: List of acceptance criteria

        Returns:
            QualityScore with dimension scores and overall assessment
        """
        self.logger.info("Scoring requirement quality", title=title)

        # Build prompt
        ac_text = "\n".join(f"- {ac}" for ac in acceptance_criteria) if acceptance_criteria else "None provided"
        prompt = QUALITY_SCORING_PROMPT.format(
            title=title,
            description=description,
            acceptance_criteria=ac_text,
        )

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
        self._validate_required_fields(
            data,
            ["overall_score", "overall_grade", "clarity", "completeness", "testability", "consistency"],
        )

        # Build quality score
        return QualityScore(
            overall_score=data["overall_score"],
            overall_grade=Grade(data["overall_grade"]),
            clarity=self._parse_dimension_score(data["clarity"]),
            completeness=self._parse_dimension_score(data["completeness"]),
            testability=self._parse_dimension_score(data["testability"]),
            consistency=self._parse_dimension_score(data["consistency"]),
            recommendation=data.get("recommendation", self._generate_recommendation(data["overall_score"])),
        )

    def _parse_dimension_score(self, data: dict) -> DimensionScore:
        """Parse a dimension score from response data."""
        return DimensionScore(
            score=data.get("score", 0),
            grade=Grade(data.get("grade", "F")),
            issues=data.get("issues", []),
        )

    def _generate_recommendation(self, score: int) -> str:
        """Generate a recommendation based on overall score."""
        if score >= 90:
            return "Excellent requirement - ready for test case generation."
        elif score >= 80:
            return "Good requirement - consider addressing minor issues before test generation."
        elif score >= 70:
            return "Acceptable requirement - address identified gaps before proceeding."
        elif score >= 60:
            return "Poor requirement - significant revision needed before test generation."
        else:
            return "Inadequate requirement - major revision required. Consider rewriting."
