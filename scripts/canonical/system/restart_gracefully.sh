#!/bin/bash

##############################################################################
# OmniMind Graceful Restart Script
#
# Restarts OmniMind with graceful shutdown before restart
# - Notifies about service updates
# - Gives users time to prepare
# - Gracefully shuts down old instance
# - Waits for all cleanup to complete
# - Starts new instance with updated code loaded
#
# Usage: ./scripts/canonical/system/restart_gracefully.sh [notification_delay_seconds]
##############################################################################

set -e

NOTIFICATION_DELAY=${1:-10}
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CREDS_FILE="$PROJECT_ROOT/config/dashboard_auth.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}🔄 OmniMind Graceful Restart${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activate venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Check if system is running
if ! pgrep -f "uvicorn.*main:app" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  OmniMind is not currently running${NC}"
    echo "   Starting fresh instance..."
    cd "$PROJECT_ROOT"
    exec bash scripts/canonical/system/start_omnimind_system.sh
fi

# Get credentials
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
fi

# PHASE 1: Notify about restart
echo -e "${BLUE}PHASE 1: Notification and Countdown${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  OmniMind will restart in $NOTIFICATION_DELAY seconds${NC}"
echo "   → New code will be loaded"
echo "   → GPU QAOA will be activated"
echo "   → Service updates will be applied"
echo ""

# Attempt to notify via API if available
if [ -n "$CREDS" ]; then
    echo "→ Notifying dashboard about restart..."
    curl -s -X POST \
        -u "$CREDS" \
        -H "Content-Type: application/json" \
        -d '{
            "status": "restart_scheduled",
            "message": "OmniMind restarting in '$NOTIFICATION_DELAY' seconds",
            "delay_seconds": '$NOTIFICATION_DELAY'
        }' \
        http://localhost:8000/api/system/restart-notification 2>/dev/null || true
    echo ""
fi

# Countdown notification
for i in $(seq $NOTIFICATION_DELAY -1 1); do
    if [ $i -gt 3 ]; then
        printf -v msg "Restarting in %2ds... " $i
        printf "\r${YELLOW}%s${NC}" "$msg"
    else
        printf "\r${RED}Restarting in %2ds...${NC}" $i
    fi
    sleep 1
done

echo ""
echo ""

# PHASE 2: Graceful shutdown
echo -e "${BLUE}PHASE 2: Graceful Shutdown${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT"
bash scripts/canonical/system/shutdown_gracefully_with_updates.sh 30

# The shutdown script will restart automatically if there are pending updates
# If there are no pending updates, system will be stopped

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Restart sequence complete${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
