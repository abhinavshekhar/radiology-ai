@echo off
title Radiology AI - Full Stack Launcher
echo ============================================
echo   Radiology AI - Days 2-6 Complete Build
echo   DenseNet121 + Captum + Cornerstone.js
echo ============================================
echo.

cd /d "%~dp0"

if not exist "demo_samples\pneumonia_demo.jpg" (
    echo [1/3] Generating demo X-ray samples...
    python scripts\download_demo_samples.py
) else (
    echo [1/3] Demo samples OK.
)

echo [2/3] Building Docker images (first run: 10-15 min for AI model)...
cd docker
docker compose build

echo [3/3] Starting all services...
docker compose up -d

echo.
echo ============================================
echo   ALL SERVICES RUNNING
echo ============================================
echo   App:       http://localhost:3000
echo   API Docs:  http://localhost:8000/docs
echo   Orthanc:   http://localhost:8042  (run: docker compose --profile pacs up -d)
echo.
echo   Logins (password: demo1234):
echo     doctor@radiology.ai      - Doctor
echo     radiologist@radiology.ai - Radiologist
echo     admin@radiology.ai       - Admin
echo ============================================
pause
