"""LLM integration for requirement analysis."""

from .base import (
    LLMProvider,
    Message,
    MessageRole,
    LLMResponse,
    GenerationConfig,
    LLMError,
    LLMAPIError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMTimeoutError,
    LLMValidationError,
)
from .anthropic_client import AnthropicClient
from .prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    COMPREHENSIVE_ANALYSIS_PROMPT,
    build_analysis_prompt,
    build_structure_prompt,
    build_gap_detection_prompt,
    build_ac_generation_prompt,
    build_question_generation_prompt,
    build_transcript_prompt,
)

__all__ = [
    # Base classes
    "LLMProvider",
    "Message",
    "MessageRole",
    "LLMResponse",
    "GenerationConfig",
    # Errors
    "LLMError",
    "LLMAPIError",
    "LLMRateLimitError",
    "LLMAuthenticationError",
    "LLMTimeoutError",
    "LLMValidationError",
    # Clients
    "AnthropicClient",
    # Prompts
    "ANALYSIS_SYSTEM_PROMPT",
    "COMPREHENSIVE_ANALYSIS_PROMPT",
    "build_analysis_prompt",
    "build_structure_prompt",
    "build_gap_detection_prompt",
    "build_ac_generation_prompt",
    "build_question_generation_prompt",
    "build_transcript_prompt",
]
