"""Unit tests for RedisConfig class."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.redis_client import RedisConfig


@pytest.mark.unit
class TestRedisConfig:
    """Test RedisConfig configuration management."""

    def test_config_from_defaults(self) -> None:
        """Test configuration with default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = RedisConfig()
            assert config.host == "localhost"
            assert config.port == 6379
            assert config.password is None

    def test_config_from_env_vars(self) -> None:
        """Test configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "REDIS_HOST": "test-host",
                "REDIS_PORT": "6380",
                "REDIS_PASSWORD": "test-password",
            },
        ):
            config = RedisConfig()
            assert config.host == "test-host"
            assert config.port == 6380
            assert config.password == "test-password"

    def test_config_from_parameters(self) -> None:
        """Test configuration from direct parameters."""
        config = RedisConfig(host="custom-host", port=6381, password="custom-password")
        assert config.host == "custom-host"
        assert config.port == 6381
        assert config.password == "custom-password"

    def test_parameters_override_env_vars(self) -> None:
        """Test that direct parameters override environment variables."""
        with patch.dict(
            os.environ,
            {
                "REDIS_HOST": "env-host",
                "REDIS_PORT": "6380",
                "REDIS_PASSWORD": "env-password",
            },
        ):
            config = RedisConfig(host="param-host", port=6381, password="param-password")
            assert config.host == "param-host"
            assert config.port == 6381
            assert config.password == "param-password"

    def test_password_preview_with_password(self) -> None:
        """Test password preview generation with a password."""
        config = RedisConfig(password="secret123")
        preview = config.get_password_preview()
        assert preview == "s********"
        assert len(preview) == len("secret123")

    def test_password_preview_without_password(self) -> None:
        """Test password preview generation without a password."""
        with patch.dict(os.environ, {}, clear=True):
            config = RedisConfig()
            preview = config.get_password_preview()
            assert preview == "None"

    def test_password_preview_single_char(self) -> None:
        """Test password preview with single character password."""
        config = RedisConfig(password="x")
        preview = config.get_password_preview()
        assert preview == "x"

    def test_from_env_file_not_found(self) -> None:
        """Test loading from non-existent .env file."""
        fake_path = Path("/nonexistent/path/.env")
        with pytest.raises(FileNotFoundError, match=".env file not found"):
            RedisConfig.from_env(fake_path)

    def test_port_conversion_from_string(self) -> None:
        """Test that port is properly converted from string to int."""
        with patch.dict(os.environ, {"REDIS_PORT": "6380"}):
            config = RedisConfig()
            assert isinstance(config.port, int)
            assert config.port == 6380
