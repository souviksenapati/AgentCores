@echo off
REM filepath: restart-app-docker.bat
echo ==========================================
echo    Restarting AgentCores MVP (Docker)
echo ==========================================

cd /d "D:\Projects\get-github-user-details-master\AgentCores"

REM Try docker compose first, then fallback to docker-compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

echo.
echo Restarting all services...
%COMPOSE_CMD% restart

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ==========================================
echo    AgentCores MVP Restarted Successfully!
echo ==========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000/docs
echo.
pause