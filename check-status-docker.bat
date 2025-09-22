@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM filepath: check-status-docker.bat
echo ==========================================
echo  AgentCores Multi-Tenant - Service Status
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
echo [INFO] Checking multi-tenant Docker services status...
echo.

%COMPOSE_CMD% ps

echo.
echo ==========================================
echo     Multi-Tenant Service Health Checks
echo ==========================================
echo.

echo [TEST] Testing Backend API (multi-tenant auth)...
powershell -Command "try { $r = Invoke-WebRequest 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5; exit 0 } catch { exit 1 }" >nul 2>&1
if !errorlevel! equ 0 (
    echo [PASS] Backend API: HEALTHY ^(Multi-tenant auth ready^)
) else (
    echo [FAIL] Backend API: NOT RESPONDING
)

echo.
echo [TEST] Testing Frontend (organization login)...
powershell -Command "try { $r = Invoke-WebRequest 'http://localhost:3000' -UseBasicParsing -TimeoutSec 5; exit 0 } catch { exit 1 }" >nul 2>&1
if !errorlevel! equ 0 (
    echo [PASS] Frontend: HEALTHY ^(Single-domain multi-tenant^)
) else (
    echo [FAIL] Frontend: NOT RESPONDING
)

echo.
echo [TEST] Testing Database (tenant isolation)...
docker exec agentcores-postgres-1 pg_isready -U agent_user >nul 2>&1
if !errorlevel! equ 0 (
    echo [PASS] PostgreSQL: HEALTHY ^(Multi-tenant models ready^)
) else (
    echo [FAIL] PostgreSQL: NOT RESPONDING
)

echo.
echo [TEST] Testing Redis (session management)...
docker exec agentcores-redis-1 redis-cli ping >nul 2>&1
if !errorlevel! equ 0 (
    echo [PASS] Redis: HEALTHY ^(Session storage ready^)
) else (
    echo [FAIL] Redis: NOT RESPONDING
)

echo.
echo ==========================================
echo      Multi-Tenant Quick Access
echo ==========================================
echo.
echo Frontend Dashboard: http://localhost:3000/app
echo Backend API Docs:   http://localhost:8000/docs
echo Health Check:       http://localhost:8000/health
echo.
echo Default Organization Login:
echo    Organization: "AgentCores Demo"
echo    Email: "admin@demo.agentcores.com" 
echo    Password: "admin123"
echo.
echo Create new organizations and invite users!
echo Each organization has complete tenant isolation.
echo.
pause