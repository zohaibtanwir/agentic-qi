"""Unit tests for LLM router (Anthropic-only)."""

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
    """Test LLM Router (Anthropic-only configuration)."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for Anthropic-only."""
        settings = MagicMock()
        settings.has_anthropic = True
        settings.anthropic_api_key = "test-anthropic-key"
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
    async def test_initialize_anthropic_only(self, mock_settings):
        """Test initializing Anthropic provider only."""
        with patch("test_cases_agent.llm.router.get_settings", return_value=mock_settings):
            with patch("test_cases_agent.llm.router.SimpleAnthropicClient") as MockAnthropic:
                # Setup mock
                mock_anthropic = AsyncMock()
                MockAnthropic.return_value = mock_anthropic

                # Initialize router
                router = LLMRouter()
                await router.initialize()

                # Check only Anthropic was initialized
                assert router._initialized is True
                assert LLMProviderType.ANTHROPIC in router.providers
                assert len(router.providers) == 1

                # Check initialize was called
                mock_anthropic.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_no_anthropic_configured(self):
        """Test initialization fails when Anthropic is not configured."""
        settings = MagicMock()
        settings.has_anthropic = False

        with patch("test_cases_agent.llm.router.get_settings", return_value=settings):
            router = LLMRouter()
            with pytest.raises(LLMError, match="Anthropic API key not configured"):
                await router.initialize()

    @pytest.mark.asyncio
    async def test_generate_with_anthropic(self, router):
        """Test generation with Anthropic provider."""
        # Setup mock provider
        mock_provider = AsyncMock()
        mock_response = LLMResponse(
            content="Test response from Claude",
            model="claude-sonnet-4",
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
        response = await router.generate(messages)

        assert response == mock_response
        mock_provider.generate.assert_called_once_with(messages, None)

    @pytest.mark.asyncio
    async def test_generate_without_initialization(self, router):
        """Test generation initializes router if not initialized."""
        # Setup mock provider
        mock_provider = AsyncMock()
        mock_response = LLMResponse(
            content="Test response",
            model="claude-sonnet-4",
            provider="anthropic",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        mock_provider.generate.return_value = mock_response

        # Mock initialize to add the provider
        async def mock_initialize():
            router.providers[LLMProviderType.ANTHROPIC] = mock_provider
            router._initialized = True

        router.initialize = mock_initialize

        # Generate (should auto-initialize)
        messages = [Message(role=MessageRole.USER, content="Test")]
        response = await router.generate(messages)

        assert response == mock_response
        assert router._initialized is True

    @pytest.mark.asyncio
    async def test_generate_anthropic_fails(self, router):
        """Test when Anthropic generation fails (no fallback available)."""
        # Setup mock provider that fails
        mock_provider = AsyncMock()
        mock_provider.generate.side_effect = Exception("Anthropic API error")

        router.providers[LLMProviderType.ANTHROPIC] = mock_provider
        router._initialized = True

        # Generate - should raise error since no fallback
        messages = [Message(role=MessageRole.USER, content="Test")]
        with pytest.raises(LLMError, match="Anthropic generation failed"):
            await router.generate(messages)

    @pytest.mark.asyncio
    async def test_generate_text(self, router):
        """Test simple text generation."""
        # Setup mock provider
        mock_provider = AsyncMock()
        mock_response = LLMResponse(
            content="Test response",
            model="claude-sonnet-4",
            provider="anthropic",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        mock_provider.generate.return_value = mock_response
        router.providers[LLMProviderType.ANTHROPIC] = mock_provider
        router._initialized = True

        # Generate text
        response = await router.generate_text("Test prompt")

        assert response == mock_response
        # Check that it was called with a Message
        call_args = mock_provider.generate.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0].role == "user"
        assert call_args[0].content == "Test prompt"

    def test_get_provider_order_anthropic_only(self, router):
        """Test getting provider order returns only Anthropic."""
        router.providers = {
            LLMProviderType.ANTHROPIC: MagicMock(),
        }

        # With fallback (no fallback available in Anthropic-only mode)
        order = router._get_provider_order(LLMProviderType.ANTHROPIC, fallback=True)
        assert order == [LLMProviderType.ANTHROPIC]

        # Without fallback
        order = router._get_provider_order(LLMProviderType.ANTHROPIC, fallback=False)
        assert order == [LLMProviderType.ANTHROPIC]

    def test_get_available_providers_anthropic_only(self, router):
        """Test getting available providers returns only Anthropic."""
        router.providers = {
            LLMProviderType.ANTHROPIC: MagicMock(),
        }

        providers = router.get_available_providers()
        assert providers == [LLMProviderType.ANTHROPIC]
        assert len(providers) == 1

    def test_get_provider(self, router):
        """Test getting specific provider."""
        mock_provider = MagicMock()
        router.providers[LLMProviderType.ANTHROPIC] = mock_provider

        # Get Anthropic provider
        provider = router.get_provider(LLMProviderType.ANTHROPIC)
        assert provider == mock_provider

    def test_is_provider_available(self, router):
        """Test checking provider availability."""
        router.providers[LLMProviderType.ANTHROPIC] = MagicMock()

        # Anthropic should be available
        assert router.is_provider_available(LLMProviderType.ANTHROPIC) is True

    def test_get_supported_models_anthropic_only(self, router):
        """Test getting supported models for Anthropic."""
        mock_anthropic = MagicMock()
        mock_anthropic.get_supported_models.return_value = [
            "claude-sonnet-4",
            "claude-opus-4",
            "claude-haiku-4"
        ]

        router.providers[LLMProviderType.ANTHROPIC] = mock_anthropic

        # Get all models
        models = router.get_supported_models()
        assert models == {"anthropic": ["claude-sonnet-4", "claude-opus-4", "claude-haiku-4"]}

        # Get specific provider models
        models = router.get_supported_models(LLMProviderType.ANTHROPIC)
        assert models == {"anthropic": ["claude-sonnet-4", "claude-opus-4", "claude-haiku-4"]}

    @pytest.mark.asyncio
    async def test_close(self, router):
        """Test closing router."""
        mock_anthropic = AsyncMock()
        router.providers[LLMProviderType.ANTHROPIC] = mock_anthropic
        router._initialized = True

        await router.close()

        mock_anthropic.close.assert_called_once()
        assert len(router.providers) == 0
        assert router._initialized is False


def test_get_llm_router():
    """Test getting singleton router instance."""
    router1 = get_llm_router()
    router2 = get_llm_router()
    assert router1 is router2
