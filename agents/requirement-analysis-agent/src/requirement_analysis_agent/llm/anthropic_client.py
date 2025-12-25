"""Anthropic Claude LLM client implementation."""

import asyncio
import time
from typing import Optional

import anthropic
from anthropic import AsyncAnthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from requirement_analysis_agent.llm.base import (
    GenerationConfig,
    LLMAPIError,
    LLMAuthenticationError,
    LLMProvider,
    LLMRateLimitError,
    LLMResponse,
    LLMTimeoutError,
    Message,
    MessageRole,
)
from requirement_analysis_agent.utils.logging import (
    get_logger,
    log_llm_error,
    log_llm_request,
    log_llm_response,
)


class AnthropicClient(LLMProvider):
    """Anthropic Claude LLM client for requirement analysis."""

    # Supported models with context windows
    MODELS = {
        "claude-sonnet-4-20250514": 200000,  # Claude Sonnet 4 - default
        "claude-3-5-sonnet-20241022": 200000,  # Claude 3.5 Sonnet
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
        "claude-3-5-haiku-20241022": 200000,
    }

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            default_model: Default model to use (defaults to Claude Sonnet 4)
        """
        super().__init__(api_key, default_model or self.DEFAULT_MODEL)
        self.logger = get_logger(__name__)

    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        try:
            self._client = AsyncAnthropic(api_key=self.api_key)
            self.logger.info("Anthropic client initialized", model=self.default_model)
        except Exception as e:
            self.logger.error("Failed to initialize Anthropic client", error=str(e))
            raise LLMAPIError(
                f"Failed to initialize Anthropic client: {e}",
                provider=self.provider_name,
            )

    @retry(
        retry=retry_if_exception_type(LLMRateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def generate(
        self,
        messages: list[Message],
        config: Optional[GenerationConfig] = None,
    ) -> LLMResponse:
        """
        Generate a response using Claude.

        Args:
            messages: List of messages in the conversation
            config: Generation configuration

        Returns:
            LLMResponse with generated content
        """
        if not self._client:
            await self.initialize()

        config = self.validate_config(config)
        start_time = time.time()

        # Extract system message if present
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                chat_messages.append({
                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                    "content": msg.content,
                })

        try:
            # Log request
            prompt_text = " ".join([m.content for m in messages])
            log_llm_request(
                provider=self.provider_name,
                model=config.model or self.DEFAULT_MODEL,
                prompt_tokens=self.estimate_tokens(prompt_text),
            )

            # Build API call kwargs, only including optional params if set
            api_kwargs = {
                "model": config.model or self.DEFAULT_MODEL,
                "messages": chat_messages,
                "max_tokens": config.max_tokens or 8192,  # Higher for analysis output
                "timeout": config.timeout or 120,  # Higher timeout for complex analysis
            }

            # Only add optional parameters if they have values
            if config.temperature is not None:
                api_kwargs["temperature"] = config.temperature
            if config.top_p is not None:
                api_kwargs["top_p"] = config.top_p
            if config.top_k is not None:
                api_kwargs["top_k"] = config.top_k
            if system_message:
                api_kwargs["system"] = system_message
            if config.stop_sequences:
                api_kwargs["stop_sequences"] = config.stop_sequences

            # Make API call
            response = await self._client.messages.create(**api_kwargs)

            duration_ms = (time.time() - start_time) * 1000

            # Log response
            log_llm_response(
                provider=self.provider_name,
                model=config.model or self.DEFAULT_MODEL,
                completion_tokens=response.usage.output_tokens,
                duration_ms=duration_ms,
            )

            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                provider=self.provider_name,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                metadata={
                    "message_id": response.id,
                    "stop_sequence": response.stop_sequence,
                    "duration_ms": duration_ms,
                },
            )

        except anthropic.RateLimitError as e:
            log_llm_error(self.provider_name, config.model or self.DEFAULT_MODEL, e)
            raise LLMRateLimitError(
                str(e),
                provider=self.provider_name,
                status_code=429,
            )
        except anthropic.AuthenticationError as e:
            log_llm_error(self.provider_name, config.model or self.DEFAULT_MODEL, e)
            raise LLMAuthenticationError(
                str(e),
                provider=self.provider_name,
                status_code=401,
            )
        except asyncio.TimeoutError as e:
            log_llm_error(self.provider_name, config.model or self.DEFAULT_MODEL, e)
            raise LLMTimeoutError(f"Request timed out: {e}")
        except Exception as e:
            log_llm_error(self.provider_name, config.model or self.DEFAULT_MODEL, e)
            raise LLMAPIError(
                f"Anthropic API error: {e}",
                provider=self.provider_name,
            )

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
        messages = [Message(role=MessageRole.USER, content=prompt)]
        return await self.generate(messages, config)

    async def generate_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> LLMResponse:
        """
        Generate text with system and user prompts.

        Args:
            system_prompt: System instructions
            user_prompt: User message
            config: Generation configuration

        Returns:
            LLMResponse with generated content
        """
        messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompt),
            Message(role=MessageRole.USER, content=user_prompt),
        ]
        return await self.generate(messages, config)

    def is_available(self) -> bool:
        """Check if Anthropic client is available."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def get_supported_models(self) -> list[str]:
        """Get list of supported Claude models."""
        return list(self.MODELS.keys())

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Claude uses a similar tokenization to GPT models.
        Rough estimate: 1 token ≈ 4 characters.
        """
        return len(text) // 4

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"

    def get_model_context_window(self, model: Optional[str] = None) -> int:
        """Get the context window size for a model."""
        model = model or self.default_model
        return self.MODELS.get(model, 200000)
