@echo off
REM EasyChatbox Startup Script for Windows

echo Starting EasyChatbox...

REM Start the backend server in a new window
start "Backend Server" /D "backend" cmd /k "python main.py"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start the frontend server in a new window
start "Frontend Server" /D "frontend" cmd /k "npm start"

echo EasyChatbox servers starting...
echo Backend should be available at http://localhost:8000
echo Frontend should be available at http://localhost:3000
echo Press any key to close this window...
pause >nul
