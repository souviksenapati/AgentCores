@echo off
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
echo 📋 Checking multi-tenant Docker services status...
echo.

%COMPOSE_CMD% ps

echo.
echo ==========================================
echo     Multi-Tenant Service Health Checks
echo ==========================================
echo.

echo 🔍 Testing Backend API (multi-tenant auth)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API: HEALTHY (Multi-tenant auth ready)
) else (
    echo ❌ Backend API: NOT RESPONDING
)

echo.
echo 🔍 Testing Frontend (organization login)...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend: HEALTHY (Single-domain multi-tenant)
) else (
    echo ❌ Frontend: NOT RESPONDING
)

echo.
echo 🔍 Testing Database (tenant isolation)...
docker exec agentcores_postgres_1 pg_isready -U agent_user >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL: HEALTHY (Multi-tenant models ready)
) else (
    echo ❌ PostgreSQL: NOT RESPONDING
)

echo.
echo 🔍 Testing Redis (session management)...
docker exec agentcores_redis_1 redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis: HEALTHY (Session storage ready)
) else (
    echo ❌ Redis: NOT RESPONDING
)

echo.
echo ==========================================
echo      Multi-Tenant Quick Access
echo ==========================================
echo.
echo 🌐 Frontend Dashboard: http://localhost:3000/app
echo 📚 Backend API Docs:   http://localhost:8000/docs
echo 🔍 Health Check:       http://localhost:8000/health
echo.
echo 🏢 Default Organization Login:
echo    Organization: "AgentCores Demo"
echo    Email: "admin@demo.agentcores.com" 
echo    Password: "admin123"
echo.
echo 💡 Create new organizations and invite users!
echo    Each organization has complete tenant isolation.
echo.
pause