"""Integration tests for Redis connection and basic operations."""

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from scripts.redis_client import RedisStackClient


@pytest.mark.integration
@pytest.mark.requires_redis
class TestRedisConnection:
    """Test Redis connection and basic operations."""

    def test_ping_successful(self, redis_client: RedisStackClient) -> None:
        """Test successful connection to Redis."""
        assert redis_client.ping() is True

    def test_get_version(self, redis_client: RedisStackClient) -> None:
        """Test retrieving Redis version."""
        version = redis_client.get_version()
        assert version != "unknown"
        assert len(version) > 0

    def test_get_info(self, redis_client: RedisStackClient) -> None:
        """Test retrieving Redis server information."""
        info = redis_client.get_info()
        assert "redis_version" in info
        assert "used_memory" in info
        assert "connected_clients" in info

    def test_get_modules(self, redis_client: RedisStackClient) -> None:
        """Test retrieving loaded Redis modules."""
        modules = redis_client.get_modules()
        assert isinstance(modules, list)
        assert len(modules) > 0

    def test_has_search_module(self, redis_client: RedisStackClient) -> None:
        """Test that RediSearch module is loaded."""
        assert redis_client.has_module("search") is True

    def test_has_json_module(self, redis_client: RedisStackClient) -> None:
        """Test that RedisJSON module is loaded."""
        assert redis_client.has_module("ReJSON") is True

    def test_has_nonexistent_module(self, redis_client: RedisStackClient) -> None:
        """Test checking for a module that doesn't exist."""
        assert redis_client.has_module("nonexistent") is False


@pytest.mark.integration
@pytest.mark.requires_redis
class TestRedisBasicOperations:
    """Test basic Redis key-value operations."""

    def test_set_and_get(self, redis_client: RedisStackClient) -> None:
        """Test setting and getting a value."""
        key = "test:set_get"
        value = "Hello, Redis!"

        assert redis_client.set(key, value) is True
        assert redis_client.get(key) == value

        # Cleanup
        redis_client.delete(key)

    def test_get_nonexistent_key(self, redis_client: RedisStackClient) -> None:
        """Test getting a non-existent key returns None."""
        result = redis_client.get("test:nonexistent")
        assert result is None

    def test_delete_key(self, redis_client: RedisStackClient) -> None:
        """Test deleting a key."""
        key = "test:delete"
        redis_client.set(key, "value")

        deleted_count = redis_client.delete(key)
        assert deleted_count == 1
        assert redis_client.get(key) is None

    def test_delete_multiple_keys(self, redis_client: RedisStackClient) -> None:
        """Test deleting multiple keys at once."""
        keys = ["test:multi1", "test:multi2", "test:multi3"]
        for key in keys:
            redis_client.set(key, "value")

        deleted_count = redis_client.delete(*keys)
        assert deleted_count == 3

        for key in keys:
            assert redis_client.get(key) is None

    def test_delete_nonexistent_key(self, redis_client: RedisStackClient) -> None:
        """Test deleting a non-existent key returns 0."""
        deleted_count = redis_client.delete("test:nonexistent")
        assert deleted_count == 0


@pytest.mark.integration
@pytest.mark.requires_redis
class TestRedisContextManager:
    """Test Redis client as context manager."""

    def test_context_manager(self, redis_config) -> None:
        """Test using Redis client as context manager."""
        with RedisStackClient(redis_config) as client:
            assert client.ping() is True
            client.set("test:context", "value")
            assert client.get("test:context") == "value"
            client.delete("test:context")

        # Client should be closed after context exit
        assert client._client is None
