"""Configuration management for Test Cases Agent."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file from the root qa-platform folder
root_env_path = Path(__file__).parent.parent.parent.parent / ".env"
if root_env_path.exists():
    load_dotenv(root_env_path, override=True)


class Environment(str, Enum):
    """Environment enum."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(str, Enum):
    """Log level enum."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    """LLM provider enum."""

    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Configuration
    service_name: str = Field(default="test-cases-agent", description="Service name")
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Environment"
    )
    grpc_port: int = Field(default=9003, description="gRPC server port")
    http_port: int = Field(default=8083, description="HTTP health check port")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")

    # LLM Configuration (Anthropic only)
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")

    # Weaviate Configuration
    weaviate_url: str = Field(
        default="http://localhost:8080", description="Weaviate instance URL"
    )
    weaviate_api_key: Optional[str] = Field(
        default=None, description="Weaviate API key"
    )

    # Agent Connections
    domain_agent_host: str = Field(
        default="localhost", description="Domain Agent host"
    )
    domain_agent_port: int = Field(default=9002, description="Domain Agent port")
    test_data_agent_host: str = Field(
        default="localhost", description="Test Data Agent host"
    )
    test_data_agent_port: int = Field(
        default=9091, description="Test Data Agent port"
    )

    # Timeouts (in seconds)
    grpc_timeout: int = Field(default=30, description="gRPC timeout in seconds")
    llm_timeout: int = Field(default=60, description="LLM timeout in seconds")
    agent_timeout: int = Field(default=30, description="Agent timeout in seconds")

    # Performance
    max_workers: int = Field(default=10, description="Max worker threads")
    max_concurrent_requests: int = Field(
        default=100, description="Max concurrent requests"
    )

    # Metrics
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")

    # File Paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="Project root directory",
    )

    @field_validator("anthropic_api_key", mode="before")
    def validate_api_keys(cls, v: Optional[str]) -> Optional[str]:
        """Validate API keys."""
        if v and v.startswith("your_") and v.endswith("_here"):
            return None
        return v

    @property
    def domain_agent_address(self) -> str:
        """Get Domain Agent address."""
        return f"{self.domain_agent_host}:{self.domain_agent_port}"

    @property
    def test_data_agent_address(self) -> str:
        """Get Test Data Agent address."""
        return f"{self.test_data_agent_host}:{self.test_data_agent_port}"

    @property
    def has_anthropic(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(self.anthropic_api_key)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance."""
    return settings


# For convenience
__all__ = [
    "Settings",
    "settings",
    "get_settings",
    "Environment",
    "LogLevel",
    "LLMProvider",
]