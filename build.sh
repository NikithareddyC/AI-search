#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
npm install --production=false
npm run build
echo "✅ Frontend build complete!"
cd ..

echo "Starting backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
