#!/bin/bash
# Startup script for production deployment

echo "🚀 Starting AI Content Growth Platform..."

# Start backend in background
echo "Starting backend on port 8000..."
cd backend
python -m uvicorn main:app --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend on port 3001..."
cd ../frontend
npm run dev -- --host &
FRONTEND_PID=$!

echo "✅ Platform is running!"
echo "📱 Frontend: http://localhost:3001"
echo "📚 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
