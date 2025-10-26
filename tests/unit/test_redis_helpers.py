"""Unit tests for Redis helper classes."""

import pytest

from scripts.redis_client import RedisJSONHelper, RedisSearchHelper


@pytest.mark.unit
class TestRedisSearchHelper:
    """Test RedisSearchHelper utility functions."""

    def test_create_blog_schema(self) -> None:
        """Test blog schema creation."""
        schema = RedisSearchHelper.create_blog_schema()
        assert len(schema) == 4
        assert schema[0].name == "title"
        assert schema[1].name == "content"
        assert schema[2].name == "tags"
        assert schema[3].name == "doc_score"

    def test_create_sample_blog_post(self) -> None:
        """Test sample blog post creation."""
        post = RedisSearchHelper.create_sample_blog_post()
        assert "title" in post
        assert "content" in post
        assert "tags" in post
        assert "doc_score" in post
        assert post["title"] == "Redis Stack Tutorial"
        assert isinstance(post["doc_score"], float)


@pytest.mark.unit
class TestRedisJSONHelper:
    """Test RedisJSONHelper utility functions."""

    def test_create_sample_user(self) -> None:
        """Test sample user creation."""
        user = RedisJSONHelper.create_sample_user()
        assert "name" in user
        assert "email" in user
        assert "profile" in user
        assert "age" in user["profile"]
        assert "interests" in user["profile"]
        assert isinstance(user["profile"]["interests"], list)
        assert len(user["profile"]["interests"]) > 0
