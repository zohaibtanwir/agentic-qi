"""Simplified Anthropic Claude LLM client implementation - Direct without retry logic."""

import asyncio
from typing import List, Optional

from anthropic import AsyncAnthropic

from test_cases_agent.llm.base import (
    GenerationConfig,
    LLMAPIError,
    LLMAuthenticationError,
    LLMProvider,
    LLMResponse,
    Message,
    MessageRole,
)
from test_cases_agent.utils.logging import get_logger


class SimpleAnthropicClient(LLMProvider):
    """Simplified Anthropic Claude LLM client without retry logic."""

    # Supported models - using haiku which should work
    MODELS = {
        "claude-3-haiku-20240307": 200000,
    }

    DEFAULT_MODEL = "claude-3-haiku-20240307"  # Using haiku model

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            default_model: Default model to use
        """
        super().__init__(api_key, default_model or self.DEFAULT_MODEL)
        self.logger = get_logger(__name__)
        self._client = None

    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        try:
            self._client = AsyncAnthropic(api_key=self.api_key)
            self.logger.info(f"Simple Anthropic client initialized with key: {self.api_key[:10]}...")
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic client: {e}")
            raise LLMAPIError(
                f"Failed to initialize Anthropic client: {e}",
                provider=self.provider_name,
            )

    async def generate(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None,
    ) -> LLMResponse:
        """
        Generate a response using Claude without retry logic.

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
            if msg.role == MessageRole.SYSTEM or msg.role == "system":
                system_message = msg.content
            else:
                # Convert to Anthropic format
                role = "user" if msg.role in [MessageRole.USER, "user"] else "assistant"
                chat_messages.append({
                    "role": role,
                    "content": msg.content
                })

        # Ensure messages alternate between user and assistant
        if not chat_messages:
            chat_messages = [{"role": "user", "content": "Generate test cases"}]

        self.logger.info(f"Sending request to Anthropic with {len(chat_messages)} messages")
        self.logger.debug(f"System message: {system_message[:100] if system_message else 'None'}...")
        self.logger.debug(f"Messages: {chat_messages}")

        try:
            # Make API call directly without retry
            response = await self._client.messages.create(
                model=config.model or self.DEFAULT_MODEL,
                messages=chat_messages,
                max_tokens=config.max_tokens or 4096,
                temperature=config.temperature if config.temperature is not None else 0.7,
                system=system_message if system_message else None,
            )

            self.logger.info(f"Successfully received response from Anthropic")

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
                },
            )

        except Exception as e:
            self.logger.error(f"Anthropic API error (direct): {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")

            # Check if it's an authentication error
            if "401" in str(e) or "authentication" in str(e).lower():
                raise LLMAuthenticationError(
                    f"Authentication failed: {e}",
                    provider=self.provider_name,
                    status_code=401,
                )

            # Re-raise as generic API error
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

    async def close(self) -> None:
        """Close the client."""
        if self._client:
            await self._client.close()
            self._client = None