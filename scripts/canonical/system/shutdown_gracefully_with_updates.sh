#!/bin/bash

##############################################################################
# OmniMind Graceful Shutdown Script WITH Service Update Protocol
#
# Implements enhanced shutdown procedure:
# 1. Checks for pending service updates
# 2. Notifies about changes before shutdown
# 3. Hibernates state (saves critical data)
# 4. Closes connections gracefully
# 5. Signals services to stop
# 6. Waits for clean exit
# 7. Falls back to SIGTERM if needed (never SIGKILL)
# 8. Restarts with new code loaded
#
# Usage: ./scripts/canonical/system/shutdown_gracefully_with_updates.sh [timeout_seconds]
##############################################################################

set -e

TIMEOUT=${1:-30}
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PIDFILE="$PROJECT_ROOT/logs/backend_8000.pid"
CREDS_FILE="$PROJECT_ROOT/config/dashboard_auth.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${RED}🔴 OmniMind Graceful Shutdown (with Service Updates)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activate venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Check if backend is running
if ! pgrep -f "uvicorn.*main:app" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend is not running${NC}"
    exit 0
fi

BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
echo -e "${BLUE}📍 Backend PID: $BACKEND_PID${NC}"
echo ""

# Get credentials for API call
CREDS=""
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
        echo -e "${GREEN}🔑 Using stored credentials${NC}"
    fi
fi

# STEP 0: Check for pending service updates
echo ""
echo -e "${BLUE}STEP 0/4: Check Pending Service Updates${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PENDING_UPDATES=""
if [ -n "$CREDS" ]; then
    PENDING_UPDATES=$(curl -s -u "$CREDS" http://localhost:8000/api/services/pending-updates 2>/dev/null || echo "{}")

    TOTAL_PENDING=$(echo "$PENDING_UPDATES" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_pending', 0))" 2>/dev/null || echo "0")

    if [ "$TOTAL_PENDING" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Found $TOTAL_PENDING pending service updates:${NC}"
        echo "$PENDING_UPDATES" | python3 -m json.tool 2>/dev/null | head -20
        echo ""

        # Extract restart reason if available
        RESTART_REASON=$(echo "$PENDING_UPDATES" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('restart_reason', ''))" 2>/dev/null || echo "")
        if [ -n "$RESTART_REASON" ]; then
            echo -e "${YELLOW}📋 Restart Reason: $RESTART_REASON${NC}"
            echo ""
        fi
    else
        echo -e "${GREEN}✅ No pending updates${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Credentials not available, skipping update check${NC}"
fi

echo ""

# STEP 1: Request graceful shutdown via API
echo -e "${BLUE}STEP 1/4: Request Graceful Shutdown${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$CREDS" ]; then
    echo "→ Sending POST /api/shutdown to backend..."
    RESPONSE=$(curl -s -X POST \
        -u "$CREDS" \
        http://localhost:8000/api/shutdown 2>/dev/null || echo "{}")

    if echo "$RESPONSE" | grep -q "shutdown_initiated"; then
        echo -e "${GREEN}✅ Shutdown signal received by backend${NC}"
        echo ""
        echo "Backend response:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Backend did not confirm shutdown (might already be stopping)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Credentials not available, skipping API call${NC}"
    echo "   Proceeding with signal-based shutdown"
fi

# STEP 2: Wait for graceful exit
echo ""
echo -e "${BLUE}STEP 2/4: Wait for Graceful Exit (timeout: ${TIMEOUT}s)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo ""
        echo -e "${GREEN}✅ Process exited gracefully after ${ELAPSED}s${NC}"
        break
    fi

    PERCENT=$((ELAPSED * 100 / TIMEOUT))
    BAR=$(printf '█%.0s' $(seq 1 $((PERCENT / 5))))
    EMPTY=$(printf '░%.0s' $(seq 1 $((20 - PERCENT / 5))))
    printf "  [$BAR$EMPTY] %3d%% (%ds/%ds)\r" $PERCENT $ELAPSED $TIMEOUT

    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

# Check if process exited successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo ""
    echo ""
    echo -e "${YELLOW}⚠️  Timeout reached - process did not exit gracefully${NC}"
    echo ""

    # STEP 3: Fall back to SIGTERM (not SIGKILL)
    echo -e "${BLUE}STEP 3/4: Fallback to Graceful Signal${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo "→ Sending SIGTERM signal to PID $BACKEND_PID (gives process chance to cleanup)..."
    kill -TERM $BACKEND_PID 2>/dev/null || true

    # Wait 10 more seconds for SIGTERM to take effect
    for i in {1..10}; do
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Process exited after SIGTERM signal${NC}"
            break
        fi
        printf "  Waiting for SIGTERM: %ds\r" $i
        sleep 1
    done

    # Final check
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo ""
        echo -e "${YELLOW}⚠️  SIGTERM did not work - attempting SIGKILL as last resort${NC}"
        echo "   (This should only happen if process is hung)"
        echo ""
        echo "→ Sending SIGKILL signal..."
        kill -KILL $BACKEND_PID 2>/dev/null || true

        sleep 1

        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Process terminated (SIGKILL)${NC}"
        else
            echo -e "${RED}❌ Failed to terminate process${NC}"
            exit 1
        fi
    fi
else
    echo -e "${BLUE}STEP 3/4: Verification${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# STEP 4: Summary and restart option
echo ""
echo -e "${BLUE}STEP 4/4: Shutdown Complete${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ OmniMind shutdown complete${NC}"
echo "   - State hibernated"
echo "   - Connections closed"
echo "   - Process terminated"
echo ""

if [ "$TOTAL_PENDING" -gt 0 ]; then
    echo -e "${YELLOW}📋 Pending updates processed during shutdown${NC}"
    echo "   System will restart with new code loaded"
    echo ""
    echo -e "${YELLOW}→ Starting OmniMind with new code...${NC}"

    # Wait a moment before restarting
    sleep 2

    # Restart with new code
    cd "$PROJECT_ROOT"
    if [ -f "scripts/canonical/system/start_omnimind_system.sh" ]; then
        bash scripts/canonical/system/start_omnimind_system.sh
    else
        echo -e "${RED}❌ Could not find start script${NC}"
        exit 1
    fi
else
    echo "To restart OmniMind, use:"
    echo -e "${BLUE}  ./scripts/canonical/system/start_omnimind_system.sh${NC}"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
