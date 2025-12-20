"""OpenAI GPT LLM client implementation."""

import asyncio
from typing import List, Optional

import openai
from openai import AsyncOpenAI
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
)
from test_cases_agent.utils.logging import get_logger, log_llm_error, log_llm_request, log_llm_response


class OpenAIClient(LLMProvider):
    """OpenAI GPT LLM client."""

    # Supported models with context windows
    MODELS = {
        "gpt-4-turbo-preview": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-3.5-turbo": 16385,
        "gpt-3.5-turbo-16k": 16385,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
    }

    DEFAULT_MODEL = "gpt-4-turbo-preview"

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            default_model: Default model to use
        """
        super().__init__(api_key, default_model or self.DEFAULT_MODEL)
        self.logger = get_logger(__name__)

    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            self._client = AsyncOpenAI(api_key=self.api_key)
            self.logger.info("OpenAI client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise LLMAPIError(
                f"Failed to initialize OpenAI client: {e}",
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
        Generate a response using GPT.

        Args:
            messages: List of messages in the conversation
            config: Generation configuration

        Returns:
            LLMResponse with generated content
        """
        if not self._client:
            await self.initialize()

        config = self.validate_config(config)

        try:
            # Format messages
            formatted_messages = self.format_messages(messages)

            # Log request
            log_llm_request(
                provider=self.provider_name,
                model=config.model,
                prompt_tokens=self.estimate_tokens(
                    " ".join([m.content for m in messages])
                ),
            )

            # Make API call
            response = await self._client.chat.completions.create(
                model=config.model,
                messages=formatted_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop_sequences,
                stream=False,
                timeout=config.timeout or 60,
            )

            # Log response
            log_llm_response(
                provider=self.provider_name,
                model=config.model,
                completion_tokens=response.usage.completion_tokens,
                duration_ms=0,  # TODO: Track actual duration
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider=self.provider_name,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "message_id": response.id,
                    "created": response.created,
                },
            )

        except openai.RateLimitError as e:
            log_llm_error(self.provider_name, config.model, e)
            raise LLMRateLimitError(
                str(e),
                provider=self.provider_name,
                status_code=429,
            )
        except openai.AuthenticationError as e:
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
                f"OpenAI API error: {e}",
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
        messages = [Message(role="user", content=prompt)]
        return await self.generate(messages, config)

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def get_supported_models(self) -> List[str]:
        """Get list of supported GPT models."""
        return list(self.MODELS.keys())

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        OpenAI uses tiktoken for tokenization.
        Rough estimate: 1 token ≈ 4 characters.
        """
        # For a more accurate count, you could use tiktoken library
        return len(text) // 4

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openai"

    def get_model_context_window(self, model: str) -> int:
        """Get the context window size for a model."""
        return self.MODELS.get(model, 8192)