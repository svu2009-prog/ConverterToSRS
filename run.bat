@echo off
title List Processor for sing-box

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found. Please install Python 3.12+ and try again.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo requirements.txt not found.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt -q

echo Starting application...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to exit.
    pause
)
