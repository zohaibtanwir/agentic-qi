import os
import pytest
from unittest.mock import patch

from ecommerce_agent.config import Settings, get_settings


class TestSettings:
    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        assert settings.service_name == "ecommerce-domain-agent"
        assert settings.grpc_port == 9002
        assert settings.http_port == 8082

    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        get_settings.cache_clear()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2