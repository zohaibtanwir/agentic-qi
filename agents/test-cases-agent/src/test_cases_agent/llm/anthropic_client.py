"""Anthropic Claude LLM client implementation."""

import asyncio
from typing import Dict, List, Optional

import anthropic
from anthropic import AsyncAnthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from test_cases_agent.llm.base import (
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
from test_cases_agent.utils.logging import get_logger, log_llm_error, log_llm_request, log_llm_response


class AnthropicClient(LLMProvider):
    """Anthropic Claude LLM client."""

    # Supported models
    MODELS = {
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-5-haiku-20241022": 200000,
    }

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            default_model: Default model to use
        """
        super().__init__(api_key, default_model or self.DEFAULT_MODEL)
        self.logger = get_logger(__name__)

    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        try:
            self._client = AsyncAnthropic(api_key=self.api_key)
            self.logger.info("Anthropic client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic client: {e}")
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
        messages: List[Message],
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

        # Extract system message if present
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                chat_messages.append({
                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                    "content": msg.content
                })

        try:
            # Log request
            log_llm_request(
                provider=self.provider_name,
                model=config.model,
                prompt_tokens=self.estimate_tokens(
                    " ".join([m.content for m in messages])
                ),
            )

            # Make API call
            response = await self._client.messages.create(
                model=config.model,
                messages=chat_messages,
                max_tokens=config.max_tokens or 4096,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                system=system_message,
                stop_sequences=config.stop_sequences,
                timeout=config.timeout or 60,
            )

            # Log response
            log_llm_response(
                provider=self.provider_name,
                model=config.model,
                completion_tokens=response.usage.output_tokens,
                duration_ms=0,  # TODO: Track actual duration
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
                },
            )

        except anthropic.RateLimitError as e:
            log_llm_error(self.provider_name, config.model, e)
            raise LLMRateLimitError(
                str(e),
                provider=self.provider_name,
                status_code=429,
            )
        except anthropic.AuthenticationError as e:
            log_llm_error(self.provider_name, config.model, e)
            raise LLMAuthenticationError(
                str(e),
                provider=self.provider_name,
                status_code=401,
            )
        except asyncio.TimeoutError as e:
            log_llm_error(self.provider_name, config.model, e)
            raise LLMTimeoutError(f"Request timed out: {e}")
        except Exception as e:
            log_llm_error(self.provider_name, config.model, e)
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

    def is_available(self) -> bool:
        """Check if Anthropic client is available."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def get_supported_models(self) -> List[str]:
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

    def get_model_context_window(self, model: str) -> int:
        """Get the context window size for a model."""
        return self.MODELS.get(model, 200000)