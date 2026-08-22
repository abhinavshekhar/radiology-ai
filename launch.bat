@echo off
title Radiology AI Assistant
cd /d "%~dp0"

echo Starting Radiology AI...
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed or not in PATH.
    echo Please install Docker Desktop and try again.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop is not running. Starting it...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker...
    timeout /t 20 /nobreak >nul
)

if not exist "demo_samples\pneumonia_demo.jpg" (
    echo Generating demo samples...
    python scripts\download_demo_samples.py 2>nul
)

cd docker
docker compose up -d
if errorlevel 1 (
    echo Failed to start containers.
    pause
    exit /b 1
)

echo.
echo Radiology AI is starting...
echo   App:  http://localhost:3000
echo   API:  http://localhost:8000/docs
echo.

timeout /t 5 /nobreak >nul
start "" "http://localhost:3000"

exit /b 0
