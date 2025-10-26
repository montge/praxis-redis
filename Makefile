.PHONY: help install install-dev start stop restart test test-unit test-integration test-e2e test-all lint format clean coverage

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Redis Stack Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -r requirements-dev.txt

start: ## Start Redis Stack container
	@echo "$(BLUE)Starting Redis Stack...$(NC)"
	./scripts/start.sh

stop: ## Stop Redis Stack container
	@echo "$(BLUE)Stopping Redis Stack...$(NC)"
	./scripts/stop.sh

restart: stop start ## Restart Redis Stack container

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit -v -m unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration -v -m integration

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	pytest tests/e2e -v -m e2e

test-all: ## Run all tests with coverage
	@echo "$(BLUE)Running all tests with coverage...$(NC)"
	pytest -v --cov=scripts --cov-report=html --cov-report=term-missing

coverage: ## Generate and open coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	pytest --cov=scripts --cov-report=html
	@echo "$(GREEN)Opening coverage report in browser...$(NC)"
	@which open > /dev/null && open htmlcov/index.html || xdg-open htmlcov/index.html || echo "Please open htmlcov/index.html manually"

lint: ## Run code quality checks
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "$(YELLOW)Black (formatter check)...$(NC)"
	black --check .
	@echo "$(YELLOW)Ruff (linter)...$(NC)"
	ruff check .
	@echo "$(YELLOW)MyPy (type checker)...$(NC)"
	mypy scripts/ --ignore-missing-imports

format: ## Format code with Black and Ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	black .
	ruff check --fix .

clean: ## Clean up generated files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage coverage.xml
	@echo "$(GREEN)Cleanup complete!$(NC)"

verify: lint test-all ## Run all verification checks (lint + test)
	@echo "$(GREEN)All verification checks passed!$(NC)"

ci-local: ## Simulate CI pipeline locally
	@echo "$(BLUE)Running CI pipeline locally...$(NC)"
	@make lint
	@make test-all
	@echo "$(GREEN)Local CI pipeline complete!$(NC)"
