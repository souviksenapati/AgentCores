@echo off
REM filepath: view-logs-docker.bat
echo ==========================================
echo    AgentCores MVP - Docker Logs
echo ==========================================

cd /d "D:\Projects\get-github-user-details-master\AgentCores"

echo.
echo Choose which logs to view:
echo.
echo 1. All services
echo 2. Backend only
echo 3. Frontend only
echo 4. Database only
echo 5. Live tail all logs
echo.
set /p choice="Enter your choice (1-5): "

REM Try docker compose first, then fallback to docker-compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

if "%choice%"=="1" (
    %COMPOSE_CMD% logs
) else if "%choice%"=="2" (
    %COMPOSE_CMD% logs backend
) else if "%choice%"=="3" (
    %COMPOSE_CMD% logs frontend
) else if "%choice%"=="4" (
    %COMPOSE_CMD% logs postgres
) else if "%choice%"=="5" (
    echo Press Ctrl+C to stop following logs...
    %COMPOSE_CMD% logs -f
) else (
    echo Invalid choice. Showing all logs...
    %COMPOSE_CMD% logs
)

echo.
pause