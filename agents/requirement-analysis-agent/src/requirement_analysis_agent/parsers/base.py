"""Base parser interface for requirement inputs."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from requirement_analysis_agent.models import (
    InputType,
    JiraStoryInput,
    FreeFormInput,
    TranscriptInput,
)

# Type variable for input types
T = TypeVar("T", JiraStoryInput, FreeFormInput, TranscriptInput)


class ParsedInput:
    """Normalized parsed input from any source."""

    def __init__(
        self,
        input_type: InputType,
        title: str,
        description: str,
        acceptance_criteria: list[str],
        context: str = "",
        metadata: dict | None = None,
    ):
        self.input_type = input_type
        self.title = title
        self.description = description
        self.acceptance_criteria = acceptance_criteria
        self.context = context
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "input_type": self.input_type.value,
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "context": self.context,
            "metadata": self.metadata,
        }


class BaseParser(ABC, Generic[T]):
    """Abstract base class for input parsers."""

    @property
    @abstractmethod
    def input_type(self) -> InputType:
        """Return the type of input this parser handles."""
        ...

    @abstractmethod
    def parse(self, input_data: T) -> ParsedInput:
        """
        Parse raw input into normalized format.

        Args:
            input_data: The typed input data

        Returns:
            ParsedInput with normalized content
        """
        ...

    @abstractmethod
    def validate(self, input_data: T) -> list[str]:
        """
        Validate input data before parsing.

        Args:
            input_data: The typed input data

        Returns:
            List of validation error messages (empty if valid)
        """
        ...

    def parse_if_valid(self, input_data: T) -> tuple[ParsedInput | None, list[str]]:
        """
        Validate and parse input data.

        Args:
            input_data: The typed input data

        Returns:
            Tuple of (parsed_input, errors). If errors, parsed_input is None.
        """
        errors = self.validate(input_data)
        if errors:
            return None, errors
        return self.parse(input_data), []
