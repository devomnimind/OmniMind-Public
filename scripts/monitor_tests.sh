#!/bin/bash
# scripts/monitor_tests.sh
# Checks the status of the background test run.

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit 1

LOG_FILE="data/test_reports/background_run.log"
STATUS_FILE="data/test_reports/background_run.status"

clear
echo "🔍 OmniMind Test Monitor"
echo "========================"
echo "Time: $(date)"
echo ""

if [ -f "$STATUS_FILE" ]; then
    STATUS=$(head -n 1 "$STATUS_FILE")
    echo "Status: $STATUS"
    cat "$STATUS_FILE" | tail -n +2 | sed 's/^/  /'
else
    echo "Status: NOT STARTED (No status file found)"
fi

echo ""
echo "📊 Log Output ($LOG_FILE):"
echo "----------------------------------------"

if [ -f "$LOG_FILE" ]; then
    # Show the last 15 lines of the log
    tail -n 15 "$LOG_FILE"
    
    # Try to extract progress if possible (pytest output can be tricky to parse in stream)
    echo "----------------------------------------"
    echo "Log Size: $(du -h "$LOG_FILE" | cut -f1)"
else
    echo "Log file not found yet."
fi
echo "========================"
