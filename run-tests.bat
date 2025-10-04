@echo off
REM AgentCores CI/CD Test Runner for Windows
REM This script runs all tests and quality checks

echo 🚀 Starting AgentCores CI/CD Pipeline...

echo 🔧 Running Backend Tests...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️ Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Code formatting check
echo ✅ Checking code formatting...
black --check --diff . 
if %errorlevel% neq 0 (
    echo ❌ Code formatting issues found. Run 'black .' to fix.
    exit /b 1
)

REM Import sorting check
echo ✅ Checking import sorting...
isort --check-only --diff .
if %errorlevel% neq 0 (
    echo ❌ Import sorting issues found. Run 'isort .' to fix.
    exit /b 1
)

REM Linting
echo ✅ Running linter...
flake8 app\ --max-line-length=88 --extend-ignore=E203,W503
if %errorlevel% neq 0 (
    echo ❌ Linting issues found.
    exit /b 1
)

REM Type checking
echo ✅ Running type checking...
mypy app\ --ignore-missing-imports

REM Security scan
echo ✅ Running security scan...
bandit -r app\ -f json -o bandit-report.json

REM Unit tests
echo ✅ Running unit tests...
pytest tests\ -v --cov=app --cov-report=html
if %errorlevel% neq 0 (
    echo ❌ Backend tests failed.
    exit /b 1
)

cd ..

echo 🎨 Running Frontend Tests...
cd frontend

REM Install dependencies
call npm ci

REM Linting
echo ✅ Running ESLint...
call npm run lint
if %errorlevel% neq 0 (
    echo ❌ Frontend linting issues found.
    exit /b 1
)

REM Format check
echo ✅ Checking code formatting...
call npm run format:check
if %errorlevel% neq 0 (
    echo ❌ Frontend formatting issues found. Run 'npm run format' to fix.
    exit /b 1
)

REM Unit tests
echo ✅ Running frontend tests...
call npm run test:ci
if %errorlevel% neq 0 (
    echo ❌ Frontend tests failed.
    exit /b 1
)

REM Build test
echo ✅ Testing frontend build...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Frontend build failed.
    exit /b 1
)

cd ..

echo 🔄 Running Integration Tests...
echo ✅ Starting services for integration tests...

REM Start services in background
docker-compose up -d

REM Wait for services to be ready
timeout /t 30

REM Run basic health checks
echo ✅ Running health checks...
curl --fail http://localhost:8000/health
if %errorlevel% neq 0 (
    echo ❌ Backend health check failed.
    docker-compose down
    exit /b 1
)

curl --fail http://localhost:3000
if %errorlevel% neq 0 (
    echo ❌ Frontend health check failed.
    docker-compose down
    exit /b 1
)

REM Cleanup
echo ✅ Cleaning up test environment...
docker-compose down

echo ✅ 🎉 All tests passed! CI/CD pipeline completed successfully.