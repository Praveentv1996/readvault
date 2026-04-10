@echo off
REM Start Readvault API and open browser
setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Kill any existing Python processes on port 5000
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

REM Wait a moment
timeout /t 3 /nobreak >nul

start /B pythonw.exe api.py

REM Wait for API to start
timeout /t 6 /nobreak >nul

REM Open browser
start http://localhost:5000

exit /b 0
