@echo off
REM filepath: setup-docker.bat
echo ==========================================
echo    AgentCores MVP - Docker Setup Helper
echo ==========================================

echo.
echo This script will help you set up Docker for AgentCores MVP
echo.

echo [1/4] Checking if Docker is installed...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed!
    docker --version
    goto check_compose
) else (
    echo ❌ Docker is not installed
    echo.
    echo Please install Docker Desktop:
    echo 1. Go to: https://www.docker.com/products/docker-desktop/
    echo 2. Download Docker Desktop for Windows
    echo 3. Install and restart your computer
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

:check_compose
echo.
echo [2/4] Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose is available!
    docker compose version
) else (
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Legacy docker-compose is available!
        docker-compose --version
    ) else (
        echo ❌ Docker Compose is not available
        echo Please ensure Docker Desktop is running
        pause
        exit /b 1
    )
)

echo.
echo [3/4] Checking Docker Desktop status...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Desktop is running!
) else (
    echo ❌ Docker Desktop is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo.
echo [4/4] Setting up project environment...
cd /d "D:\Projects\get-github-user-details-master\AgentCores"

if not exist backend\.env (
    echo Creating .env file from template...
    copy backend\.env.example backend\.env >nul
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

echo.
echo ==========================================
echo    Docker Setup Complete!
echo ==========================================
echo.
echo You're ready to start AgentCores MVP!
echo.
echo Next steps:
echo 1. Double-click 'start-app-docker.bat' to start all services
echo 2. Wait for the build process (5-10 minutes first time)
echo 3. Access your app at http://localhost:3000
echo.
echo Available commands:
echo - start-app-docker.bat     : Start all services
echo - stop-app-docker.bat      : Stop all services
echo - restart-app-docker.bat   : Restart services
echo - view-logs-docker.bat     : View service logs
echo - check-status-docker.bat  : Check service health
echo.
pause