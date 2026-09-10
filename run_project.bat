@echo off
title Smart Textile AI Pattern Studio Launcher
echo ========================================================
echo   Starting Smart Textile AI Pattern Studio
echo ========================================================
echo.

echo Starting Flask Backend on http://localhost:8000 ...
if exist "%~dp0textile_generator_backend\.venv\Scripts\python.exe" (
    start "Backend Server (Flask API)" cmd /k "cd /d "%~dp0textile_generator_backend" && .venv\Scripts\python.exe app.py"
) else (
    start "Backend Server (Flask API)" cmd /k "cd /d "%~dp0textile_generator_backend" && venv\Scripts\python.exe app.py"
)

echo Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak >nul

echo Starting Vite Frontend on http://localhost:5173 ...
start "Frontend Server (React Vite)" cmd /k "cd /d "%~dp0textile_generator_frontend" && npm run dev"

echo.
echo ========================================================
echo   Both servers are starting in separate windows!
echo   Frontend App: http://localhost:5173
echo   Backend API:  http://localhost:8000
echo ========================================================
echo.
pause
