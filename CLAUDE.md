# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker-based Redis Stack environment for a Praxis thesis project. It provides Redis with advanced modules (RediSearch, RedisJSON) for testing and development purposes.

## Environment Setup

### Initial Setup
```bash
# Copy environment template
cp .env.example .env
# Edit .env to set REDIS_PASSWORD (required)

# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables (.env)
- `REDIS_PASSWORD`: Required - authentication password for Redis
- `REDIS_PORT`: Optional (default: 6379)
- `REDIS_HOST`: Optional (default: localhost)

## Common Commands

### Redis Container Management
```bash
# Start Redis Stack container
./scripts/start.sh

# Stop and remove Redis container
./scripts/stop.sh

# Test Redis connection and modules
python scripts/test_redis_connection.py
```

### Direct Docker Commands
```bash
# View container logs
docker logs redis-llm

# Execute Redis CLI in container
docker exec redis-llm redis-cli -a "${REDIS_PASSWORD}" ping
```

## Architecture

### Docker Setup
- **Container Name**: `redis-llm`
- **Image**: `redis/redis-stack:latest` (includes Redis core + modules)
- **Ports**:
  - 6379: Redis server (configurable via `REDIS_PORT`)
  - 8001: RedisInsight Web UI (http://localhost:8001)
- **Data Persistence**: Named volume `redis_data` mounted at `/data`
- **Configuration**: Password authentication via `REDIS_ARGS=--requirepass ${REDIS_PASSWORD}`
- **RediSearch Config**: `MAXSEARCHRESULTS 10000`

### Script Architecture

**start.sh** (scripts/start.sh):
- Validates `.env` file exists and `REDIS_PASSWORD` is set
- Changes to `docker/redis` directory to run docker-compose
- Handles both `docker compose` and legacy `docker-compose` commands
- Performs container health check with 10 retries
- Logs connection details on successful start

**stop.sh** (scripts/stop.sh):
- Gracefully stops and removes the `redis-llm` container
- Falls back through multiple stop methods (compose → direct docker)
- Performs verification that container is fully removed

**test_redis_connection.py** (scripts/test_redis_connection.py):
- Comprehensive test suite for Redis Stack functionality
- Tests basic connectivity with retry logic
- Validates RediSearch: creates index, inserts document, performs search
- Validates RedisJSON: stores JSON document, retrieves with JSON path queries
- Displays loaded modules and Redis version info
- Returns non-zero exit code on failure

**redis_client.py** (scripts/redis_client.py):
- Self-documenting modular Redis client wrapper
- `RedisConfig`: Configuration management with environment variable support
- `RedisStackClient`: High-level client for Redis, RediSearch, and RedisJSON operations
- `RedisSearchHelper`: Helper utilities for RediSearch schema and sample data
- `RedisJSONHelper`: Helper utilities for RedisJSON sample data
- Designed for testability with dependency injection and context manager support

### Python Dependencies

**Production** (requirements.txt):
- `redis>=5.2.0`: Redis client with Stack modules support (RediSearch, RedisJSON)
- `python-dotenv>=1.0.1`: Environment variable management

**Testing** (requirements.txt):
- `pytest>=8.3.0`: Test framework
- `pytest-cov>=6.0.0`: Coverage reporting
- `pytest-asyncio>=0.24.0`: Async test support
- `pytest-timeout>=2.3.1`: Test timeout management
- `pytest-mock>=3.14.0`: Mocking utilities

**Code Quality** (requirements.txt):
- `black>=24.10.0`: Code formatter
- `ruff>=0.7.0`: Fast Python linter
- `mypy>=1.13.0`: Static type checker

**Development** (requirements-dev.txt):
- Includes all production and testing dependencies
- `pytest-xdist>=3.6.1`: Parallel test execution
- `pytest-benchmark>=4.0.0`: Performance benchmarking
- `pre-commit>=4.0.1`: Git hooks for code quality

## Redis Stack Modules

This environment includes:

1. **Redis Core**: Standard key-value operations
2. **RediSearch**: Full-text search and secondary indexing
   - Used in test script with `TextField`, `NumericField`, `TagField`
   - Index created with prefix pattern `blog:`
3. **RedisJSON**: JSON document storage with path-based queries
   - Supports JSON path syntax (e.g., `$.profile.age`)
4. **RedisInsight**: Web-based GUI at http://localhost:8001

## Working with This Codebase

### Development Workflow (Using Makefile)

The project uses a Makefile for common commands. Run `make help` to see all available targets:

```bash
# Setup
make install          # Install production dependencies
make install-dev      # Install development dependencies

