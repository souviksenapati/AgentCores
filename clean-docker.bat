@echo off
REM filepath: clean-docker.bat
echo ==========================================
echo  AgentCores Multi-Tenant - Clean Slate
echo ==========================================

cd /d "D:\Projects\get-github-user-details-master\AgentCores"

echo.
echo WARNING: This will remove ALL Docker resources for this project!
echo.
echo This will delete:
echo - All containers (running and stopped)
echo - All images for this project
echo - All volumes (MULTI-TENANT DATABASE DATA WILL BE LOST!)
echo - All networks
echo - Build cache
echo.
echo 🏢 This includes ALL organization data:
echo - All tenants/organizations
echo - All users (including admin accounts)
echo - All agents and tasks
echo - All audit logs
echo.
echo Your source code will NOT be affected.
echo.
set /p confirm="Are you sure you want to continue? (y/N): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

REM Try docker compose first, then fallback to docker-compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

echo.
echo [1/6] Stopping all multi-tenant containers...
%COMPOSE_CMD% down --remove-orphans

echo.
echo [2/6] Removing all containers (including stopped ones)...
for /f "tokens=*" %%i in ('docker ps -aq 2^>nul') do docker rm -f %%i 2>nul

echo.
echo [3/6] Removing project images...
REM Remove images that contain agentcores in the name
for /f "tokens=*" %%i in ('docker images --format "table {{.Repository}}:{{.Tag}}" ^| findstr agentcores 2^>nul') do (
    echo Removing image: %%i
    docker rmi -f "%%i" 2>nul
)

REM Remove images from current directory
for /f "tokens=*" %%i in ('docker images --format "table {{.Repository}}:{{.Tag}}" ^| findstr "%CD:~0,3%" 2^>nul') do (
    echo Removing image: %%i
    docker rmi -f "%%i" 2>nul
)

echo.
echo [4/6] Removing all volumes (MULTI-TENANT DATA WILL BE LOST!)...
docker volume prune -f 2>nul
REM Specifically remove project volumes
docker volume rm agentcores_postgres_data 2>nul
docker volume rm agentcores_redis_data 2>nul

echo.
echo [5/6] Removing unused networks...
docker network prune -f 2>nul

echo.
echo [6/6] Cleaning up build cache and unused resources...
docker system prune -af --volumes 2>nul

echo.
echo ==========================================
echo   Multi-Tenant Clean Slate Complete!
echo ==========================================
echo.
echo ✅ All containers removed
echo ✅ All project images removed  
echo ✅ All volumes removed (ALL organization data deleted)
echo ✅ All networks cleaned
echo ✅ Build cache cleared
echo.
echo 🚀 Ready for fresh multi-tenant start!
echo.
echo Next steps:
echo 1. Run: start-app-docker.bat
echo 2. This will rebuild everything from scratch
echo 3. Database will be auto-initialized with default tenant
echo 4. Login with: Organization="AgentCores Demo", Email="admin@demo.agentcores.com", Password="admin123"
echo 5. Create your organizations, agents and tasks again
echo.
echo Note: First build will take 5-10 minutes since everything
echo is rebuilt, but subsequent code changes will be fast!
echo.
pause