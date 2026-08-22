@echo off
cd /d "%~dp0\docker"
docker compose down
echo Containers stopped.
