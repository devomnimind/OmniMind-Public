#!/bin/bash

# Kill existing python processes related to main.py
pkill -f "python web/backend/main.py"
pkill -f "uvicorn src.api.main:app"

# Export PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Create logs directory if it doesn't exist
mkdir -p logs

echo "Starting OmniMind Backend Cluster..."

# Start Primary Instance (Port 8000)
echo "Starting Primary (Port 8000)..."
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --workers 1 > logs/backend_8000.log 2>&1 &
PID_8000=$!
echo $PID_8000 > logs/backend_8000.pid
echo "Primary started with PID $PID_8000"

# Start Secondary Instance (Port 8080)
echo "Starting Secondary (Port 8080)..."
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8080 --workers 1 > logs/backend_8080.log 2>&1 &
PID_8080=$!
echo $PID_8080 > logs/backend_8080.pid
echo "Secondary started with PID $PID_8080"

# Start Fallback Instance (Port 3001)
echo "Starting Fallback (Port 3001)..."
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 3001 --workers 1 > logs/backend_3001.log 2>&1 &
PID_3001=$!
echo $PID_3001 > logs/backend_3001.pid
echo "Fallback started with PID $PID_3001"

echo "Cluster is running. Logs available in logs/backend_*.log"
echo "Monitor with: tail -f logs/backend_*.log"
