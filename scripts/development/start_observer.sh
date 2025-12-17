#!/bin/bash

# OmniMind Long-term Observer Launcher
# Starts the observer service in background

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
LOG_FILE="$PROJECT_ROOT/data/long_term_logs/observer_startup.log"

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/data/long_term_logs"

cd "$PROJECT_ROOT"

echo "Starting OmniMind Observer at $(date)" >> "$LOG_FILE"

# Activate venv
source .venv/bin/activate

# Start Service
nohup python src/services/observer_service.py >> "$LOG_FILE" 2>&1 &

PID=$!
echo "Observer started with PID: $PID"
echo "Observer started with PID: $PID" >> "$LOG_FILE"

# Save PID for management
echo $PID > "$PROJECT_ROOT/data/long_term_logs/observer.pid"
