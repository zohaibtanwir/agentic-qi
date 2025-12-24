import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.service_name = "test-service"
    settings.grpc_port = 9002
    settings.http_port = 8082
    settings.log_level = "DEBUG"
    settings.anthropic_api_key = "test-key"
    settings.weaviate_url = "http://localhost:8080"
    settings.weaviate_grpc_port = 50051
    settings.test_data_agent_host = "localhost"
    settings.test_data_agent_port = 9001
    return settings