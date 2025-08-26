#!/bin/bash

# Test script for Docker development environment setup
# This script verifies that all Docker configurations are correct

set -e

echo "🧪 Testing Docker Development Environment Setup"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

echo "✅ docker-compose.yml found"

# Check if Dockerfiles exist
if [ ! -f "backend/Dockerfile.dev" ]; then
    echo "❌ backend/Dockerfile.dev not found"
    exit 1
fi

if [ ! -f "frontend/Dockerfile.dev" ]; then
    echo "❌ frontend/Dockerfile.dev not found"
    exit 1
fi

echo "✅ Dockerfiles found"

# Check if required files exist
if [ ! -f "backend/requirements/base.txt" ]; then
    echo "❌ backend/requirements/base.txt not found"
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    echo "❌ frontend/package.json not found"
    exit 1
fi

if [ ! -f "backend/app/main.py" ]; then
    echo "❌ backend/app/main.py not found"
    exit 1
fi

if [ ! -f "frontend/src/pages/index.tsx" ]; then
    echo "❌ frontend/src/pages/index.tsx not found"
    exit 1
fi

echo "✅ Required application files found"

# Validate docker-compose.yml syntax
if docker-compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml syntax is valid"
else
    echo "❌ docker-compose.yml syntax is invalid"
    docker-compose config
    exit 1
fi

echo ""
echo "🎉 All tests passed! Your Docker development environment is ready."
echo ""
echo "To start the development environment:"
echo "  docker-compose up"
echo ""
echo "To access the services:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo ""
