@echo off
REM Windows startup script for AI Content Growth Platform

echo.
echo 🚀 Starting AI Content Growth Platform...
echo.

REM Kill any existing Python processes on port 8000
taskkill /F /IM python.exe /T 2>nul

REM Start backend
echo Starting backend on port 8000...
cd backend
start "Backend - uvicorn" python -m uvicorn main:app --port 8000

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo Starting frontend on port 3001...
cd ..\frontend
start "Frontend - Vite" npm run dev

echo.
echo ✅ Platform is starting!
echo 📱 Frontend:   http://localhost:3001
echo 📚 Backend:    http://localhost:8000
echo 📊 API Docs:   http://localhost:8000/docs
echo.
pause
