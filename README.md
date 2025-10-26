## Redis Stack Environment for Praxis Project

This repository contains a Docker-based Redis Stack environment with tools for testing and development.

### Setup Instructions

1. Make sure you have Docker and Docker Compose installed
2. Copy the .env.example to .env and set your desired password:
    ```bash
    cp .env.example .env
    # Edit .env with your preferred settings
    ```
3. Set up a virtual environment and install Python dependencies:
    ```bash
    # Create virtual environment
    python -m venv .venv
    
    # Activate virtual environment
    # On Linux/Mac:
    source .venv/bin/activate
    # On Windows:
    # .venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```
4. Start the Redis server:
    ```bash
    ./scripts/start.sh
    ```
5. Test the Redis connection:
    ```bash
    python scripts/test_redis_connection.py
    ```
6. When finished, stop the Redis server:
    ```bash
    ./scripts/stop.sh
    ```

### Environment Configuration

The `.env` file contains the following configuration:
- `REDIS_PASSWORD`: Secure password for Redis
- `REDIS_PORT`: The port Redis will run on (default: 6379)
- `REDIS_HOST`: The host Redis will run on (default: localhost)

### Available Scripts

- `scripts/start.sh`: Starts the Redis container
- `scripts/stop.sh`: Stops and removes the Redis container
- `scripts/test_redis_connection.py`: Legacy Redis connectivity test
- `scripts/redis_client.py`: Modular Redis client library for programmatic access

### Quick Commands (Using Makefile)

```bash
make help             # Show all available commands
make start            # Start Redis Stack
make stop             # Stop Redis Stack
make test             # Run all tests
make test-unit        # Run unit tests (fast, no Redis required)
make test-integration # Run integration tests (requires Redis)
make lint             # Check code quality
make format           # Auto-format code
make coverage         # Generate coverage report
```

### Redis Stack Features

This setup includes:
- Redis core functionality
- RediSearch for advanced search capabilities
- RedisJSON for JSON document storage
- RedisInsight Web UI accessible at http://localhost:8001

## Testing

This project follows **Test-Driven Development (TDD)** principles with comprehensive test coverage:

### Test Structure

- **Unit Tests** (`tests/unit/`): Fast, isolated tests without external dependencies
- **Integration Tests** (`tests/integration/`): Tests requiring a running Redis instance
- **End-to-End Tests** (`tests/e2e/`): Complete workflow tests

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit        # Unit tests only (no Redis required)
make test-integration # Integration tests (requires Redis)
make test-e2e         # End-to-end tests (requires Redis)

# Run with coverage
make test-all         # All tests with coverage report
make coverage         # Generate HTML coverage report
```

### Continuous Integration

The project includes GitHub Actions workflows that automatically run:
- Code quality checks (black, ruff, mypy)
- Unit tests (no external dependencies)
- Integration tests (with Redis service container)
- End-to-end tests (with Redis service container)
- Coverage reporting

All tests run on push/pull requests to `main` and `develop` branches.

## Development

### Code Quality

```bash
make lint             # Run all linters
make format           # Auto-format code
make verify           # Run lint + all tests
```

### Local Development Workflow

1. Create a feature branch
2. Write tests first (TDD approach)
3. Implement functionality
4. Run `make verify` to ensure quality
5. Commit and push (CI will run automatically)

## Attribution

This project includes code that was generated or assisted by AI tools including [Cursor AI](https://cursor.ai/) and [Claude Code](https://claude.ai/code).
