"""Unit tests for LLM router."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from test_cases_agent.llm import (
    GenerationConfig,
    LLMError,
    LLMResponse,
    LLMRouter,
    LLMProviderType,
    Message,
    MessageRole,
    get_llm_router,
)


class TestLLMRouter:
    """Test LLM Router."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings."""
        settings = MagicMock()
        settings.has_anthropic = True
        settings.has_openai = True
        settings.has_gemini = False
        settings.anthropic_api_key = "test-anthropic-key"
        settings.openai_api_key = "test-openai-key"
        settings.default_llm_provider = MagicMock(value="anthropic")
        return settings

    @pytest.fixture
    async def router(self, mock_settings):
        """Create router with mock settings."""
        with patch("test_cases_agent.llm.router.get_settings", return_value=mock_settings):
            router = LLMRouter()
            # Mock the providers
            router.providers = {}
            return router

    @pytest.mark.asyncio
    async def test_router_initialization(self, mock_settings):
        """Test router initialization."""
        with patch("test_cases_agent.llm.router.get_settings", return_value=mock_settings):
            router = LLMRouter()
            assert router.settings == mock_settings
            assert router.providers == {}
            assert router._initialized is False

    @pytest.mark.asyncio
    async def test_initialize_providers(self, mock_settings):
        """Test initializing providers."""
        with patch("test_cases_agent.llm.router.get_settings", return_value=mock_settings):
            with patch("test_cases_agent.llm.router.AnthropicClient") as MockAnthropic:
                with patch("test_cases_agent.llm.router.OpenAIClient") as MockOpenAI:
                    # Setup mocks
                    mock_anthropic = AsyncMock()
                    mock_openai = AsyncMock()
                    MockAnthropic.return_value = mock_anthropic
                    MockOpenAI.return_value = mock_openai

                    # Initialize router
                    router = LLMRouter()
                    await router.initialize()

                    # Check providers were initialized
                    assert router._initialized is True
                    assert LLMProviderType.ANTHROPIC in router.providers
                    assert LLMProviderType.OPENAI in router.providers
                    assert LLMProviderType.GEMINI not in router.providers

                    # Check initialize was called
                    mock_anthropic.initialize.assert_called_once()
                    mock_openai.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_no_providers(self):
        """Test initialization with no providers configured."""
        settings = MagicMock()
        settings.has_anthropic = False
        settings.has_openai = False
        settings.has_gemini = False

        with patch("test_cases_agent.llm.router.get_settings", return_value=settings):
            router = LLMRouter()
            with pytest.raises(LLMError, match="No LLM providers configured"):
                await router.initialize()

    @pytest.mark.asyncio
    async def test_generate_with_specific_provider(self, router):
        """Test generation with specific provider."""
        # Setup mock provider
        mock_provider = AsyncMock()
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="anthropic",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        mock_provider.generate.return_value = mock_response
        router.providers[LLMProviderType.ANTHROPIC] = mock_provider
        router._initialized = True

        # Generate
        messages = [Message(role=MessageRole.USER, content="Test")]
        response = await router.generate(
            messages,
            provider=LLMProviderType.ANTHROPIC,
        )

        assert response == mock_response
        mock_provider.generate.assert_called_once_with(messages, None)

    @pytest.mark.asyncio
    async def test_generate_with_fallback(self, router):
        """Test generation with fallback to another provider."""
        # Setup mock providers
        mock_anthropic = AsyncMock()
        mock_openai = AsyncMock()

        # Anthropic fails, OpenAI succeeds
        mock_anthropic.generate.side_effect = Exception("Anthropic failed")
        mock_response = LLMResponse(
            content="OpenAI response",
            model="gpt-4",
            provider="openai",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        mock_openai.generate.return_value = mock_response

        router.providers[LLMProviderType.ANTHROPIC] = mock_anthropic
        router.providers[LLMProviderType.OPENAI] = mock_openai
        router._initialized = True

        # Generate with fallback
        messages = [Message(role=MessageRole.USER, content="Test")]
        response = await router.generate(
            messages,
            provider=LLMProviderType.ANTHROPIC,
            fallback=True,
        )

        assert response == mock_response
        mock_anthropic.generate.assert_called_once()
        mock_openai.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_no_fallback(self, router):
        """Test generation without fallback fails immediately."""
        # Setup mock provider that fails
        mock_provider = AsyncMock()
        mock_provider.generate.side_effect = Exception("Provider failed")
        router.providers[LLMProviderType.ANTHROPIC] = mock_provider
        router._initialized = True

        # Generate without fallback
        messages = [Message(role=MessageRole.USER, content="Test")]
        with pytest.raises(Exception, match="Provider failed"):
            await router.generate(
                messages,
                provider=LLMProviderType.ANTHROPIC,
                fallback=False,
            )

    @pytest.mark.asyncio
    async def test_generate_all_providers_fail(self, router):
        """Test when all providers fail."""
        # Setup mock providers that all fail
        mock_anthropic = AsyncMock()
        mock_openai = AsyncMock()
        mock_anthropic.generate.side_effect = Exception("Anthropic failed")
        mock_openai.generate.side_effect = Exception("OpenAI failed")

        router.providers[LLMProviderType.ANTHROPIC] = mock_anthropic
        router.providers[LLMProviderType.OPENAI] = mock_openai
        router._initialized = True

        # Generate with fallback
        messages = [Message(role=MessageRole.USER, content="Test")]
        with pytest.raises(LLMError, match="All LLM providers failed"):
            await router.generate(
                messages,
                provider=LLMProviderType.ANTHROPIC,
                fallback=True,
            )

    @pytest.mark.asyncio
    async def test_generate_text(self, router):
        """Test simple text generation."""
        # Setup mock provider
        mock_provider = AsyncMock()
        mock_response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="anthropic",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        mock_provider.generate.return_value = mock_response
        router.providers[LLMProviderType.ANTHROPIC] = mock_provider
        router._initialized = True

        # Generate text
        response = await router.generate_text(
            "Test prompt",
            provider=LLMProviderType.ANTHROPIC,
        )

        assert response == mock_response
        # Check that it was called with a Message
        call_args = mock_provider.generate.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0].role == MessageRole.USER
        assert call_args[0].content == "Test prompt"

    def test_get_provider_order(self, router):
        """Test getting provider order."""
        router.providers = {
            LLMProviderType.ANTHROPIC: MagicMock(),
            LLMProviderType.OPENAI: MagicMock(),
        }

        # With fallback
        order = router._get_provider_order(LLMProviderType.ANTHROPIC, fallback=True)
        assert order[0] == LLMProviderType.ANTHROPIC
        assert LLMProviderType.OPENAI in order

        # Without fallback
        order = router._get_provider_order(LLMProviderType.ANTHROPIC, fallback=False)
        assert order == [LLMProviderType.ANTHROPIC]

    def test_get_available_providers(self, router):
        """Test getting available providers."""
        router.providers = {
            LLMProviderType.ANTHROPIC: MagicMock(),
            LLMProviderType.OPENAI: MagicMock(),
        }

        providers = router.get_available_providers()
        assert LLMProviderType.ANTHROPIC in providers
        assert LLMProviderType.OPENAI in providers
        assert len(providers) == 2

    def test_get_provider(self, router):
        """Test getting specific provider."""
        mock_provider = MagicMock()
        router.providers[LLMProviderType.ANTHROPIC] = mock_provider

        provider = router.get_provider(LLMProviderType.ANTHROPIC)
        assert provider == mock_provider

        provider = router.get_provider(LLMProviderType.GEMINI)
        assert provider is None

    def test_is_provider_available(self, router):
        """Test checking provider availability."""
        router.providers[LLMProviderType.ANTHROPIC] = MagicMock()

        assert router.is_provider_available(LLMProviderType.ANTHROPIC) is True
        assert router.is_provider_available(LLMProviderType.GEMINI) is False

    def test_get_supported_models(self, router):
        """Test getting supported models."""
        mock_anthropic = MagicMock()
        mock_anthropic.get_supported_models.return_value = ["claude-3", "claude-2"]
        mock_openai = MagicMock()
        mock_openai.get_supported_models.return_value = ["gpt-4", "gpt-3.5"]

        router.providers[LLMProviderType.ANTHROPIC] = mock_anthropic
        router.providers[LLMProviderType.OPENAI] = mock_openai

        # Get all models
        models = router.get_supported_models()
        assert models["anthropic"] == ["claude-3", "claude-2"]
        assert models["openai"] == ["gpt-4", "gpt-3.5"]

        # Get specific provider models
        models = router.get_supported_models(LLMProviderType.ANTHROPIC)
        assert models == {"anthropic": ["claude-3", "claude-2"]}

    @pytest.mark.asyncio
    async def test_close(self, router):
        """Test closing router."""
        mock_anthropic = AsyncMock()
        mock_openai = AsyncMock()
        router.providers[LLMProviderType.ANTHROPIC] = mock_anthropic
        router.providers[LLMProviderType.OPENAI] = mock_openai
        router._initialized = True

        await router.close()

        mock_anthropic.close.assert_called_once()
        mock_openai.close.assert_called_once()
        assert len(router.providers) == 0
        assert router._initialized is False


def test_get_llm_router():
    """Test getting singleton router instance."""
    router1 = get_llm_router()
    router2 = get_llm_router()
    assert router1 is router2