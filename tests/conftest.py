"""Pytest configuration and shared fixtures."""

import os
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

from scripts.redis_client import RedisConfig, RedisStackClient


@pytest.fixture(scope="session", autouse=True)
def load_test_env() -> None:
    """Load environment variables for testing."""
    env_path = Path(__file__).parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


@pytest.fixture(scope="session")
def redis_config() -> RedisConfig:
    """Create Redis configuration for tests."""
    return RedisConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
    )


@pytest.fixture
def redis_client(redis_config: RedisConfig) -> Generator[RedisStackClient, None, None]:
    """Create a Redis client for testing."""
    client = RedisStackClient(redis_config)
    yield client
    client.close()


@pytest.fixture
def clean_redis(redis_client: RedisStackClient) -> Generator[RedisStackClient, None, None]:
    """Provide a clean Redis instance for each test."""
    # Clean up before test
    test_keys = []

    yield redis_client

    # Clean up after test
    if test_keys:
        redis_client.delete(*test_keys)


def pytest_configure(config: pytest.Config) -> None:
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests that don't require external services")
    config.addinivalue_line(
        "markers", "integration: Integration tests that require Redis connection"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests that test complete workflows")
    config.addinivalue_line("markers", "slow: Tests that take a long time to run")
    config.addinivalue_line(
        "markers", "requires_redis: Tests that require a running Redis instance"
    )
