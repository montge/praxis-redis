#!/bin/bash
# scripts/start.sh
# Script to start Redis container with proper configuration

# Get the absolute path to the docker/redis directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCKER_DIR="${SCRIPT_DIR}/../docker/redis"
ENV_FILE="${SCRIPT_DIR}/../.env"

# Log function for consistent output
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_debug() {
    echo "[DEBUG] $1"
}

# Error handling function
handle_error() {
    log_error "$1"
    exit 1
}

# Source the .env file to get variables
if [ -f "${ENV_FILE}" ]; then
    log_debug "Loading environment from ${ENV_FILE}"
    source "${ENV_FILE}"
else
    handle_error ".env file not found at ${ENV_FILE}"
fi

# Validate required environment variables
if [ -z "${REDIS_PASSWORD}" ]; then
    handle_error "REDIS_PASSWORD is not set in ${ENV_FILE}"
fi

if [ -z "${REDIS_PORT}" ]; then
    log_info "REDIS_PORT not set in ${ENV_FILE}, using default port 6379"
    REDIS_PORT=6379
fi

# Debug password (show first character followed by stars)
PASSWORD_LENGTH=${#REDIS_PASSWORD}
PASSWORD_PREVIEW="${REDIS_PASSWORD:0:1}$(printf '%*s' "$((PASSWORD_LENGTH-1))" | tr ' ' '*')"
log_info "Using Redis password: ${PASSWORD_PREVIEW}"

log_debug "Script directory: ${SCRIPT_DIR}"
log_debug "Docker directory: ${DOCKER_DIR}"
log_debug "Environment file: ${ENV_FILE}"

# Change to the docker/redis directory
cd "${DOCKER_DIR}" || handle_error "Failed to change to directory: ${DOCKER_DIR}"

# Stop and remove existing container if it exists
log_info "Stopping any existing Redis container..."
docker compose down 2>/dev/null || true

log_debug "Current directory: $(pwd)"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    handle_error "docker-compose.yml not found in $(pwd)"
fi

# Start Redis container
log_info "Starting Redis container..."
if command -v docker compose &> /dev/null; then
    log_debug "Using docker compose (new syntax)..."
    docker compose -f "$(pwd)/docker-compose.yml" --env-file "${ENV_FILE}" up -d || handle_error "Failed to start Redis container"
elif command -v docker-compose &> /dev/null; then
    log_debug "Using docker-compose (old syntax)..."
    docker-compose -f "$(pwd)/docker-compose.yml" --env-file "${ENV_FILE}" up -d || handle_error "Failed to start Redis container"
else
    handle_error "Neither docker compose nor docker-compose found"
fi

# Verify container is running
log_info "Verifying Redis container..."
if ! docker ps | grep -q redis-llm; then
    log_error "Redis container failed to start"
    log_debug "Checking docker logs..."
    docker logs redis-llm
    exit 1
fi

log_success "Redis container is running"

# Wait for Redis to be ready with better retry logic
log_info "Waiting for Redis to become ready..."
max_retries=10
retry_count=0
connection_successful=false

while [ $retry_count -lt $max_retries ]; do
    log_debug "Attempt $((retry_count+1))/$max_retries to connect to Redis..."
    sleep 2  # Wait between retries
    
    if docker exec redis-llm redis-cli -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q PONG; then
        connection_successful=true
        break
    fi
    
    retry_count=$((retry_count+1))
done

if [ "$connection_successful" = true ]; then
    log_success "Redis connection successful"
else
    log_error "Redis connection failed after $max_retries attempts"
    log_debug "Container logs:"
    docker logs redis-llm
    exit 1
fi

log_success "Redis server started successfully"
log_info "Redis container started. You can connect using:"
log_info "Host: ${REDIS_HOST:-localhost}"
log_info "Port: ${REDIS_PORT:-6379}" 