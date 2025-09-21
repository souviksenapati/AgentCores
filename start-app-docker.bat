@echo off
REM filepath: start-app-docker.bat
echo ==========================================
echo    AgentCores MVP - Docker Setup
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
echo [3/6] Setting up environment...
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
echo [5/6] Building and starting Docker services with optimization...
cd ..
echo.
echo This will start:
echo - PostgreSQL Database
echo - Redis Cache
echo - FastAPI Backend (with hot reload)
echo - React Frontend (with hot reload)
echo.
echo Building containers with layer caching (faster after first build)...

%COMPOSE_CMD% down
%COMPOSE_CMD% build --parallel
%COMPOSE_CMD% up -d

echo.
echo [6/6] Waiting for services to initialize...
echo Checking service health...

:wait_loop
timeout /t 5 /nobreak >nul
echo Checking if services are ready...

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
echo    AgentCores MVP Started Successfully!
echo ==========================================
echo.
echo 🎯 Access your application:
echo.
echo Frontend Dashboard: http://localhost:3000 (Hot Reload Enabled)
echo Backend API Docs:   http://localhost:8000/docs (Hot Reload Enabled)
echo Interactive API:    http://localhost:8000/redoc
echo Health Check:       http://localhost:8000/health
echo.
echo 📊 Database Access:
echo PostgreSQL: localhost:5432
echo Redis: localhost:6379
echo.
echo � HOT RELOAD ACTIVE:
echo - Frontend: Code changes auto-refresh browser
echo - Backend: Code changes auto-restart server
echo - NO rebuild needed for code changes!
echo.
echo �🔧 Useful Docker commands:
echo   View logs:     %COMPOSE_CMD% logs -f
echo   Stop services: %COMPOSE_CMD% down
echo   Restart:       %COMPOSE_CMD% restart [service]
echo   Quick rebuild: %COMPOSE_CMD% build --parallel
echo.
echo Opening frontend dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo Press any key to exit (services will keep running)...
pause >nul