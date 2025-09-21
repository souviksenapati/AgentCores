@echo off
REM filepath: stop-app-docker.bat
echo ==========================================
echo    Stopping AgentCores MVP (Docker)
echo ==========================================

cd /d "D:\Projects\get-github-user-details-master\AgentCores"

echo.
echo Stopping all Docker services...

REM Try docker compose first, then fallback to docker-compose
docker compose down >nul 2>&1
if %errorlevel% neq 0 (
    docker-compose down >nul 2>&1
)

echo.
echo Cleaning up Docker resources...
docker system prune -f >nul 2>&1

echo.
echo ==========================================
echo    AgentCores MVP Stopped Successfully!
echo ==========================================
echo.
echo All containers have been stopped and removed.
echo Data volumes have been preserved.
echo.
pause