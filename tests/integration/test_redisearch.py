"""Integration tests for RediSearch operations."""

import pytest

from scripts.redis_client import RedisSearchHelper, RedisStackClient


@pytest.mark.integration
@pytest.mark.requires_redis
class TestRediSearch:
    """Test RediSearch functionality."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, redis_client: RedisStackClient) -> None:
        """Setup and teardown for each test."""
        self.index_name = "test-blog-idx"
        self.key_prefix = "test:blog:"

        # Cleanup before test
        redis_client.drop_search_index(self.index_name)

        yield

        # Cleanup after test
        redis_client.drop_search_index(self.index_name)
        # Clean up any test documents
        for i in range(1, 10):
            redis_client.delete(f"{self.key_prefix}{i}")

    def test_create_search_index(self, redis_client: RedisStackClient) -> None:
        """Test creating a search index."""
        schema = RedisSearchHelper.create_blog_schema()

        # Should not raise an exception
        redis_client.create_search_index(self.index_name, self.key_prefix, schema)

        # Verify by attempting to search (empty results expected)
        results = redis_client.search(self.index_name, "*")
        assert results.total == 0

    def test_drop_search_index(self, redis_client: RedisStackClient) -> None:
        """Test dropping a search index."""
        schema = RedisSearchHelper.create_blog_schema()
        redis_client.create_search_index(self.index_name, self.key_prefix, schema)

        # Should not raise an exception
        redis_client.drop_search_index(self.index_name)

        # Dropping non-existent index should not raise
        redis_client.drop_search_index(self.index_name)

    def test_add_and_search_document(self, redis_client: RedisStackClient) -> None:
        """Test adding a document and searching for it."""
        schema = RedisSearchHelper.create_blog_schema()
        redis_client.create_search_index(self.index_name, self.key_prefix, schema)

        # Add a document
        doc_key = f"{self.key_prefix}1"
        doc = RedisSearchHelper.create_sample_blog_post()
        redis_client.add_document(doc_key, doc)

        # Search for the document
        results = redis_client.search(self.index_name, "Redis")
        assert results.total == 1
        assert results.docs[0].id == doc_key

    def test_search_with_multiple_documents(self, redis_client: RedisStackClient) -> None:
        """Test searching with multiple documents."""
        schema = RedisSearchHelper.create_blog_schema()
        redis_client.create_search_index(self.index_name, self.key_prefix, schema)

        # Add multiple documents
        documents = [
            {
                "title": "Redis Tutorial",
                "content": "Learn Redis basics",
                "tags": "redis,tutorial",
                "doc_score": 0.9,
            },
            {
                "title": "Python Guide",
                "content": "Python programming with Redis",
                "tags": "python,redis",
                "doc_score": 0.8,
            },
            {
                "title": "Database Design",
                "content": "NoSQL database patterns",
                "tags": "database,nosql",
                "doc_score": 0.7,
            },
        ]

        for i, doc in enumerate(documents, start=1):
            redis_client.add_document(f"{self.key_prefix}{i}", doc)

        # Search for Redis
        results = redis_client.search(self.index_name, "Redis")
        assert results.total == 2

        # Search for Python
        results = redis_client.search(self.index_name, "Python")
        assert results.total == 1

        # Search for database
        results = redis_client.search(self.index_name, "database")
        assert results.total == 1

    def test_search_no_results(self, redis_client: RedisStackClient) -> None:
        """Test searching when no documents match."""
        schema = RedisSearchHelper.create_blog_schema()
        redis_client.create_search_index(self.index_name, self.key_prefix, schema)

        results = redis_client.search(self.index_name, "nonexistent")
        assert results.total == 0
        assert len(results.docs) == 0
