@echo off
REM Digital Twin - Complete Setup Script for Windows

echo ================================================================
echo         Digital Twin - Complete Setup Script (Windows)
echo ================================================================
echo.

REM Check Python version
echo [1/6] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.10 or higher.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo SUCCESS: Python %PYTHON_VERSION% found
echo.

REM Check Node.js version
echo [2/6] Checking Node.js version...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo SUCCESS: Node.js %NODE_VERSION% found
echo.

REM Setup Backend (Python)
echo [3/6] Setting up Backend (Python)...

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo SUCCESS: Virtual environment created
) else (
    echo SUCCESS: Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo [4/6] Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo SUCCESS: Backend dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo WARNING: Please edit .env file and add your GEMINI_API_KEY if needed
) else (
    echo SUCCESS: .env file already exists
)
echo.

REM Create data directories
echo Creating data directories...
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
echo SUCCESS: Data directories created
echo.

REM Setup Frontend (Node.js)
echo [5/6] Setting up Frontend (Node.js)...

REM Check if pnpm is available, if not use npm
where pnpm >nul 2>&1
if errorlevel 1 (
    set PACKAGE_MANAGER=npm
    echo Using npm as package manager
    echo WARNING: For better performance, consider installing pnpm: npm install -g pnpm
) else (
    set PACKAGE_MANAGER=pnpm
    echo Using pnpm as package manager
)
echo.

REM Install frontend dependencies
cd frontend
echo Installing frontend dependencies (this may take a few minutes)...
call %PACKAGE_MANAGER% install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
echo SUCCESS: Frontend dependencies installed
cd ..
echo.

REM Final verification
echo [6/6] Verifying setup...
if exist "frontend\node_modules" (
    echo SUCCESS: Frontend dependencies are in place
) else (
    echo ERROR: Frontend dependencies are missing
    pause
    exit /b 1
)
echo.

REM Print final instructions
echo ================================================================
echo                    Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo.
echo   1. (Optional) Configure your Gemini API key in .env file
echo.
echo   2. Start the application using:
echo      start.bat
echo.
echo   Or start services manually:
echo      Backend:  .venv\Scripts\activate.bat ^&^& uvicorn src.digital_twin.app:app --reload --port 8000
echo      Frontend: cd frontend ^&^& %PACKAGE_MANAGER% run dev
echo.
echo   3. Access the application:
echo      Frontend: http://localhost:5173
echo      Backend:  http://localhost:8000
echo      API Docs: http://localhost:8000/docs
echo.
pause
