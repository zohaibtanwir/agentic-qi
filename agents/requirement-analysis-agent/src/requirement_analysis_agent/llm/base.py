"""Base interface for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class MessageRole(str, Enum):
    """Message roles for chat completions."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Chat message."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Response from LLM provider."""

    content: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class GenerationConfig:
    """Configuration for text generation."""

    model: Optional[str] = None
    temperature: float = 0.3  # Lower for more deterministic analysis
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    top_k: Optional[int] = None
    stop_sequences: Optional[list[str]] = None
    timeout: Optional[int] = None
    retry_attempts: int = 3
    metadata: Optional[dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for the provider
            default_model: Default model to use if not specified
        """
        self.api_key = api_key
        self.default_model = default_model
        self._client: Optional[Any] = None
        self._total_tokens_used: int = 0

    def get_total_tokens(self) -> int:
        """Get total tokens used across all requests."""
        return self._total_tokens_used

    def reset_token_count(self) -> int:
        """Reset token count and return the previous value."""
        tokens = self._total_tokens_used
        self._total_tokens_used = 0
        return tokens

    def _track_tokens(self, tokens: int) -> None:
        """Add tokens to the running total."""
        self._total_tokens_used += tokens

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider client."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        config: Optional[GenerationConfig] = None,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: List of messages in the conversation
            config: Generation configuration

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> LLMResponse:
        """
        Generate text from a simple prompt.

        Args:
            prompt: Text prompt
            config: Generation configuration

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.

        Returns:
            True if provider is available, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_models(self) -> list[str]:
        """
        Get list of supported models for this provider.

        Returns:
            List of model names
        """
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            Provider name string
        """
        pass

    def validate_config(self, config: Optional[GenerationConfig]) -> GenerationConfig:
        """
        Validate and set defaults for generation config.

        Args:
            config: Generation configuration

        Returns:
            Validated configuration with defaults
        """
        if config is None:
            config = GenerationConfig()

        # Set default model if not specified
        if config.model is None:
            config.model = self.default_model

        # Validate temperature
        if not 0.0 <= config.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        # Validate top_p
        if not 0.0 <= config.top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")

        return config

    def format_messages(self, messages: list[Message]) -> list[dict[str, str]]:
        """
        Format messages for API calls.

        Args:
            messages: List of Message objects

        Returns:
            List of formatted message dictionaries
        """
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
            }
            for msg in messages
        ]

    async def close(self) -> None:
        """Close the provider client and cleanup resources."""
        if self._client:
            if hasattr(self._client, "close"):
                await self._client.close()
            self._client = None


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    pass


class LLMAPIError(LLMError):
    """API-related errors from LLM providers."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        response: Optional[str] = None,
    ):
        """Initialize API error."""
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.response = response


class LLMRateLimitError(LLMAPIError):
    """Rate limit exceeded error."""

    pass


class LLMAuthenticationError(LLMAPIError):
    """Authentication error."""

    pass


class LLMTimeoutError(LLMError):
    """Request timeout error."""

    pass


class LLMValidationError(LLMError):
    """Input validation error."""

    pass


__all__ = [
    "LLMProvider",
    "Message",
    "MessageRole",
    "LLMResponse",
    "GenerationConfig",
    "LLMError",
    "LLMAPIError",
    "LLMRateLimitError",
    "LLMAuthenticationError",
    "LLMTimeoutError",
    "LLMValidationError",
]