# Redis Container Management
make start            # Start Redis Stack
make stop             # Stop Redis Stack
make restart          # Restart Redis Stack

# Testing (Test-Driven Development)
make test             # Run all tests
make test-unit        # Run unit tests only (no Redis required)
make test-integration # Run integration tests (requires Redis)
make test-e2e         # Run end-to-end tests (requires Redis)
make test-all         # Run all tests with coverage report
make coverage         # Generate HTML coverage report and open in browser

# Code Quality
make lint             # Run all linters (black, ruff, mypy)
make format           # Auto-format code with black and ruff
make verify           # Run lint + test-all (full verification)
make ci-local         # Simulate CI pipeline locally

# Cleanup
make clean            # Remove generated files and caches
```

### Test-Driven Development Approach

The project follows TDD principles with three test layers:

**1. Unit Tests** (tests/unit/):
- Test individual components in isolation
- No external dependencies (Redis not required)
- Fast execution (< 1 second)
- Examples: `test_redis_config.py`, `test_redis_helpers.py`
- Run with: `make test-unit` or `pytest tests/unit -m unit`

**2. Integration Tests** (tests/integration/):
- Test Redis operations with a live Redis instance
- Verify RediSearch and RedisJSON functionality
- Requires Redis Stack running
- Examples: `test_redis_connection.py`, `test_redisearch.py`, `test_redisjson.py`
- Run with: `make test-integration` or `pytest tests/integration -m integration`

**3. End-to-End Tests** (tests/e2e/):
- Test complete workflows combining multiple features
- Simulate real-world usage patterns
- Examples: Blog platform workflow, user preferences, caching + search
- Run with: `make test-e2e` or `pytest tests/e2e -m e2e`

### Testing Best Practices

1. **Run unit tests first** - they're fast and catch basic issues
2. **Ensure Redis is running** before integration/e2e tests: `make start`
3. **Use markers** to run specific test types: `pytest -m unit`
4. **Check coverage** regularly: `make coverage` (aim for >80%)
5. **CI pipeline** runs automatically on push/PR to main/develop branches

### GitHub Actions CI/CD

The project includes a comprehensive CI pipeline (`.github/workflows/ci.yml`):

- **Lint Job**: Runs black, ruff, mypy on code
- **Test-Unit Job**: Runs unit tests (no Redis required)
- **Test-Integration Job**: Runs integration tests with Redis service container
- **Test-E2E Job**: Runs end-to-end tests with Redis service container
- **Test-All Job**: Runs complete test suite with combined coverage reporting

All jobs run on push/PR to main/develop branches. Coverage reports are uploaded to Codecov.

### When Modifying Code

**Scripts (scripts/):**
- Start/stop scripts use absolute paths resolved from `SCRIPT_DIR`
- Include logging functions: `log_info`, `log_error`, `log_success`, `log_debug`
- Error handling via `handle_error()` function exits with code 1
- Password preview shows first character + asterisks for security

**Redis Client (scripts/redis_client.py):**
- Uses type hints for all public methods
- Self-documenting with docstrings
- Context manager support (`with` statement)
- Dependency injection for testability
- Helper classes provide reusable test data

**Tests:**
- Use descriptive test names: `test_<what>_<condition>`
- Include docstrings explaining what is being tested
- Use fixtures from `conftest.py` for shared setup
- Clean up test data in teardown methods
- Mark tests appropriately: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`

### Code Quality Standards

1. **Formatting**: Code must pass `black --check .`
2. **Linting**: Code must pass `ruff check .`
3. **Type Checking**: Code should pass `mypy scripts/` (currently not enforced)
4. **Coverage**: Aim for >80% code coverage on new code
5. **Self-Documenting**: Use clear names, type hints, and docstrings

### Configuration Files

- **pytest.ini**: Pytest configuration, markers, coverage settings
- **pyproject.toml**: Tool configuration (black, ruff, mypy, coverage)
- **docker-compose.yml**: Located in `docker/redis/` (not project root)
- **.env**: Required for local development (copy from `.env.example`)

### Docker Compose Location

The docker-compose.yml is in `docker/redis/` directory, not the project root. The start/stop scripts handle the path navigation automatically.
