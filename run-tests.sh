#!/bin/bash

# AgentCores CI/CD Test Runner
# This script runs all tests and quality checks

set -e

echo "🚀 Starting AgentCores CI/CD Pipeline..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Backend Tests
echo "🔧 Running Backend Tests..."
cd backend

# Install dependencies if needed
if [ ! -d "venv" ]; then
    print_warning "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Code formatting check
print_status "Checking code formatting..."
black --check --diff . || (print_error "Code formatting issues found. Run 'black .' to fix." && exit 1)

# Import sorting check
print_status "Checking import sorting..."
isort --check-only --diff . || (print_error "Import sorting issues found. Run 'isort .' to fix." && exit 1)

# Linting
print_status "Running linter..."
flake8 app/ --max-line-length=88 --extend-ignore=E203,W503 || (print_error "Linting issues found." && exit 1)

# Type checking
print_status "Running type checking..."
mypy app/ --ignore-missing-imports || print_warning "Type checking completed with warnings"

# Security scan
print_status "Running security scan..."
bandit -r app/ -f json -o bandit-report.json || print_warning "Security scan completed with warnings"

# Unit tests
print_status "Running unit tests..."
pytest tests/ -v --cov=app --cov-report=html || (print_error "Backend tests failed." && exit 1)

cd ..

# Frontend Tests
echo "🎨 Running Frontend Tests..."
cd frontend

# Install dependencies
npm ci

# Linting
print_status "Running ESLint..."
npm run lint || (print_error "Frontend linting issues found." && exit 1)

# Format check
print_status "Checking code formatting..."
npm run format:check || (print_error "Frontend formatting issues found. Run 'npm run format' to fix." && exit 1)

# Unit tests
print_status "Running frontend tests..."
npm run test:ci || (print_error "Frontend tests failed." && exit 1)

# Build test
print_status "Testing frontend build..."
npm run build || (print_error "Frontend build failed." && exit 1)

cd ..

# Integration Tests
echo "🔄 Running Integration Tests..."
print_status "Starting services for integration tests..."

# Start services in background
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run basic health checks
print_status "Running health checks..."
curl --fail http://localhost:8000/health || (print_error "Backend health check failed." && exit 1)
curl --fail http://localhost:3000 || (print_error "Frontend health check failed." && exit 1)

# Cleanup
print_status "Cleaning up test environment..."
docker-compose down

print_status "🎉 All tests passed! CI/CD pipeline completed successfully."