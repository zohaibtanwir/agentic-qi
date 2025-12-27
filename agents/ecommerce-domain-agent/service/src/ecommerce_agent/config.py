from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service
    service_name: str = "ecommerce-domain-agent"
    grpc_port: int = 9002
    http_port: int = 8082
    log_level: str = "INFO"

    # LLM - Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # RAG - Weaviate
    weaviate_url: str = "http://weaviate:8080"
    weaviate_api_key: str = ""
    weaviate_grpc_port: int = 50051

    # Test Data Agent (client) - supports URL or host/port
    test_data_agent_url: Optional[str] = None  # e.g., "http://test-data-agent:9091"
    test_data_agent_host: str = "localhost"
    test_data_agent_port: int = 9091
    test_data_agent_timeout: float = 30.0

    @model_validator(mode="after")
    def parse_test_data_agent_url(self) -> "Settings":
        """Parse TEST_DATA_AGENT_URL if provided and extract host/port."""
        if self.test_data_agent_url:
            parsed = urlparse(self.test_data_agent_url)
            if parsed.hostname:
                self.test_data_agent_host = parsed.hostname
            if parsed.port:
                self.test_data_agent_port = parsed.port
        return self

    # Knowledge
    knowledge_refresh_interval: int = 3600

    # Observability
    prometheus_port: int = 9092
    otlp_endpoint: str = "http://otel-collector:4317"
    enable_tracing: bool = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()