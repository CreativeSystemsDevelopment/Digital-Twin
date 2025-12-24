@echo off
REM Digital Twin - Startup Script for Windows

echo ================================================================
echo         Digital Twin - Starting Application (Windows)
echo ================================================================
echo.

REM Check if setup has been run
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run setup.bat first
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not found. Please run setup.bat first
    pause
    exit /b 1
)

REM Check if pnpm is available, if not use npm
where pnpm >nul 2>&1
if errorlevel 1 (
    set PACKAGE_MANAGER=npm
) else (
    set PACKAGE_MANAGER=pnpm
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Start Backend
echo [1/2] Starting Backend (FastAPI on port 8000)...
REM Note: Windows version uses simplified health checking compared to Linux
start "Digital Twin Backend" /MIN cmd /c ".venv\Scripts\activate.bat && uvicorn src.digital_twin.app:app --reload --host 0.0.0.0 --port 8000 > logs\backend.log 2>&1"
echo SUCCESS: Backend started (check logs\backend.log for status)

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/2] Starting Frontend (Vite on port 5173)...
start "Digital Twin Frontend" /MIN cmd /c "cd frontend && %PACKAGE_MANAGER% run dev > ..\logs\frontend.log 2>&1"
echo SUCCESS: Frontend started
echo.

REM Wait for services to initialize
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Print status
echo ================================================================
echo              Application Started Successfully!
echo ================================================================
echo.
echo Services are running:
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo.
echo Logs are being written to:
echo   Backend:  logs\backend.log
echo   Frontend: logs\frontend.log
echo.
echo Opening frontend in your browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173
echo.
echo To view logs, check the files in the logs directory.
echo To stop services, close the Backend and Frontend windows.
echo.
pause
