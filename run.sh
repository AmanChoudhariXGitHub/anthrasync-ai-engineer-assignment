#!/bin/bash

# Enterprise Knowledge Assistant Startup Script

set -e

echo "🚀 Enterprise Knowledge Assistant - Startup"
echo "============================================"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create necessary directories
mkdir -p rag_system/data
mkdir -p chroma_db

echo ""
echo "Starting services..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
}

trap cleanup EXIT

# Start FastAPI backend
echo "📡 Starting FastAPI backend on http://localhost:${API_PORT:-8000}..."
cd rag_system/backend
python3 main.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Failed to start FastAPI backend"
    exit 1
fi

echo "✓ FastAPI backend started (PID: $BACKEND_PID)"
echo ""

# Start Streamlit frontend
echo "🎨 Starting Streamlit frontend on http://localhost:8501..."
streamlit run rag_system/frontend/app.py --logger.level=info

wait
