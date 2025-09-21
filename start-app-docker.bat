@echo off
REM filepath: start-app-docker.bat
echo ==========================================
echo   AgentCores Multi-Tenant - Docker Setup
echo ==========================================

echo.
echo [1/6] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo Docker found! Version:
docker --version

echo.
echo [2/6] Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo Trying legacy docker-compose...
    docker-compose --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Docker Compose is not available
        echo Please ensure Docker Desktop is running
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

echo Docker Compose found!

echo.
echo [3/6] Setting up multi-tenant environment...
cd /d "D:\Projects\get-github-user-details-master\AgentCores"

echo.
echo [4/6] Creating .env file from template...
cd backend
if not exist .env (
    copy .env.example .env
    echo .env file created from template
) else (
    echo .env file already exists
)

echo.
echo [5/6] Building and starting Multi-Tenant Docker services...
cd ..
echo.
echo This will start:
echo - PostgreSQL Database (Multi-tenant with isolation)
echo - Redis Cache
echo - Database Initialization Service (Sets up default tenant)
echo - FastAPI Backend (Multi-tenant API with JWT auth)
echo - React Frontend (Single-domain multi-tenant UI)
echo.
echo Building containers with layer caching...

%COMPOSE_CMD% down
%COMPOSE_CMD% build --parallel
%COMPOSE_CMD% up -d

echo.
echo [6/6] Waiting for multi-tenant services to initialize...
echo Checking database initialization and service health...

:wait_loop
timeout /t 5 /nobreak >nul
echo Checking if multi-tenant services are ready...

REM Check if backend is responding
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend is ready!
    goto services_ready
)

echo Still waiting for services to start...
goto wait_loop

:services_ready
echo.
echo ==========================================
echo   AgentCores Multi-Tenant Started!
echo ==========================================
echo.
echo 🎯 Access your multi-tenant application:
echo.
echo Frontend Dashboard: http://localhost:3000
echo Backend API Docs:   http://localhost:8000/docs
echo Interactive API:    http://localhost:8000/redoc
echo Health Check:       http://localhost:8000/health
echo.
echo 🏢 Default Organization Login:
echo Organization: AgentCores Demo
echo Email:        admin@demo.agentcores.com
echo Password:     admin123
echo Role:         Owner (Full Access)
echo.
echo ⚠️  IMPORTANT: Change the default password after first login!
echo.
echo 📊 Database Access:
echo PostgreSQL: localhost:5432 (Multi-tenant with row-level security)
echo Redis: localhost:6379
echo.
echo 🔒 Multi-Tenant Features Active:
echo - Complete organization isolation
echo - Role-based access control
echo - JWT authentication with tenant context
echo - Single-domain architecture
echo - Enterprise-grade security
echo.
echo 🔧 Useful Docker commands:
echo   View logs:     %COMPOSE_CMD% logs -f
echo   Stop services: %COMPOSE_CMD% down
echo   Restart:       %COMPOSE_CMD% restart [service]
echo   Clean start:   clean-docker.bat
echo.
echo Opening multi-tenant dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo Press any key to exit (services will keep running)...
pause >nul