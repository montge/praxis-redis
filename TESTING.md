# Testing Guide

This document provides comprehensive testing guidelines for the Redis Stack thesis project.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Coverage](#coverage)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

This project follows **Test-Driven Development (TDD)** principles with three layers of testing:

1. **Unit Tests**: Fast, isolated tests without external dependencies
2. **Integration Tests**: Tests that require a running Redis instance
3. **End-to-End Tests**: Complete workflow tests simulating real-world usage

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests (no Redis required)
│   ├── __init__.py
│   ├── test_redis_config.py
│   └── test_redis_helpers.py
├── integration/                # Integration tests (requires Redis)
│   ├── __init__.py
│   ├── test_redis_connection.py
│   ├── test_redisearch.py
│   └── test_redisjson.py
└── e2e/                        # End-to-end tests (requires Redis)
    ├── __init__.py
    └── test_complete_workflow.py
```

## Running Tests

### Using Makefile (Recommended)

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests only (fast, no Redis)
make test-integration   # Integration tests (requires Redis)
make test-e2e           # End-to-end tests (requires Redis)

# Run with coverage
make test-all           # All tests with coverage report
make coverage           # Generate HTML coverage report and open in browser
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test types using markers
pytest -m unit                  # Unit tests only
pytest -m integration           # Integration tests only
pytest -m e2e                   # End-to-end tests only
pytest -m "not requires_redis"  # All tests that don't need Redis

# Run specific test files
pytest tests/unit/test_redis_config.py
pytest tests/integration/

# Run with coverage
pytest --cov=scripts --cov-report=html --cov-report=term-missing

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Before Running Integration/E2E Tests

Ensure Redis is running:

```bash
make start
# or
./scripts/start.sh
```

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (e.g., `TestRedisConfig`)
- Test functions: `test_*` (e.g., `test_config_from_defaults`)

### Test Structure Example

```python
"""Module docstring explaining what is being tested."""

import pytest
from scripts.redis_client import RedisConfig


@pytest.mark.unit
class TestRedisConfig:
    """Test RedisConfig configuration management."""

    def test_config_from_defaults(self) -> None:
        """Test configuration with default values."""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
```

### Using Markers

Mark tests appropriately:

```python
@pytest.mark.unit              # Unit test (no external dependencies)
@pytest.mark.integration       # Integration test (requires Redis)
@pytest.mark.e2e              # End-to-end test
@pytest.mark.requires_redis    # Requires Redis instance
@pytest.mark.slow             # Slow-running test
```

### Using Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
def test_redis_ping(redis_client: RedisStackClient) -> None:
    """Test Redis connection using fixture."""
    assert redis_client.ping() is True
```

### Cleanup in Tests

Always clean up test data:

```python
@pytest.fixture(autouse=True)
def setup_and_teardown(self, redis_client: RedisStackClient) -> None:
    """Setup and teardown for each test."""
    # Setup
    self.test_key = "test:mykey"

    yield

    # Teardown
    redis_client.delete(self.test_key)
```

## Coverage

### Coverage Goals

- **Overall**: Aim for >80% code coverage
- **New Code**: Should have >90% coverage
- **Critical Paths**: 100% coverage for authentication, data persistence

### Viewing Coverage Reports

```bash
# Generate and view HTML report
make coverage

# Generate terminal report
pytest --cov=scripts --cov-report=term-missing

# Generate XML report (for CI)
pytest --cov=scripts --cov-report=xml
```

### Coverage Configuration

Coverage settings are in `pytest.ini` and `pyproject.toml`:

- Source: `scripts/` directory
- Omit: `tests/`, `__pycache__/`, `venv/`, `.venv/`
- Branch coverage enabled
- Precision: 2 decimal places

## Continuous Integration

### GitHub Actions Workflow

The CI pipeline (`.github/workflows/ci.yml`) includes:

1. **Lint Job**: Code quality checks
   - Black formatter
   - Ruff linter
   - MyPy type checker

2. **Test-Unit Job**: Unit tests
   - Runs on all commits
   - No external dependencies
   - Fast execution

3. **Test-Integration Job**: Integration tests
   - Uses Redis Stack service container
   - Tests Redis, RediSearch, RedisJSON

4. **Test-E2E Job**: End-to-end tests
   - Uses Redis Stack service container
   - Tests complete workflows

5. **Test-All Job**: Combined coverage
   - Runs after lint passes
   - Uploads coverage to Codecov
   - Archives HTML coverage report

### Running CI Locally

Simulate the CI pipeline locally:

```bash
make ci-local
```

This runs:
1. All linters (black, ruff, mypy)
2. All tests with coverage

## Troubleshooting

### Redis Connection Errors

**Problem**: Tests fail with "Connection refused" or "Authentication failed"

**Solutions**:
1. Ensure Redis is running: `make start`
2. Check Redis password in `.env` matches test configuration
3. Verify Redis is healthy: `docker ps` (should show "healthy" status)
4. Check Redis logs: `docker logs redis-llm`

### Import Errors

**Problem**: `ModuleNotFoundError` when running tests

**Solutions**:
1. Ensure virtual environment is activated: `source .venv/bin/activate`
2. Install dependencies: `make install` or `make install-dev`
3. Verify Python path includes project root

### Coverage Not Generated

**Problem**: Coverage report is empty or missing files

**Solutions**:
1. Ensure tests are in `tests/` directory
2. Check coverage source configuration in `pytest.ini`
3. Run with explicit coverage: `pytest --cov=scripts`

### Tests Hang or Timeout

**Problem**: Tests run indefinitely or timeout

**Solutions**:
1. Check Redis connection (tests might be waiting for Redis)
2. Use timeout marker: `@pytest.mark.timeout(30)`
3. Run with timeout: `pytest --timeout=60`
4. Check for infinite loops in code

### Fixture Errors

**Problem**: "fixture not found" errors

**Solutions**:
1. Ensure `conftest.py` is in `tests/` directory
2. Check fixture scope (session, module, function)
3. Verify fixture name matches usage

### Parallel Test Failures

**Problem**: Tests fail when run in parallel but pass individually

**Solutions**:
1. Ensure tests are isolated (no shared state)
2. Use unique keys for each test
3. Proper cleanup in fixtures
4. Avoid hardcoded values (ports, keys)

## Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests isolated** (no dependencies between tests)
3. **Use descriptive names** (test name should describe what is being tested)
4. **One assertion per test** (when possible)
5. **Clean up resources** (delete test data, close connections)
6. **Use fixtures** (avoid code duplication)
7. **Mark tests appropriately** (unit, integration, e2e)
8. **Document complex tests** (docstrings explaining purpose)
9. **Run tests frequently** (after each change)
10. **Maintain high coverage** (aim for >80%)

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [RediSearch Documentation](https://redis.io/docs/stack/search/)
- [RedisJSON Documentation](https://redis.io/docs/stack/json/)
