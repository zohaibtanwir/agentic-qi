"""Google Gemini LLM client implementation."""

import asyncio
from typing import List, Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig as GeminiConfig
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


class GeminiClient(LLMProvider):
    """Google Gemini LLM client."""

    # Supported models with context windows
    MODELS = {
        "gemini-pro": 30720,
        "gemini-pro-vision": 30720,
        "gemini-1.5-pro": 1048576,
        "gemini-1.5-flash": 1048576,
    }

    DEFAULT_MODEL = "gemini-1.5-pro"

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Google AI API key
            default_model: Default model to use
        """
        super().__init__(api_key, default_model or self.DEFAULT_MODEL)
        self.logger = get_logger(__name__)

    async def initialize(self) -> None:
        """Initialize the Gemini client."""
        try:
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.default_model)
            self.logger.info("Gemini client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise LLMAPIError(
                f"Failed to initialize Gemini client: {e}",
                provider=self.provider_name,
            )

    def _convert_messages_to_gemini_format(self, messages: List[Message]) -> List[dict]:
        """
        Convert messages to Gemini chat format.

        Args:
            messages: List of Message objects

        Returns:
            List of Gemini-formatted messages
        """
        gemini_messages = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # Gemini doesn't have a system role, prepend to first user message
                continue

            role = "user" if msg.role == MessageRole.USER else "model"

            # Handle system message by prepending to first user message
            content = msg.content
            if msg.role == MessageRole.USER and not gemini_messages:
                # Check if there's a system message before this
                system_msgs = [m for m in messages if m.role == MessageRole.SYSTEM]
                if system_msgs:
                    content = f"{system_msgs[0].content}\n\n{content}"

            gemini_messages.append({
                "role": role,
                "parts": [content]
            })

        return gemini_messages

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
        Generate a response using Gemini.

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
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)

            # Log request
            log_llm_request(
                provider=self.provider_name,
                model=config.model or self.default_model,
                prompt_tokens=self.estimate_tokens(
                    " ".join([m.content for m in messages])
                ),
            )

            # Create model with specific configuration
            model = genai.GenerativeModel(config.model or self.default_model)

            # Create generation config
            gemini_config = GeminiConfig(
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                max_output_tokens=config.max_tokens,
                stop_sequences=config.stop_sequences,
            )

            # Start chat and send message
            chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

            # Send the last message
            last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""

            # Use asyncio to run the sync method
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: chat.send_message(
                    last_message,
                    generation_config=gemini_config,
                )
            )

            # Count tokens (Gemini provides this in response metadata)
            prompt_tokens = self.estimate_tokens(" ".join([m.content for m in messages]))
            completion_tokens = self.estimate_tokens(response.text)

            # Log response
            log_llm_response(
                provider=self.provider_name,
                model=config.model or self.default_model,
                completion_tokens=completion_tokens,
                duration_ms=0,  # TODO: Track actual duration
            )

            return LLMResponse(
                content=response.text,
                model=config.model or self.default_model,
                provider=self.provider_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                finish_reason="stop",
                metadata={
                    "safety_ratings": [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name,
                        }
                        for rating in response.prompt_feedback.safety_ratings
                    ]
                    if hasattr(response, "prompt_feedback") and response.prompt_feedback
                    else None,
                },
            )

        except Exception as e:
            error_str = str(e)

            if "quota" in error_str.lower() or "rate" in error_str.lower():
                log_llm_error(self.provider_name, config.model or self.default_model, e)
                raise LLMRateLimitError(
                    error_str,
                    provider=self.provider_name,
                    status_code=429,
                )
            elif "api key" in error_str.lower() or "auth" in error_str.lower():
                log_llm_error(self.provider_name, config.model or self.default_model, e)
                raise LLMAuthenticationError(
                    error_str,
                    provider=self.provider_name,
                    status_code=401,
                )
            elif "timeout" in error_str.lower():
                log_llm_error(self.provider_name, config.model or self.default_model, e)
                raise LLMTimeoutError(f"Request timed out: {e}")
            else:
                log_llm_error(self.provider_name, config.model or self.default_model, e)
                raise LLMAPIError(
                    f"Gemini API error: {e}",
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
        """Check if Gemini client is available."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def get_supported_models(self) -> List[str]:
        """Get list of supported Gemini models."""
        return list(self.MODELS.keys())

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Gemini uses a similar tokenization approach.
        Rough estimate: 1 token ≈ 4 characters.
        """
        return len(text) // 4

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "gemini"

    def get_model_context_window(self, model: str) -> int:
        """Get the context window size for a model."""
        return self.MODELS.get(model, 30720)