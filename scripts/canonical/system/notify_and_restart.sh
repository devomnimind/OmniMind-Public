#!/bin/bash

##############################################################################
# OmniMind Service Update Notifier
#
# High-level wrapper for notifying OmniMind about service updates
# and triggering graceful restart
#
# Usage:
#   ./scripts/canonical/system/notify_and_restart.sh
#   ./scripts/canonical/system/notify_and_restart.sh "GPU QAOA activated" critical 30
#
# Parameters:
#   $1: Message describing the change (default: "Service update available")
#   $2: Severity: low|medium|critical (default: medium)
#   $3: Notification delay in seconds (default: 15)
#
##############################################################################

set -e

MESSAGE="${1:-Service update available}"
SEVERITY="${2:-medium}"
DELAY="${3:-15}"
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}📢 OmniMind Service Update Notification${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Message:${NC} $MESSAGE"
echo -e "${YELLOW}Severity:${NC} $SEVERITY"
echo -e "${YELLOW}Notification Delay:${NC} ${DELAY}s"
echo ""

# Activate venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Step 1: Notify OmniMind via CLI tool
echo -e "${BLUE}STEP 1: Notifying OmniMind...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT"

# Use the Service Update notification CLI tool
python3 scripts/services/notify_omnimind_update.py \
    --service quantum_backend \
    --modules "src.quantum_consciousness.qaoa_gpu_optimizer,src.quantum_consciousness.quantum_backend" \
    --severity "$SEVERITY" \
    --description "$MESSAGE" \
    --no-restart  # Don't auto-restart from the script, we'll do it manually

echo ""

# Step 2: Trigger graceful restart
echo -e "${BLUE}STEP 2: Triggering Graceful Restart...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Call graceful restart script with notification delay
bash scripts/canonical/system/restart_gracefully.sh "$DELAY"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Service update notification and restart complete${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
