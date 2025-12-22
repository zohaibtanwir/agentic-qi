"""Unit tests for LLM base classes."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from test_cases_agent.llm.base import (
    GenerationConfig,
    LLMError,
    LLMProvider,
    LLMResponse,
    Message,
    MessageRole,
)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    async def initialize(self):
        self._client = MagicMock()

    async def generate(self, messages, config=None):
        return LLMResponse(
            content="Test response",
            model="test-model",
            provider=self.provider_name,
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

    async def generate_text(self, prompt, config=None):
        return await self.generate([Message(role=MessageRole.USER, content=prompt)], config)

    def is_available(self):
        return True

    def get_supported_models(self):
        return ["test-model-1", "test-model-2"]

    def estimate_tokens(self, text):
        return len(text) // 4

    @property
    def provider_name(self):
        return "mock"


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(
            role=MessageRole.USER,
            content="Test content",
            name="test_user",
            metadata={"key": "value"},
        )

        assert msg.role == MessageRole.USER
        assert msg.content == "Test content"
        assert msg.name == "test_user"
        assert msg.metadata == {"key": "value"}

    def test_message_roles(self):
        """Test different message roles."""
        system = Message(role=MessageRole.SYSTEM, content="System")
        user = Message(role=MessageRole.USER, content="User")
        assistant = Message(role=MessageRole.ASSISTANT, content="Assistant")

        assert system.role == MessageRole.SYSTEM
        assert user.role == MessageRole.USER
        assert assistant.role == MessageRole.ASSISTANT


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_response_creation(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Generated text",
            model="claude-3-sonnet-20240229",
            provider="anthropic",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            finish_reason="stop",
            metadata={"id": "123"},
        )

        assert response.content == "Generated text"
        assert response.model == "claude-3-sonnet-20240229"
        assert response.provider == "anthropic"
        assert response.prompt_tokens == 100
        assert response.completion_tokens == 50
        assert response.total_tokens == 150
        assert response.finish_reason == "stop"
        assert response.metadata == {"id": "123"}


class TestGenerationConfig:
    """Test GenerationConfig dataclass."""

    def test_default_config(self):
        """Test default generation config."""
        config = GenerationConfig()

        assert config.model is None
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
        assert config.stream is False

    def test_custom_config(self):
        """Test custom generation config."""
        config = GenerationConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000,
            top_p=0.9,
            stop_sequences=["\n\n", "END"],
        )

        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.top_p == 0.9
        assert config.stop_sequences == ["\n\n", "END"]


class TestLLMProvider:
    """Test LLMProvider base class."""

    @pytest.fixture
    def provider(self):
        """Create a mock provider."""
        return MockLLMProvider(api_key="test-key", default_model="test-model")

    def test_provider_initialization(self, provider):
        """Test provider initialization."""
        assert provider.api_key == "test-key"
        assert provider.default_model == "test-model"
        assert provider._client is None

    @pytest.mark.asyncio
    async def test_initialize(self, provider):
        """Test provider initialization."""
        await provider.initialize()
        assert provider._client is not None

    def test_validate_config(self, provider):
        """Test config validation."""
        # Test with None config
        config = provider.validate_config(None)
        assert config.model == "test-model"

        # Test with valid config
        config = GenerationConfig(temperature=0.5, top_p=0.8)
        validated = provider.validate_config(config)
        assert validated.temperature == 0.5
        assert validated.top_p == 0.8
        assert validated.model == "test-model"

    def test_validate_config_invalid_temperature(self, provider):
        """Test config validation with invalid temperature."""
        config = GenerationConfig(temperature=3.0)
        with pytest.raises(ValueError, match="Temperature must be between"):
            provider.validate_config(config)

    def test_validate_config_invalid_top_p(self, provider):
        """Test config validation with invalid top_p."""
        config = GenerationConfig(top_p=1.5)
        with pytest.raises(ValueError, match="top_p must be between"):
            provider.validate_config(config)

    def test_format_messages(self, provider):
        """Test message formatting."""
        messages = [
            Message(role=MessageRole.SYSTEM, content="System prompt"),
            Message(role=MessageRole.USER, content="User message", name="user1"),
            Message(role=MessageRole.ASSISTANT, content="Assistant reply"),
        ]

        formatted = provider.format_messages(messages)

        assert len(formatted) == 3
        assert formatted[0] == {"role": "system", "content": "System prompt"}
        assert formatted[1] == {"role": "user", "content": "User message", "name": "user1"}
        assert formatted[2] == {"role": "assistant", "content": "Assistant reply"}

    @pytest.mark.asyncio
    async def test_generate(self, provider):
        """Test generate method."""
        messages = [Message(role=MessageRole.USER, content="Test prompt")]
        response = await provider.generate(messages)

        assert response.content == "Test response"
        assert response.provider == "mock"
        assert response.total_tokens == 30

    @pytest.mark.asyncio
    async def test_generate_text(self, provider):
        """Test generate_text method."""
        response = await provider.generate_text("Test prompt")

        assert response.content == "Test response"
        assert response.provider == "mock"

    def test_is_available(self, provider):
        """Test is_available method."""
        assert provider.is_available() is True

    def test_get_supported_models(self, provider):
        """Test get_supported_models method."""
        models = provider.get_supported_models()
        assert len(models) == 2
        assert "test-model-1" in models
        assert "test-model-2" in models

    def test_estimate_tokens(self, provider):
        """Test token estimation."""
        text = "This is a test string with some words"
        tokens = provider.estimate_tokens(text)
        assert tokens == len(text) // 4

    @pytest.mark.asyncio
    async def test_close(self, provider):
        """Test closing provider."""
        await provider.initialize()
        # Make the close method async for the mock
        provider._client.close = AsyncMock()
        await provider.close()
        assert provider._client is None


class TestLLMErrors:
    """Test LLM error classes."""

    def test_llm_error(self):
        """Test base LLM error."""
        error = LLMError("Test error")
        assert str(error) == "Test error"

    def test_llm_api_error(self):
        """Test LLM API error."""
        from test_cases_agent.llm.base import LLMAPIError

        error = LLMAPIError(
            "API failed",
            provider="anthropic",
            status_code=500,
            response="Internal error",
        )
        assert str(error) == "API failed"
        assert error.provider == "anthropic"
        assert error.status_code == 500
        assert error.response == "Internal error"

    def test_rate_limit_error(self):
        """Test rate limit error."""
        from test_cases_agent.llm.base import LLMRateLimitError

        error = LLMRateLimitError(
            "Rate limit exceeded",
            provider="anthropic",
            status_code=429,
        )
        assert str(error) == "Rate limit exceeded"
        assert error.provider == "anthropic"
        assert error.status_code == 429

    def test_authentication_error(self):
        """Test authentication error."""
        from test_cases_agent.llm.base import LLMAuthenticationError

        error = LLMAuthenticationError(
            "Invalid API key",
            provider="anthropic",
            status_code=401,
        )
        assert str(error) == "Invalid API key"
        assert error.provider == "anthropic"
        assert error.status_code == 401