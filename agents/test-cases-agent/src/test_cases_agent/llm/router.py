"""LLM Router for selecting and managing LLM providers."""

from enum import Enum
from typing import Dict, List, Optional

from test_cases_agent.config import LLMProvider as ConfigProvider, get_settings
from test_cases_agent.llm.anthropic_client import AnthropicClient
from test_cases_agent.llm.base import (
    GenerationConfig,
    LLMError,
    LLMProvider,
    LLMResponse,
    Message,
)
from test_cases_agent.llm.gemini_client import GeminiClient
from test_cases_agent.llm.openai_client import OpenAIClient
from test_cases_agent.utils.logging import get_logger


class LLMProviderType(str, Enum):
    """LLM provider types."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMRouter:
    """
    Router for managing multiple LLM providers.

    Handles provider selection, failover, and load balancing.
    """

    def __init__(self):
        """Initialize the LLM router."""
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.providers: Dict[LLMProviderType, LLMProvider] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all configured LLM providers."""
        if self._initialized:
            return

        # Initialize Anthropic if configured
        if self.settings.has_anthropic:
            try:
                client = AnthropicClient(self.settings.anthropic_api_key)
                await client.initialize()
                self.providers[LLMProviderType.ANTHROPIC] = client
                self.logger.info("Anthropic provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Anthropic provider: {e}")

        # Initialize OpenAI if configured
        if self.settings.has_openai:
            try:
                client = OpenAIClient(self.settings.openai_api_key)
                await client.initialize()
                self.providers[LLMProviderType.OPENAI] = client
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI provider: {e}")

        # Initialize Gemini if configured
        if self.settings.has_gemini:
            try:
                client = GeminiClient(self.settings.gemini_api_key)
                await client.initialize()
                self.providers[LLMProviderType.GEMINI] = client
                self.logger.info("Gemini provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini provider: {e}")

        if not self.providers:
            raise LLMError("No LLM providers configured. Please set API keys in .env")

        self._initialized = True
        self.logger.info(
            f"LLM Router initialized with {len(self.providers)} provider(s): "
            f"{', '.join([p.value for p in self.providers.keys()])}"
        )

    async def generate(
        self,
        messages: List[Message],
        provider: Optional[LLMProviderType] = None,
        config: Optional[GenerationConfig] = None,
        fallback: bool = True,
    ) -> LLMResponse:
        """
        Generate a response using the specified or default provider.

        Args:
            messages: List of messages in the conversation
            provider: Specific provider to use (optional)
            config: Generation configuration
            fallback: Whether to try other providers on failure

        Returns:
            LLMResponse with generated content

        Raises:
            LLMError: If generation fails with all providers
        """
        if not self._initialized:
            await self.initialize()

        # Determine provider to use
        if provider:
            primary_provider = provider
        else:
            # Use default from settings
            primary_provider = LLMProviderType(self.settings.default_llm_provider.value)

        # Get ordered list of providers to try
        providers_to_try = self._get_provider_order(primary_provider, fallback)

        last_error = None
        for provider_type in providers_to_try:
            if provider_type not in self.providers:
                continue

            provider_client = self.providers[provider_type]

            try:
                self.logger.info(
                    f"Attempting generation with {provider_type.value} provider"
                )
                response = await provider_client.generate(messages, config)
                self.logger.info(
                    f"Successfully generated response with {provider_type.value}"
                )
                return response

            except Exception as e:
                last_error = e
                self.logger.error(
                    f"Failed to generate with {provider_type.value}: {e}"
                )

                if not fallback:
                    raise

                continue

        # All providers failed
        raise LLMError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    async def generate_text(
        self,
        prompt: str,
        provider: Optional[LLMProviderType] = None,
        config: Optional[GenerationConfig] = None,
        fallback: bool = True,
    ) -> LLMResponse:
        """
        Generate text from a simple prompt.

        Args:
            prompt: Text prompt
            provider: Specific provider to use (optional)
            config: Generation configuration
            fallback: Whether to try other providers on failure

        Returns:
            LLMResponse with generated content
        """
        messages = [Message(role="user", content=prompt)]
        return await self.generate(messages, provider, config, fallback)

    def _get_provider_order(
        self,
        primary: LLMProviderType,
        fallback: bool,
    ) -> List[LLMProviderType]:
        """
        Get ordered list of providers to try.

        Args:
            primary: Primary provider to use
            fallback: Whether to include fallback providers

        Returns:
            Ordered list of provider types
        """
        providers = [primary]

        if fallback:
            # Add other configured providers as fallbacks
            for provider_type in LLMProviderType:
                if provider_type != primary and provider_type in self.providers:
                    providers.append(provider_type)

        return providers

    def get_available_providers(self) -> List[LLMProviderType]:
        """Get list of available providers."""
        return list(self.providers.keys())

    def get_provider(self, provider_type: LLMProviderType) -> Optional[LLMProvider]:
        """
        Get a specific provider client.

        Args:
            provider_type: Type of provider to get

        Returns:
            Provider client or None if not available
        """
        return self.providers.get(provider_type)

    def is_provider_available(self, provider_type: LLMProviderType) -> bool:
        """
        Check if a specific provider is available.

        Args:
            provider_type: Type of provider to check

        Returns:
            True if provider is available
        """
        return provider_type in self.providers

    def get_supported_models(
        self,
        provider_type: Optional[LLMProviderType] = None,
    ) -> Dict[str, List[str]]:
        """
        Get supported models for all or specific provider.

        Args:
            provider_type: Specific provider (optional)

        Returns:
            Dictionary of provider -> models
        """
        models = {}

        if provider_type:
            if provider_type in self.providers:
                models[provider_type.value] = (
                    self.providers[provider_type].get_supported_models()
                )
        else:
            for ptype, provider in self.providers.items():
                models[ptype.value] = provider.get_supported_models()

        return models

    async def close(self) -> None:
        """Close all provider clients."""
        for provider in self.providers.values():
            await provider.close()
        self.providers.clear()
        self._initialized = False
        self.logger.info("LLM Router closed")


# Singleton instance
_router_instance: Optional[LLMRouter] = None


def get_llm_router() -> LLMRouter:
    """
    Get the singleton LLM router instance.

    Returns:
        LLMRouter instance
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance


__all__ = [
    "LLMRouter",
    "LLMProviderType",
    "get_llm_router",
]