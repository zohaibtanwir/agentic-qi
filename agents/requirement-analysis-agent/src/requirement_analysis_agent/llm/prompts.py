"""Prompt templates for requirement analysis using LLMs."""

from typing import Optional

# System prompt for requirement analysis
ANALYSIS_SYSTEM_PROMPT = """You are an expert requirement analyst specializing in software development. Your role is to analyze requirements for quality, completeness, and testability.

You analyze requirements from three perspectives:
1. **Clarity**: Is the requirement unambiguous and well-defined?
2. **Completeness**: Are all necessary details included?
3. **Testability**: Can the requirement be verified through testing?
4. **Consistency**: Is the requirement internally consistent and aligned with context?

When analyzing, you:
- Identify gaps, missing information, and ambiguities
- Extract structured information (actors, actions, outcomes)
- Generate clarifying questions for unclear parts
- Suggest acceptance criteria when missing
- Validate against domain knowledge when available

Always respond with structured JSON as specified in the user prompt."""

# Prompt template for comprehensive requirement analysis
COMPREHENSIVE_ANALYSIS_PROMPT = """Analyze the following requirement and provide a detailed assessment.

## Requirement Details

**Title:** {title}

**Description:**
{description}

**Existing Acceptance Criteria:**
{acceptance_criteria}

**Additional Context:**
{context}

## Analysis Instructions

Analyze this requirement and respond with a JSON object containing:

```json
{{
  "quality_score": {{
    "overall_score": <0-100>,
    "overall_grade": "<A|B|C|D|F>",
    "clarity": {{
      "score": <0-100>,
      "grade": "<A|B|C|D|F>",
      "issues": ["list of clarity issues"]
    }},
    "completeness": {{
      "score": <0-100>,
      "grade": "<A|B|C|D|F>",
      "issues": ["list of completeness issues"]
    }},
    "testability": {{
      "score": <0-100>,
      "grade": "<A|B|C|D|F>",
      "issues": ["list of testability issues"]
    }},
    "consistency": {{
      "score": <0-100>,
      "grade": "<A|B|C|D|F>",
      "issues": ["list of consistency issues"]
    }},
    "recommendation": "action recommendation based on score"
  }},
  "extracted_structure": {{
    "actor": "primary actor (who)",
    "secondary_actors": ["other actors involved"],
    "action": "what is being done",
    "object": "what is acted upon",
    "outcome": "expected result (why)",
    "preconditions": ["required starting state"],
    "postconditions": ["expected end state"],
    "triggers": ["what initiates the action"],
    "constraints": ["limitations or rules"],
    "entities": ["domain entities mentioned"]
  }},
  "gaps": [
    {{
      "id": "GAP-001",
      "category": "<missing_ac|ambiguous_term|undefined_term|missing_error_handling|missing_edge_case|missing_precondition|missing_postcondition|contradiction>",
      "severity": "<high|medium|low>",
      "description": "what is missing or unclear",
      "location": "where in the requirement",
      "suggestion": "how to fix it"
    }}
  ],
  "questions": [
    {{
      "id": "Q-001",
      "priority": "<high|medium|low>",
      "category": "<error_handling|scope|ux|security|performance|validation|integration|data>",
      "question": "the clarifying question",
      "context": "why this question matters",
      "suggested_answers": ["possible answer 1", "possible answer 2"]
    }}
  ],
  "generated_acs": [
    {{
      "id": "AC-GEN-001",
      "source": "<gap_detection|domain_knowledge|structure_extraction>",
      "confidence": <0.0-1.0>,
      "text": "plain text acceptance criterion",
      "gherkin": "Given... When... Then..."
    }}
  ],
  "ready_for_test_generation": <true|false>,
  "blockers": ["list of blocking issues preventing test generation"]
}}
```

## Scoring Guidelines

- **A (90-100)**: Excellent - ready for development
- **B (80-89)**: Good - minor improvements needed
- **C (70-79)**: Acceptable - some gaps to address
- **D (60-69)**: Poor - significant issues
- **F (0-59)**: Inadequate - major revision needed

## Gap Categories

- `missing_ac`: Acceptance criteria not specified
- `ambiguous_term`: Vague or undefined language
- `undefined_term`: Domain term not explained
- `missing_error_handling`: No failure scenarios
- `missing_edge_case`: Boundary conditions not covered
- `missing_precondition`: Assumed state not specified
- `missing_postcondition`: End state not defined
- `contradiction`: Conflicting statements

Respond ONLY with the JSON object, no additional text."""


