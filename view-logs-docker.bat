@echo off
REM filepath: view-logs-docker.bat
echo ==========================================
echo  AgentCores Multi-Tenant - Docker Logs
echo ==========================================

cd /d "D:\Projects\get-github-user-details-master\AgentCores"

echo.
echo Choose which logs to view:
echo.
echo 1. All services (multi-tenant stack)
echo 2. Backend only (API + auth)
echo 3. Frontend only (React app)
echo 4. Database only (PostgreSQL + multi-tenant data)
echo 5. Live tail all logs (real-time monitoring)
echo 6. Redis only (sessions + cache)
echo.
set /p choice="Enter your choice (1-6): "

REM Try docker compose first, then fallback to docker-compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

if "%choice%"=="1" (
    echo.
    echo 📋 Showing logs for all multi-tenant services...
    %COMPOSE_CMD% logs
) else if "%choice%"=="2" (
    echo.
    echo 🖥️ Showing backend logs (FastAPI + multi-tenant auth)...
    %COMPOSE_CMD% logs backend
) else if "%choice%"=="3" (
    echo.
    echo 🌐 Showing frontend logs (React + organization login)...
    %COMPOSE_CMD% logs frontend
) else if "%choice%"=="4" (
    echo.
    echo 🗄️ Showing database logs (PostgreSQL + tenant isolation)...
    %COMPOSE_CMD% logs postgres
) else if "%choice%"=="5" (
    echo.
    echo 🔄 Following live logs (Ctrl+C to stop)...
    echo Monitoring multi-tenant operations in real-time...
    %COMPOSE_CMD% logs -f
) else if "%choice%"=="6" (
    echo.
    echo 💾 Showing Redis logs (sessions + cache)...
    %COMPOSE_CMD% logs redis
) else (
    echo.
    echo ❌ Invalid choice. Showing all multi-tenant logs...
    %COMPOSE_CMD% logs
)

echo.
echo 💡 Tip: Look for tenant-specific operations in the logs!
echo Organization context is included in most log entries.
echo.
pause