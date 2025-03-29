## Redis Stack Environment for Thesis Project

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
- `scripts/test_redis_connection.py`: Test Redis connectivity and functionality

### Redis Stack Features

This setup includes:
- Redis core functionality
- RediSearch for advanced search capabilities
- RedisJSON for JSON document storage
- RedisInsight Web UI accessible at http://localhost:8001 