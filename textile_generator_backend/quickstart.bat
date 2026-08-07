@echo off
REM Quick start script for development (Windows)

setlocal enabledelayedexpansion

echo.
echo ===== Textile Pattern Generator - Quick Start =====
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found

REM Create venv
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate venv
echo [3/6] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo ✓ Dependencies installed

REM Setup environment
echo [4/6] Setting up configuration...
if not exist ".env" (
    copy .env.example .env
    echo ✓ Created .env from template (update with your settings)
) else (
    echo ✓ .env already exists
)

REM Initialize database
echo [5/6] Initializing database...
python init_db.py --init >nul 2>&1
echo ✓ Database initialized

echo.
echo ===== Setup Complete! =====
echo.
echo Next steps:
echo 1. Make sure PostgreSQL is running
echo 2. Update .env if needed (DB credentials, model path)
echo 3. Run: python app.py
echo 4. Visit: http://localhost:5000
echo.
echo First API call to generate:
echo curl -X POST http://localhost:5000/api/generate ^
echo   -H "Content-Type: application/json" ^
echo   -d "{\"prompt\": \"geometric pattern\", \"style\": \"block_print\"}"
echo.
pause
