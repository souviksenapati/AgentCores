@echo off
REM filepath: stop-app-docker.bat
echo ==========================================
echo  Stopping AgentCores Multi-Tenant (Docker)
echo ==========================================

cd /d "D:\Projects\get-github-user-details-master\AgentCores"

echo.
echo Stopping all multi-tenant Docker services...

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
echo   AgentCores Multi-Tenant Stopped!
echo ==========================================
echo.
echo ✅ All containers have been stopped and removed
echo ✅ Data volumes have been preserved (organization data safe)
echo.
echo 🏢 Your multi-tenant data is preserved:
echo - All organizations/tenants
echo - All users and roles
echo - All agents and tasks
echo - All audit logs
echo.
echo To restart: run start-app-docker.bat
echo To clean slate: run clean-docker.bat (WARNING: deletes all data)
echo.
pause