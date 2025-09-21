@echo off
REM filepath: check-status-docker.bat
echo ==========================================
echo    AgentCores MVP - Service Status
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
echo Checking Docker services status...
echo.

%COMPOSE_CMD% ps

echo.
echo ==========================================
echo    Service Health Checks
echo ==========================================
echo.

echo Testing Backend API...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API: HEALTHY
) else (
    echo ❌ Backend API: NOT RESPONDING
)

echo.
echo Testing Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend: HEALTHY
) else (
    echo ❌ Frontend: NOT RESPONDING
)

echo.
echo Testing Database...
docker exec agentcores_postgres_1 pg_isready -U agent_user >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL: HEALTHY
) else (
    echo ❌ PostgreSQL: NOT RESPONDING
)

echo.
echo Testing Redis...
docker exec agentcores_redis_1 redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis: HEALTHY
) else (
    echo ❌ Redis: NOT RESPONDING
)

echo.
echo ==========================================
echo    Quick Access URLs
echo ==========================================
echo.
echo Frontend Dashboard: http://localhost:3000
echo Backend API Docs:   http://localhost:8000/docs
echo Health Check:       http://localhost:8000/health
echo.
pause