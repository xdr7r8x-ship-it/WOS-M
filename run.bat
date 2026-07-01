@echo off
REM WOS-M Run Script (Windows)
REM © MANSOUR — WOS-M. All rights reserved.

echo Starting WOS-M...

REM Check for .env file
if not exist .env (
    echo Warning: .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit .env file with your credentials!
    exit /b 1
)

REM Create data directories
if not exist "data\logs" mkdir "data\logs"
if not exist "data\backups" mkdir "data\backups"

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
)

REM Activate virtual environment
call venv\Scripts\activate

REM Run the bot
echo Starting bot...
python main.py
