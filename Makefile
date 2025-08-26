# Makefile for Real-Time BI Platform Development

.PHONY: help up down build logs clean test

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