# Prompt template for extracting requirement structure
STRUCTURE_EXTRACTION_PROMPT = """Extract the structured components from this requirement.

## Requirement Text
{requirement_text}

## Instructions

Identify and extract the following components:

1. **Actor**: Who is performing the action? (the subject)
2. **Action**: What action is being performed? (the verb)
3. **Object**: What is the action being performed on? (the object)
4. **Outcome**: What is the expected result or benefit?
5. **Preconditions**: What must be true before this action?
6. **Postconditions**: What will be true after this action?
7. **Triggers**: What initiates this action?
8. **Constraints**: What limitations or rules apply?
9. **Entities**: What domain entities are mentioned?

Respond with a JSON object:

```json
{{
  "actor": "identified actor or 'User' if not specified",
  "secondary_actors": ["other actors mentioned"],
  "action": "the main action",
  "object": "the target of the action",
  "outcome": "the expected result",
  "preconditions": ["list of preconditions"],
  "postconditions": ["list of postconditions"],
  "triggers": ["list of triggers"],
  "constraints": ["list of constraints"],
  "entities": ["list of domain entities"],
  "is_user_story_format": <true|false>,
  "confidence": <0.0-1.0>
}}
```

Respond ONLY with the JSON object."""


# Prompt template for gap detection
GAP_DETECTION_PROMPT = """Analyze this requirement for gaps and missing information.

## Requirement
**Title:** {title}
**Description:** {description}
**Acceptance Criteria:** {acceptance_criteria}

## Instructions

Identify gaps in the following categories:
- Missing acceptance criteria
- Ambiguous terminology
- Undefined domain terms
- Missing error handling scenarios
- Missing edge cases
- Missing preconditions
- Missing postconditions
- Internal contradictions

For each gap found, assess its severity:
- **High**: Blocks development or testing
- **Medium**: May cause issues during implementation
- **Low**: Nice to have clarification

Respond with a JSON array:

```json
{{
  "gaps": [
    {{
      "id": "GAP-001",
      "category": "gap category",
      "severity": "high|medium|low",
      "description": "detailed description of the gap",
      "location": "where in the requirement (e.g., 'description paragraph 2')",
      "suggestion": "how to address this gap"
    }}
  ],
  "total_high_severity": <count>,
  "total_medium_severity": <count>,
  "total_low_severity": <count>
}}
```

Respond ONLY with the JSON object."""


# Prompt template for generating acceptance criteria
AC_GENERATION_PROMPT = """Generate acceptance criteria for this requirement.

## Requirement
**Title:** {title}
**Description:** {description}
**Existing ACs:** {existing_acs}
**Identified Gaps:** {gaps}

## Instructions

Generate acceptance criteria that:
1. Address the identified gaps
2. Cover the main functionality
3. Include error handling scenarios
4. Consider edge cases
5. Are testable and measurable

For each generated AC, provide:
- Plain text format
- Gherkin format (Given/When/Then)
- Confidence score (how confident you are this AC is needed)
- Source (why you generated this AC)

Respond with a JSON object:

```json
{{
  "generated_acs": [
    {{
      "id": "AC-GEN-001",
      "source": "gap_detection|domain_knowledge|structure_extraction",
      "confidence": <0.0-1.0>,
      "text": "plain text AC",
      "gherkin": "Given [precondition]\\nWhen [action]\\nThen [outcome]",
      "addresses_gap": "GAP-001 or null"
    }}
  ]
}}
```

Respond ONLY with the JSON object."""


# Prompt template for generating clarifying questions
QUESTION_GENERATION_PROMPT = """Generate clarifying questions for this requirement.

## Requirement
**Title:** {title}
**Description:** {description}
**Identified Gaps:** {gaps}

## Instructions

Generate questions that would help clarify:
1. Ambiguous terms or phrases
2. Missing scope definitions
3. Error handling behavior
4. User experience details
5. Security considerations
6. Performance expectations
7. Integration points
8. Data requirements

Prioritize questions by:
- **High**: Blocks development if unanswered
- **Medium**: Important for complete implementation
- **Low**: Would improve the requirement

Respond with a JSON object:

```json
{{
  "questions": [
    {{
      "id": "Q-001",
      "priority": "high|medium|low",
      "category": "error_handling|scope|ux|security|performance|validation|integration|data",
      "question": "the clarifying question",
      "context": "why this question is important",
      "suggested_answers": ["possible answer 1", "possible answer 2", "possible answer 3"],
      "related_gap": "GAP-001 or null"
    }}
  ]
}}
```

Respond ONLY with the JSON object."""


