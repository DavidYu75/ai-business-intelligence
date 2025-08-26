# Makefile for Real-Time BI Platform Development

.PHONY: help up down build logs clean test lint test-backend test-frontend ci-cd

# Default target
help:
	@echo "Real-Time BI Platform Development Commands"
	@echo "=========================================="
	@echo "up          - Start all services"
	@echo "down        - Stop all services"
	@echo "build       - Build all Docker images"
	@echo "logs        - Show logs from all services"
	@echo "clean       - Stop services and remove volumes"
	@echo "test        - Run Docker setup test"
	@echo "backend     - Start only backend service"
	@echo "frontend    - Start only frontend service"
	@echo "db          - Access PostgreSQL database"
	@echo "redis       - Access Redis CLI"
	@echo ""
	@echo "Development Commands:"
	@echo "lint         - Run linting on all code"
	@echo "test-backend - Run backend tests"
	@echo "test-frontend- Run frontend tests"
	@echo "ci-cd        - Run full CI/CD pipeline locally"

# Start all services
up:
	docker-compose up

# Start services in background
up-d:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Build all images
build:
	docker-compose build

# Show logs
logs:
	docker-compose logs

# Follow logs
logs-f:
	docker-compose logs -f

# Clean up (stop and remove volumes)
clean:
	docker-compose down -v

# Test Docker setup
test:
	./scripts/test-docker-setup.sh

# Start only backend
backend:
	docker-compose up backend

# Start only frontend
frontend:
	docker-compose up frontend

# Access PostgreSQL
db:
	docker-compose exec postgres psql -U realtime_bi_user -d realtime_bi

# Access Redis
redis:
	docker-compose exec redis redis-cli

# Rebuild specific service
rebuild-backend:
	docker-compose build --no-cache backend

rebuild-frontend:
	docker-compose build --no-cache frontend

# Show service status
status:
	docker-compose ps

# Development Commands

# Run linting
lint:
	@echo "Running backend linting..."
	cd backend && black --check --diff .
	cd backend && isort --check-only --diff .
	cd backend && flake8 .
	cd backend && mypy .
	@echo "Running frontend linting..."
	cd frontend && npm run lint
	cd frontend && npm run format:check
	cd frontend && npm run type-check

# Run backend tests
test-backend:
	@echo "Running backend tests..."
	cd backend && pytest --cov=app --cov-report=term-missing

# Run frontend tests
test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test:coverage

# Run full CI/CD pipeline locally
ci-cd: lint test-backend test-frontend
	@echo "CI/CD pipeline completed successfully!"

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files

# Security scanning
security-scan:
	@echo "Running security scan..."
	cd backend && bandit -r .
	@echo "Security scan completed!"
