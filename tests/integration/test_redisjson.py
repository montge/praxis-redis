"""Integration tests for RedisJSON operations."""

import pytest

from scripts.redis_client import RedisJSONHelper, RedisStackClient


@pytest.mark.integration
@pytest.mark.requires_redis
class TestRedisJSON:
    """Test RedisJSON functionality."""

    def test_json_set_and_get(self, redis_client: RedisStackClient) -> None:
        """Test setting and getting a JSON document."""
        key = "test:user:1"
        user = RedisJSONHelper.create_sample_user()

        # Set JSON document
        assert redis_client.json_set(key, "$", user) is True

        # Get entire document
        result = redis_client.json_get(key)
        assert result["name"] == user["name"]
        assert result["email"] == user["email"]
        assert result["profile"]["age"] == user["profile"]["age"]

        # Cleanup
        redis_client.delete(key)

    def test_json_get_with_path(self, redis_client: RedisStackClient) -> None:
        """Test getting a specific path from JSON document."""
        key = "test:user:2"
        user = RedisJSONHelper.create_sample_user()
        redis_client.json_set(key, "$", user)

        # Get specific paths
        age = redis_client.json_get(key, "$.profile.age")
        assert age == [30]

        interests = redis_client.json_get(key, "$.profile.interests")
        assert isinstance(interests[0], list)
        assert "Redis" in interests[0]

        # Cleanup
        redis_client.delete(key)

    def test_json_nested_object(self, redis_client: RedisStackClient) -> None:
        """Test storing and retrieving nested JSON objects."""
        key = "test:config:1"
        config = {
            "app": {
                "name": "RedisApp",
                "version": "1.0.0",
                "features": {
                    "search": True,
                    "json": True,
                    "timeseries": False,
                },
            }
        }

        redis_client.json_set(key, "$", config)

        # Get nested values
        app_name = redis_client.json_get(key, "$.app.name")
        assert app_name == ["RedisApp"]

        features = redis_client.json_get(key, "$.app.features")
        assert features[0]["search"] is True
        assert features[0]["json"] is True
        assert features[0]["timeseries"] is False

        # Cleanup
        redis_client.delete(key)

    def test_json_array_operations(self, redis_client: RedisStackClient) -> None:
        """Test storing and retrieving JSON arrays."""
        key = "test:tags:1"
        tags = ["redis", "python", "database", "nosql"]

        redis_client.json_set(key, "$", tags)

        # Get array
        result = redis_client.json_get(key)
        assert result == tags
        assert len(result) == 4

        # Cleanup
        redis_client.delete(key)

    def test_json_update_document(self, redis_client: RedisStackClient) -> None:
        """Test updating a JSON document."""
        key = "test:user:3"
        user = {"name": "Alice", "age": 25}

        # Set initial document
        redis_client.json_set(key, "$", user)

        # Update specific field
        redis_client.json_set(key, "$.age", 26)

        # Verify update
        result = redis_client.json_get(key)
        assert result["age"] == 26
        assert result["name"] == "Alice"

        # Cleanup
        redis_client.delete(key)

    def test_json_complex_data_types(self, redis_client: RedisStackClient) -> None:
        """Test storing various JSON data types."""
        key = "test:complex:1"
        data = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"},
        }

        redis_client.json_set(key, "$", data)
        result = redis_client.json_get(key)

        assert result["string"] == "hello"
        assert result["number"] == 42
        assert result["float"] == 3.14
        assert result["boolean"] is True
        assert result["null"] is None
        assert result["array"] == [1, 2, 3]
        assert result["object"]["nested"] == "value"

        # Cleanup
        redis_client.delete(key)
