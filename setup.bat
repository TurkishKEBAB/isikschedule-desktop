@echo off
REM SchedularV3 Setup Script for Windows
REM This script sets up the project for use in PyCharm or command line

setlocal enabledelayedexpansion

echo.
echo ================================================
echo SchedularV3 Project Setup
echo ================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%

echo Project Root: %PROJECT_ROOT%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✓ Python found
python --version
echo.

REM Check if virtual environment exists
if exist "%PROJECT_ROOT%.venv\Scripts\activate.bat" (
    echo ✓ Virtual environment found
    call "%PROJECT_ROOT%.venv\Scripts\activate.bat"
) else (
    echo ! Virtual environment not found at .venv
    echo Creating virtual environment...
    python -m venv .venv
    call "%PROJECT_ROOT%.venv\Scripts\activate.bat"
    echo ✓ Virtual environment created and activated
)
echo.

REM Install the project in editable mode
echo Installing SchedularV3 in editable mode...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install project in editable mode
    pause
    exit /b 1
)
echo ✓ Project installed successfully
echo.

REM Install development dependencies
echo Installing development dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo ✓ Requirements installed successfully
echo.

REM Verify installation
echo Verifying installation...
python -c "from core.models import Course; from utils.schedule_metrics import SchedulerPrefs; from algorithms.base_scheduler import BaseScheduler; print('✓ All core imports successful')"
if errorlevel 1 (
    echo ERROR: Some imports failed
    pause
    exit /b 1
)
echo.

REM Final status
echo ================================================
echo ✓ SETUP COMPLETE
echo ================================================
echo.
echo Next steps:
echo 1. Reload your PyCharm project (File > Invalidate Caches > Invalidate and Restart)
echo 2. Mark directories as sources:
echo    - Right-click core/ > Mark Directory as > Sources Root
echo    - Right-click utils/ > Mark Directory as > Sources Root
echo    - Right-click algorithms/ > Mark Directory as > Sources Root
echo 3. Go to File > Settings > Project > Python Interpreter
echo 4. Select the .venv\Scripts\python.exe interpreter
echo.
echo All imports should now work correctly!
echo.
pause

