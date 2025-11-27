#!/bin/bash
# scripts/run_tests_background.sh
# Runs the full OmniMind test suite in the background with logging.

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found at .venv/bin/activate" >> "$LOG_FILE"
    exit 1
fi

# Create output directory
mkdir -p data/test_reports

LOG_FILE="data/test_reports/background_run.log"
STATUS_FILE="data/test_reports/background_run.status"

echo "STARTED" > "$STATUS_FILE"
echo "Starting full test suite at $(date)" >> "$STATUS_FILE"
echo "PID: $$" >> "$STATUS_FILE"

echo "==================================================" > "$LOG_FILE"
echo "OmniMind Test Suite - Background Run" >> "$LOG_FILE"
echo "Start Time: $(date)" >> "$LOG_FILE"
echo "==================================================" >> "$LOG_FILE"

# Execute pytest with standard arguments
# Note: Using unbuffered output (-u) for python if possible, but pytest handles its own buffering.
# We redirect both stdout and stderr to the log file.

pytest tests/ \
    -v \
    --tb=short \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=json:data/test_reports/coverage.json \
    --cov-report=html:data/test_reports/htmlcov \
    --maxfail=999 \
    --durations=20 \
    -W ignore::DeprecationWarning \
    >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "==================================================" >> "$LOG_FILE"
echo "End Time: $(date)" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
echo "==================================================" >> "$LOG_FILE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "COMPLETED_SUCCESS" > "$STATUS_FILE"
else
    echo "COMPLETED_FAILURE" > "$STATUS_FILE"
fi

echo "Finished at $(date) with exit code $EXIT_CODE" >> "$STATUS_FILE"
