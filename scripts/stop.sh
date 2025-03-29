#!/bin/bash
# scripts/stop.sh
# Script to stop Redis container

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

# Source the .env file to get variables if needed
if [ -f "${ENV_FILE}" ]; then
    log_debug "Loading environment from ${ENV_FILE}"
    source "${ENV_FILE}"
else
    log_debug ".env file not found at ${ENV_FILE}, continuing without it"
fi

# Change to the docker/redis directory
cd "${DOCKER_DIR}" || handle_error "Failed to change to directory: ${DOCKER_DIR}"

log_info "Stopping Redis container..."

# Try docker compose first (new syntax)
if docker compose version &> /dev/null; then
    log_debug "Using docker compose..."
    docker compose -f "$(pwd)/docker-compose.yml" down || handle_error "Failed to stop Redis container with docker compose"
# Then try docker-compose (old syntax)
elif docker-compose version &> /dev/null; then
    log_debug "Using docker-compose..."
    docker-compose -f "$(pwd)/docker-compose.yml" down || handle_error "Failed to stop Redis container with docker-compose"
# Finally fall back to direct docker commands
else
    log_debug "Using direct docker commands..."
    # Stop the container if it exists
    if docker ps -q -f name=redis-llm &> /dev/null; then
        docker stop redis-llm || handle_error "Failed to stop Redis container"
        docker rm redis-llm || handle_error "Failed to remove Redis container"
    else
        log_info "No Redis container found running"
    fi
fi

# Double check if container still exists
if docker ps -a | grep -q redis-llm; then
    log_info "Container still exists, forcing removal..."
    docker stop redis-llm 2>/dev/null || true
    docker rm redis-llm 2>/dev/null || true
    
    # Final check
    if docker ps -a | grep -q redis-llm; then
        handle_error "Failed to remove Redis container after force attempt"
    fi
fi

# Verify container is gone
if ! docker ps -a | grep -q redis-llm; then
    log_success "Redis container successfully stopped and removed"
else
    handle_error "Failed to remove Redis container"
fi 