# Prompt for transcript requirement extraction
TRANSCRIPT_EXTRACTION_PROMPT = """Extract requirements from this meeting transcript.

## Transcript
{transcript}

## Meeting Context
- Title: {meeting_title}
- Date: {meeting_date}
- Participants: {participants}

## Instructions

Analyze the transcript and extract:
1. Explicit requirements mentioned
2. Implied requirements from discussions
3. Decisions made
4. Action items related to requirements
5. Constraints or rules mentioned

Consolidate related statements into coherent requirements.

Respond with a JSON object:

```json
{{
  "extracted_requirements": [
    {{
      "id": "REQ-001",
      "title": "short title",
      "description": "consolidated description from transcript",
      "mentioned_by": ["speakers who mentioned this"],
      "related_quotes": ["relevant quotes from transcript"],
      "confidence": <0.0-1.0>
    }}
  ],
  "decisions": [
    {{
      "id": "DEC-001",
      "decision": "what was decided",
      "made_by": "speaker",
      "context": "surrounding discussion"
    }}
  ],
  "action_items": [
    {{
      "id": "ACT-001",
      "action": "what needs to be done",
      "assignee": "who is responsible",
      "related_requirement": "REQ-001 or null"
    }}
  ]
}}
```

Respond ONLY with the JSON object."""


def build_analysis_prompt(
    title: str,
    description: str,
    acceptance_criteria: list[str],
    context: str = "",
) -> str:
    """
    Build the comprehensive analysis prompt.

    Args:
        title: Requirement title
        description: Requirement description
        acceptance_criteria: List of existing acceptance criteria
        context: Additional context

    Returns:
        Formatted prompt string
    """
    ac_text = "\n".join(f"- {ac}" for ac in acceptance_criteria) if acceptance_criteria else "None provided"

    return COMPREHENSIVE_ANALYSIS_PROMPT.format(
        title=title,
        description=description,
        acceptance_criteria=ac_text,
        context=context or "None provided",
    )


def build_structure_prompt(requirement_text: str) -> str:
    """Build the structure extraction prompt."""
    return STRUCTURE_EXTRACTION_PROMPT.format(requirement_text=requirement_text)


def build_gap_detection_prompt(
    title: str,
    description: str,
    acceptance_criteria: list[str],
) -> str:
    """Build the gap detection prompt."""
    ac_text = "\n".join(f"- {ac}" for ac in acceptance_criteria) if acceptance_criteria else "None provided"

    return GAP_DETECTION_PROMPT.format(
        title=title,
        description=description,
        acceptance_criteria=ac_text,
    )


def build_ac_generation_prompt(
    title: str,
    description: str,
    existing_acs: list[str],
    gaps: list[dict],
) -> str:
    """Build the AC generation prompt."""
    ac_text = "\n".join(f"- {ac}" for ac in existing_acs) if existing_acs else "None"
    gaps_text = "\n".join(f"- {g.get('id', 'GAP')}: {g.get('description', '')}" for g in gaps) if gaps else "None identified"

    return AC_GENERATION_PROMPT.format(
        title=title,
        description=description,
        existing_acs=ac_text,
        gaps=gaps_text,
    )


def build_question_generation_prompt(
    title: str,
    description: str,
    gaps: list[dict],
) -> str:
    """Build the question generation prompt."""
    gaps_text = "\n".join(f"- {g.get('id', 'GAP')}: {g.get('description', '')}" for g in gaps) if gaps else "None identified"

    return QUESTION_GENERATION_PROMPT.format(
        title=title,
        description=description,
        gaps=gaps_text,
    )


def build_transcript_prompt(
    transcript: str,
    meeting_title: str = "",
    meeting_date: str = "",
    participants: list[str] | None = None,
) -> str:
    """Build the transcript extraction prompt."""
    return TRANSCRIPT_EXTRACTION_PROMPT.format(
        transcript=transcript,
        meeting_title=meeting_title or "Unknown",
        meeting_date=meeting_date or "Unknown",
        participants=", ".join(participants) if participants else "Unknown",
    )
