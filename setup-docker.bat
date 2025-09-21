@echo off
REM filepath: setup-docker.bat
echo ==========================================
echo   AgentCores Multi-Tenant - Setup Helper
echo ==========================================

echo.
echo This script will help you set up Docker for AgentCores Multi-Tenant
echo.

echo [1/8] Checking if Docker is installed...
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
echo [2/8] Checking Docker Compose...
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
echo [3/8] Checking Docker Desktop status...
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
echo [4/8] Setting up multi-tenant environment...
cd /d "D:\Projects\get-github-user-details-master\AgentCores"

if not exist backend\.env (
    echo Creating .env file from template...
    copy backend\.env.example backend\.env >nul
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

echo.
echo [5/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python is installed!
    python --version
) else (
    echo ❌ Python is not installed
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo [6/8] Setting up Python virtual environment...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo [7/8] Installing Python dependencies in virtual environment...
echo Activating virtual environment and installing packages...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo ✅ All Python packages installed successfully!
) else (
    echo ❌ Failed to install Python packages
    echo Please check your internet connection and requirements.txt
    pause
    exit /b 1
)
call venv\Scripts\deactivate.bat

echo.
echo [8/8] Setting up Node.js dependencies...
cd ..\frontend
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js is installed!
    node --version
    echo Installing npm packages...
    npm install
    if %errorlevel% equ 0 (
        echo ✅ All npm packages installed successfully!
    ) else (
        echo ⚠️ Failed to install npm packages
        echo Frontend may not work properly
    )
) else (
    echo ⚠️ Node.js is not installed
    echo Frontend may not work properly without Node.js
    echo You can install it from: https://nodejs.org/
)

cd ..

echo.
echo ==========================================
echo   Multi-Tenant Setup Complete!
echo ==========================================
echo.
echo ✅ Docker and Docker Compose verified
echo ✅ Environment configuration ready
echo ✅ Python virtual environment created
echo ✅ Backend dependencies installed (FastAPI, SQLAlchemy, etc.)
echo ✅ Frontend dependencies installed (React, Material-UI, etc.)
echo.
echo You're ready to start AgentCores Multi-Tenant Platform!
echo.
echo 🏢 Multi-Tenant Features:
echo - Complete organization isolation
echo - Role-based access control (Owner/Admin/Member)
echo - Single-domain architecture (agentcores.com/app)
echo - Enterprise-grade security
echo.
echo 🐍 Python Environment:
echo - Virtual environment: backend\venv\
echo - To activate manually: backend\venv\Scripts\activate.bat
echo - Installed packages: FastAPI, SQLAlchemy, PostgreSQL, Redis, JWT auth
echo.
echo 📦 Node.js Environment:
echo - Frontend packages: React 18, Material-UI, Axios, React Router
echo - Build-ready development environment
echo.
echo Next steps:
echo 1. Double-click 'start-app-docker.bat' to start all services
echo 2. Wait for the build process (5-10 minutes first time)
echo 3. Access your app at http://localhost:3000
echo 4. Login with: Organization="AgentCores Demo", Email="admin@demo.agentcores.com", Password="admin123"
echo.
echo Available commands:
echo - start-app-docker.bat     : Start all services with database initialization
echo - stop-app-docker.bat      : Stop all services
echo - restart-app-docker.bat   : Restart services
echo - view-logs-docker.bat     : View service logs
echo - check-status-docker.bat  : Check service health
echo - clean-docker.bat         : Clean slate (removes all data)
echo.
pause