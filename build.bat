@echo off
REM Build script for single unified deployment

echo.
echo 🔨 Building AI Content Growth Platform...
echo.

REM Build frontend
echo Building frontend...
cd frontend
call npm run build

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend build failed
    pause
    exit /b 1
)

echo ✅ Frontend built to backend/dist

cd ..

REM Done
echo.
echo ✅ Build complete!
echo.
echo Next steps:
echo 1. Run: cd backend
echo 2. Run: python -m uvicorn main:app --port 8000
echo 3. Open: http://localhost:8000
echo.
pause
