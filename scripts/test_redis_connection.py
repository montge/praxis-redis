#!/usr/bin/env python3

# scripts/test_redis_connection.py

import os
import sys
import time
from datetime import datetime
from pathlib import Path

import redis
from dotenv import load_dotenv
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query


def load_env():
    """
    Load environment variables from .env file in root directory
    """
    env_path = Path(__file__).parents[1] / ".env"
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        print("Please copy .env.example to .env and set your configuration")
        sys.exit(1)
    load_dotenv(dotenv_path=env_path)


def check_redis_logs():
    """Check Redis container logs for issues"""
    try:
        import subprocess

        result = subprocess.run(["docker", "logs", "redis-llm"], capture_output=True, text=True)
        if result.stdout or result.stderr:
            print("\nRedis container logs:")
            print("-" * 40)
            if result.stdout:
                print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print("-" * 40)
    except Exception as e:
        print(f"Could not fetch Redis logs: {e}")


def wait_for_redis(redis_client, max_retries=5, delay=2):
    """
    Attempt to connect to Redis with retries
    """
    for attempt in range(max_retries):
        try:
            if redis_client.ping():
                return True
        except redis.ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Waiting for Redis to be ready... (attempt {attempt + 1}/{max_retries})")
                print(f"Error: {str(e)}")
                check_redis_logs()
                time.sleep(delay)
            continue
    return False


def show_redis_info(redis_client):
    """
    Display Redis version and loaded modules information
    """
    try:
        # Get Redis version
        info = redis_client.info()
        redis_version = info.get("redis_version", "unknown")
        print(f"\nRedis Version: {redis_version}")

        # Get modules information
        print("\nLoaded Modules:")
        print("-" * 50)
        modules = redis_client.module_list()
        for module in modules:
            name = module.get("name", "unknown")
            ver = module.get("ver", "unknown")
            print(f"- {name:<15} version: {ver}")
        print("-" * 50 + "\n")

    except Exception as e:
        print(f"❌ Error getting Redis information: {str(e)}")


def test_redisearch(redis_client):
    """
    Test RediSearch functionality by creating an index and performing a search
    """
    try:
        print("Testing RediSearch functionality...")

        # First verify RediSearch is loaded
        modules = redis_client.module_list()
        if not any(mod["name"] == "search" for mod in modules):
            print("❌ RediSearch module is not loaded!")
            return False

        print("✅ RediSearch module is loaded")

        # Create a search index
        schema = (
            TextField("title", weight=5.0),
            TextField("content"),
            TagField("tags"),
            NumericField("doc_score"),
        )

        # Drop index if exists
        try:
            redis_client.ft("blog-idx").dropindex()
            print("✅ Dropped existing index")
        except Exception:
            print("No existing index to drop")

        # Create the index
        print("Creating search index...")
        redis_client.ft("blog-idx").create_index(
            schema, definition=IndexDefinition(prefix=["blog:"], index_type=IndexType.HASH)
        )
        print("✅ Created search index")

        # Add some test documents
        print("Adding test document...")
        redis_client.hset(
            "blog:1",
            mapping={
                "title": "Redis Stack Tutorial",
                "content": "Learn how to use Redis Stack with Python",
                "tags": "redis,python,tutorial",
                "doc_score": 0.8,
            },
        )
        print("✅ Added test document")

        # Test search functionality
        print("Performing search...")
        query = Query("Redis").with_scores()
        results = redis_client.ft("blog-idx").search(query)

        print(f"✅ RediSearch test successful - found {results.total} documents")
        if results.total > 0:
            print(f"First result: {results.docs[0]}")
        return True

    except Exception as e:
        print(f"❌ RediSearch test failed with exception type: {type(e)}")
        print(f"❌ RediSearch test failed: {str(e)}")
        import traceback

        print("Traceback:")
        print(traceback.format_exc())
        return False


def test_redisjson(redis_client):
    """
    Test RedisJSON functionality by storing and retrieving JSON data
    """
    try:
        # Store a JSON document
        json_key = "user:1"
        json_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "profile": {"age": 30, "interests": ["Redis", "Python", "AI"]},
        }

        redis_client.json().set(json_key, "$", json_data)

        # Retrieve the entire document
        _result = redis_client.json().get(json_key)

        # Test JSON path operations
        age = redis_client.json().get(json_key, "$.profile.age")
        interests = redis_client.json().get(json_key, "$.profile.interests")

        print("✅ RedisJSON test successful - stored and retrieved JSON data")
        print(f"Retrieved age: {age}")
        print(f"Retrieved interests: {interests}")

        # Clean up
        redis_client.delete(json_key)
        return True

    except Exception as e:
        print(f"❌ RedisJSON test failed: {str(e)}")
        return False


def test_redis_connection():
    """
    Test Redis connectivity and modules by performing basic operations:
    - Establish connection
    - Test basic Redis operations
    - Test RediSearch functionality
    - Test RedisJSON functionality
    """
    try:
        # Load environment variables
        load_env()

        # Debug password (show first character followed by stars)
        password = os.getenv("REDIS_PASSWORD")
        if password:
            password_preview = password[0] + "*" * (len(password) - 1)
            print(f"Using Redis password: {password_preview}")
        else:
            print("❌ No Redis password found in environment!")

        # Initialize Redis connection using environment variables
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True,
        )

        # Test connection with ping and retry
        print("Testing Redis connection...")
        if not wait_for_redis(redis_client):
            print("❌ Failed to connect to Redis after multiple attempts")
            check_redis_logs()
            return False

        print("✅ Successfully connected to Redis")

        # Show Redis version and modules information
        show_redis_info(redis_client)

        # Test basic Redis operations
        test_key = "test:hello"
        test_value = f"Hello World! Timestamp: {datetime.now()}"
        redis_client.set(test_key, test_value)
        print("✅ Basic Redis operations successful")

        # Test RediSearch
        if not test_redisearch(redis_client):
            return False

        # Test RedisJSON
        if not test_redisjson(redis_client):
            return False

        # Clean up
        redis_client.delete(test_key)
        print("✅ Cleaned up test data")

        return True

    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")
        print("Please ensure Redis is running and check your connection settings")
        check_redis_logs()
        return False
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        check_redis_logs()
        return False


if __name__ == "__main__":
    print("Redis Stack Connection Test Script")
    print("-" * 30)

    success = test_redis_connection()
    sys.exit(0 if success else 1)
