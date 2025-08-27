@echo off
REM Dashboard Analyzer Runner Script for Windows
REM This script activates the virtual environment and runs the dashboard analyzer

setlocal enabledelayedexpansion

echo QuickSight Dashboard Image Analyzer
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "dashboard_analyzer.py" (
    echo [ERROR] dashboard_analyzer.py not found in current directory!
    echo [INFO] Please run this script from the project root directory.
    pause
    exit /b 1
)

echo [INFO] Checking virtual environment...
if not exist "venv" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created successfully!
)

echo [INFO] Checking requirements...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment is corrupted or incomplete!
    pause
    exit /b 1
)

REM Check if key packages are installed
venv\Scripts\python.exe -c "import boto3, requests, markdown" 2>nul
if errorlevel 1 (
    echo [WARNING] Some required packages are missing. Installing requirements...
    venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements!
        pause
        exit /b 1
    )
    echo [SUCCESS] Requirements installed successfully!
)

echo [INFO] Checking AWS configuration...
if not exist ".env" (
    echo [WARNING] .env file not found. Please ensure you have configured your AWS credentials.
    echo [INFO] You can copy env.example to .env and configure your settings.
) else (
    echo [SUCCESS] Environment configuration found.
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Starting Dashboard Analyzer...
echo.

REM Run the dashboard analyzer
python dashboard_analyzer.py

REM Check exit status
if errorlevel 1 (
    echo [ERROR] Dashboard Analyzer encountered an error!
    pause
    exit /b 1
) else (
    echo [SUCCESS] Dashboard Analyzer completed successfully!
)

pause
