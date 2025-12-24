from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Test Data Agent (client)
    test_data_agent_host: str = "localhost"
    test_data_agent_port: int = 9091
    test_data_agent_timeout: float = 30.0

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