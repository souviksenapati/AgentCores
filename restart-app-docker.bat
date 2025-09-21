@echo off
REM filepath: restart-app-docker.bat
echo ==========================================
echo  Restarting AgentCores Multi-Tenant (Docker)
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
echo 🔄 Restarting all multi-tenant services...
%COMPOSE_CMD% restart

echo.
echo ⏳ Waiting for multi-tenant stack to be ready...
timeout /t 15 /nobreak >nul

echo.
echo ==========================================
echo  AgentCores Multi-Tenant Restarted! 
echo ==========================================
echo.
echo 🌐 Frontend: http://localhost:3000/app
echo 📚 Backend:  http://localhost:8000/docs
echo 💾 Database: PostgreSQL with tenant isolation
echo.
echo 🏢 Default Login:
echo    Organization: "AgentCores Demo" 
echo    Email: "admin@demo.agentcores.com"
echo    Password: "admin123"
echo.
echo 🚀 Your multi-tenant AgentCores is ready!
echo    Create organizations, invite users, manage agents.
echo.
pause