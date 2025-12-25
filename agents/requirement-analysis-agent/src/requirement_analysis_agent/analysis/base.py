"""Base classes for analysis components."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Optional

from requirement_analysis_agent.llm.base import LLMProvider, GenerationConfig
from requirement_analysis_agent.utils.logging import get_logger


class AnalyzerError(Exception):
    """Base exception for analyzer errors."""
    pass


class LLMParsingError(AnalyzerError):
    """Error parsing LLM response."""
    pass


class BaseAnalyzer(ABC):
    """Base class for all analyzers."""

    def __init__(self, llm_client: LLMProvider):
        """
        Initialize analyzer.

        Args:
            llm_client: LLM client for generating analysis
        """
        self.llm_client = llm_client
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def analyze(self, *args: Any, **kwargs: Any) -> Any:
        """Perform analysis. Subclasses must implement."""
        pass

    def _parse_json_response(self, response_text: str) -> dict:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed JSON as dictionary

        Raises:
            LLMParsingError: If JSON cannot be parsed
        """
        text = response_text.strip()

        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # Raw JSON object
        ]

        for pattern in json_patterns:
            match = re.search(pattern, text)
            if match:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                try:
                    return json.loads(json_str.strip())
                except json.JSONDecodeError:
                    continue

        # Last resort: try parsing the entire response
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            self.logger.error(
                "Failed to parse JSON from LLM response",
                error=str(e),
                response_preview=text[:500],
            )
            raise LLMParsingError(f"Failed to parse JSON: {e}")

    def _get_generation_config(self, temperature: float = 0.3) -> GenerationConfig:
        """Get default generation config for analysis."""
        return GenerationConfig(
            temperature=temperature,
            max_tokens=8192,
            top_p=0.95,
        )

    def _validate_required_fields(self, data: dict, required_fields: list[str]) -> None:
        """
        Validate that required fields are present in parsed data.

        Args:
            data: Parsed data dictionary
            required_fields: List of required field names

        Raises:
            LLMParsingError: If required fields are missing
        """
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise LLMParsingError(f"Missing required fields: {missing}")
