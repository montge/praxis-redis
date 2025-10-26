#!/usr/bin/env python3
"""
Redis client wrapper for Redis Stack operations.
Provides high-level interfaces for Redis, RediSearch, and RedisJSON operations.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import redis
from dotenv import load_dotenv
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query


class RedisConfig:
    """Configuration for Redis connection."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
    ):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = int(port or os.getenv("REDIS_PORT", "6379"))
        self.password = password or os.getenv("REDIS_PASSWORD")

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "RedisConfig":
        """Load configuration from .env file."""
        if env_path is None:
            env_path = Path(__file__).parents[1] / ".env"

        if not env_path.exists():
            raise FileNotFoundError(
                f".env file not found at {env_path}. "
                "Please copy .env.example to .env and set your configuration"
            )

        load_dotenv(dotenv_path=env_path)
        return cls()

    def get_password_preview(self) -> str:
        """Get password preview for logging (first char + asterisks)."""
        if not self.password:
            return "None"
        return self.password[0] + "*" * (len(self.password) - 1)


class RedisStackClient:
    """
    High-level client for Redis Stack operations.
    Provides methods for basic Redis, RediSearch, and RedisJSON operations.
    """

    def __init__(self, config: RedisConfig):
        self.config = config
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                decode_responses=True,
            )
        return self._client

    def ping(self) -> bool:
        """Test connection to Redis."""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    def get_info(self) -> dict[str, Any]:
        """Get Redis server information."""
        return self.client.info()

    def get_version(self) -> str:
        """Get Redis version."""
        info = self.get_info()
        return info.get("redis_version", "unknown")

    def get_modules(self) -> list[dict[str, Any]]:
        """Get list of loaded Redis modules."""
        return self.client.module_list()

    def has_module(self, module_name: str) -> bool:
        """Check if a specific module is loaded."""
        modules = self.get_modules()
        return any(mod.get("name") == module_name for mod in modules)

    def set(self, key: str, value: str) -> bool:
        """Set a key-value pair in Redis."""
        return self.client.set(key, value)

    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        return self.client.get(key)

    def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        return self.client.delete(*keys)

    def create_search_index(self, index_name: str, prefix: str, schema: tuple) -> None:
        """Create a RediSearch index."""
        self.client.ft(index_name).create_index(
            schema, definition=IndexDefinition(prefix=[prefix], index_type=IndexType.HASH)
        )

    def drop_search_index(self, index_name: str) -> None:
        """Drop a RediSearch index."""
        try:
            self.client.ft(index_name).dropindex()
        except redis.exceptions.ResponseError:
            # Index doesn't exist, ignore
            pass

    def add_document(self, key: str, mapping: dict[str, Any]) -> bool:
        """Add a document to Redis (for searching)."""
        return self.client.hset(key, mapping=mapping)

    def search(self, index_name: str, query_string: str) -> Any:
        """Perform a search query."""
        query = Query(query_string).with_scores()
        return self.client.ft(index_name).search(query)

    def json_set(self, key: str, path: str, value: Any) -> bool:
        """Set a JSON value at a specific path."""
        return self.client.json().set(key, path, value)

    def json_get(self, key: str, path: Optional[str] = None) -> Any:
        """Get a JSON value from a specific path."""
        if path:
            return self.client.json().get(key, path)
        return self.client.json().get(key)

    def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "RedisStackClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class RedisSearchHelper:
    """Helper class for RediSearch operations."""

    @staticmethod
    def create_blog_schema() -> tuple:
        """Create a standard blog post schema for testing."""
        return (
            TextField("title", weight=5.0),
            TextField("content"),
            TagField("tags"),
            NumericField("doc_score"),
        )

    @staticmethod
    def create_sample_blog_post() -> dict[str, Any]:
        """Create a sample blog post for testing."""
        return {
            "title": "Redis Stack Tutorial",
            "content": "Learn how to use Redis Stack with Python",
            "tags": "redis,python,tutorial",
            "doc_score": 0.8,
        }


class RedisJSONHelper:
    """Helper class for RedisJSON operations."""

    @staticmethod
    def create_sample_user() -> dict[str, Any]:
        """Create a sample user document for testing."""
        return {
            "name": "John Doe",
            "email": "john@example.com",
            "profile": {"age": 30, "interests": ["Redis", "Python", "AI"]},
        }
