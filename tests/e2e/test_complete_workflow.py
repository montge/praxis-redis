"""End-to-end tests for complete Redis Stack workflows."""

import time

import pytest

from scripts.redis_client import RedisSearchHelper, RedisStackClient


@pytest.mark.e2e
@pytest.mark.requires_redis
class TestCompleteWorkflow:
    """Test complete end-to-end workflows combining multiple Redis features."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, redis_client: RedisStackClient) -> None:
        """Setup and teardown for each test."""
        self.index_name = "e2e-blog-idx"
        self.key_prefix = "e2e:blog:"
        self.json_prefix = "e2e:json:"

        # Cleanup before test
        redis_client.drop_search_index(self.index_name)

        yield

        # Cleanup after test
        redis_client.drop_search_index(self.index_name)
        for i in range(1, 20):
            redis_client.delete(f"{self.key_prefix}{i}")
            redis_client.delete(f"{self.json_prefix}{i}")

    def test_blog_platform_workflow(self, redis_client: RedisStackClient) -> None:
        """
        Test a complete blog platform workflow:
        1. Create search index for blog posts
        2. Add blog posts as hash documents
        3. Search for posts
        4. Store author info as JSON
        5. Retrieve and verify data
        """
        # Step 1: Create search index
        schema = RedisSearchHelper.create_blog_schema()
        redis_client.create_search_index(self.index_name, self.key_prefix, schema)

        # Step 2: Add blog posts
        blog_posts = [
            {
                "title": "Getting Started with Redis",
                "content": "Redis is an in-memory data structure store",
                "tags": "redis,tutorial,beginner",
                "doc_score": 0.95,
            },
            {
                "title": "Advanced Redis Patterns",
                "content": "Learn advanced patterns for Redis applications",
                "tags": "redis,advanced,patterns",
                "doc_score": 0.85,
            },
            {
                "title": "Python and Redis Integration",
                "content": "How to integrate Redis with Python applications",
                "tags": "python,redis,integration",
                "doc_score": 0.90,
            },
        ]

        for i, post in enumerate(blog_posts, start=1):
            redis_client.add_document(f"{self.key_prefix}{i}", post)

        # Step 3: Search for posts
        results = redis_client.search(self.index_name, "Redis")
        assert results.total == 3

        results = redis_client.search(self.index_name, "Python")
        assert results.total == 1

        # Step 4: Store author information as JSON
        authors = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "bio": "Redis enthusiast",
                "posts": [1],
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "bio": "Database expert",
                "posts": [2, 3],
            },
        ]

        for author in authors:
            redis_client.json_set(f"{self.json_prefix}author:{author['id']}", "$", author)

        # Step 5: Retrieve and verify author data
        author1 = redis_client.json_get(f"{self.json_prefix}author:1")
        assert author1["name"] == "John Doe"
        assert len(author1["posts"]) == 1

        author2 = redis_client.json_get(f"{self.json_prefix}author:2")
        assert author2["name"] == "Jane Smith"
        assert len(author2["posts"]) == 2

        # Cleanup authors
        redis_client.delete(f"{self.json_prefix}author:1")
        redis_client.delete(f"{self.json_prefix}author:2")

    def test_user_preference_workflow(self, redis_client: RedisStackClient) -> None:
        """
        Test user preference management workflow:
        1. Store user preferences as JSON
        2. Update specific preferences
        3. Query preferences
        4. Store user activity in hash
        5. Search user activity
        """
        user_id = 1

        # Step 1: Store initial user preferences
        preferences = {
            "user_id": user_id,
            "theme": "dark",
            "language": "en",
            "notifications": {"email": True, "push": False, "sms": False},
            "privacy": {"profile_visible": True, "show_email": False},
        }

        pref_key = f"{self.json_prefix}preferences:{user_id}"
        redis_client.json_set(pref_key, "$", preferences)

        # Step 2: Update specific preference
        redis_client.json_set(pref_key, "$.notifications.push", True)

        # Step 3: Query preferences
        result = redis_client.json_get(pref_key)
        assert result["theme"] == "dark"
        assert result["notifications"]["push"] is True

        # Step 4: Store user activity
        schema = RedisSearchHelper.create_blog_schema()
        activity_index = "e2e-activity-idx"
        activity_prefix = "e2e:activity:"

        redis_client.create_search_index(activity_index, activity_prefix, schema)

        activities = [
            {
                "title": "Login",
                "content": "User logged in from Chrome",
                "tags": "login,security",
                "doc_score": 0.5,
            },
            {
                "title": "Profile Update",
                "content": "User updated profile picture",
                "tags": "profile,update",
                "doc_score": 0.6,
            },
        ]

        for i, activity in enumerate(activities, start=1):
            redis_client.add_document(f"{activity_prefix}{i}", activity)

        # Step 5: Search user activity
        results = redis_client.search(activity_index, "profile")
        assert results.total == 1

        # Cleanup
        redis_client.delete(pref_key)
        redis_client.drop_search_index(activity_index)
        for i in range(1, 3):
            redis_client.delete(f"{activity_prefix}{i}")

    def test_caching_and_search_workflow(self, redis_client: RedisStackClient) -> None:
        """
        Test combined caching and search workflow:
        1. Cache frequently accessed data
        2. Index searchable content
        3. Search and retrieve cached data
        """
        # Step 1: Cache product data
        products = {
            "prod:1": '{"id": 1, "name": "Laptop", "price": 999.99}',
            "prod:2": '{"id": 2, "name": "Mouse", "price": 29.99}',
            "prod:3": '{"id": 3, "name": "Keyboard", "price": 79.99}',
        }

        for key, value in products.items():
            redis_client.set(key, value)

        # Step 2: Create searchable product index
        schema = RedisSearchHelper.create_blog_schema()
        product_index = "e2e-product-idx"
        product_prefix = "e2e:product:"

        # Drop index if it exists from previous test
        redis_client.drop_search_index(product_index)
        redis_client.create_search_index(product_index, product_prefix, schema)

        searchable_products = [
            {
                "title": "Laptop",
                "content": "High-performance laptop for developers",
                "tags": "electronics,computers",
                "doc_score": 0.95,
            },
            {
                "title": "Mouse",
                "content": "Ergonomic wireless mouse",
                "tags": "electronics,accessories",
                "doc_score": 0.75,
            },
        ]

        for i, prod in enumerate(searchable_products, start=1):
            redis_client.add_document(f"{product_prefix}{i}", prod)

        # Allow index to update
        time.sleep(0.1)

        # Step 3: Search products
        results = redis_client.search(product_index, "laptop")
        assert results.total == 1

        # Search for "mouse" in content/title
        results = redis_client.search(product_index, "mouse")
        assert results.total == 1

        # Step 4: Retrieve cached data
        laptop_data = redis_client.get("prod:1")
        assert laptop_data is not None
        assert "Laptop" in laptop_data

        # Cleanup
        for key in products:
            redis_client.delete(key)
        redis_client.drop_search_index(product_index)
        for i in range(1, 3):
            redis_client.delete(f"{product_prefix}{i}")
