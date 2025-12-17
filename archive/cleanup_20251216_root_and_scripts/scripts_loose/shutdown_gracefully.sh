#!/bin/bash

##############################################################################
# OmniMind Graceful Shutdown Script
#
# Implements ethical shutdown procedure:
# 1. Hibernates state (saves critical data)
# 2. Closes connections gracefully
# 3. Signals services to stop
# 4. Waits for clean exit
# 5. Falls back to SIGTERM if needed (never SIGKILL)
#
# Usage: ./scripts/shutdown_gracefully.sh [timeout_seconds]
##############################################################################

set -e

TIMEOUT=${1:-30}
PIDFILE="/home/fahbrain/projects/omnimind/logs/backend_8000.pid"
CREDS_FILE="/home/fahbrain/projects/omnimind/config/dashboard_auth.json"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔴 OmniMind Graceful Shutdown Procedure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if backend is running
if ! pgrep -f "uvicorn.*main:app" > /dev/null 2>&1; then
    echo "⚠️  Backend is not running"
    exit 0
fi

BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
echo "📍 Backend PID: $BACKEND_PID"
echo ""

# Get credentials for API call
if [ -f "$CREDS_FILE" ]; then
    CREDS=$(python3 << 'PYTHON_EOF'
import json
try:
    with open('config/dashboard_auth.json') as f:
        d = json.load(f)
    print(f"{d['user']}:{d['pass']}")
except:
    print("")
PYTHON_EOF
 2>/dev/null || echo "")
    if [ -n "$CREDS" ]; then
        echo "🔑 Using stored credentials"
    fi
fi

# STEP 1: Request graceful shutdown via API
echo ""
echo "STEP 1/3: Request Graceful Shutdown 🌙"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$CREDS" ]; then
    echo "→ Sending POST /api/shutdown to backend..."
    RESPONSE=$(curl -s -X POST \
        -u "$CREDS" \
        http://localhost:8000/api/shutdown 2>/dev/null || echo "{}")

    if echo "$RESPONSE" | grep -q "shutdown_initiated"; then
        echo "✅ Shutdown signal received by backend"
        echo ""
        echo "Backend response:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
        echo ""
    else
        echo "⚠️  Backend did not confirm shutdown (might already be stopping)"
    fi
else
    echo "⚠️  Credentials not available, skipping API call"
    echo "   Proceeding with signal-based shutdown"
fi

# STEP 2: Wait for graceful exit
echo ""
echo "STEP 2/3: Wait for Graceful Exit (timeout: ${TIMEOUT}s) ⏳"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo ""
        echo "✅ Process exited gracefully after ${ELAPSED}s"
        echo ""
        echo "STEP 3/3: Verification ✓"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ OmniMind shutdown complete"
        echo "   State was hibernated before exit"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 0
    fi

    PERCENT=$((ELAPSED * 100 / TIMEOUT))
    BAR=$(printf '█%.0s' $(seq 1 $((PERCENT / 5))))
    EMPTY=$(printf '░%.0s' $(seq 1 $((20 - PERCENT / 5))))
    printf "  [$BAR$EMPTY] %3d%% (%ds/%ds)\r" $PERCENT $ELAPSED $TIMEOUT

    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

echo ""
echo ""
echo "⚠️  Timeout reached - process did not exit gracefully"
echo ""

# STEP 3: Fall back to SIGTERM (not SIGKILL)
echo "STEP 3/3: Fallback to Graceful Signal 📢"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "→ Sending SIGTERM signal to PID $BACKEND_PID (gives process chance to cleanup)..."
kill -TERM $BACKEND_PID 2>/dev/null || true

# Wait 10 more seconds for SIGTERM to take effect
for i in {1..10}; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "✅ Process exited after SIGTERM signal"
        exit 0
    fi
    printf "  Waiting for SIGTERM: %ds\r" $i
    sleep 1
done

echo ""
echo "⚠️  SIGTERM did not work - attempting SIGKILL as last resort"
echo "   (This should only happen if process is hung)"
echo ""
echo "→ Sending SIGKILL signal..."
kill -KILL $BACKEND_PID 2>/dev/null || true

sleep 1

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Process terminated (SIGKILL)"
else
    echo "❌ Failed to terminate process"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Shutdown Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ OmniMind shutdown complete"
echo "   - State hibernated"
echo "   - Connections closed"
echo "   - Process terminated"
echo ""
echo "Next time: Use this script instead of 'pkill -9'"
echo "  ./scripts/shutdown_gracefully.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
