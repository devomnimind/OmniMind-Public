#!/bin/bash

# Ultra-fast backend initialization for testing
# Starts backend with all heavy services disabled

set -e

PROJECT_ROOT="${OMNIMIND_PROJECT_ROOT:=/home/fahbrain/projects/omnimind}"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ⚡ Ultra-Fast Backend Initialization (Heavy Services Disabled) ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Clean up
echo -e "${YELLOW}🧹 Cleaning up previous processes...${NC}"
pkill -9 -f "uvicorn.*main:app" 2>/dev/null || true
sleep 1

# Activate venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Ensure logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Set environment variables to DISABLE heavy services
export OMNIMIND_INIT_ORCHESTRATOR="0"
export OMNIMIND_INIT_CONSCIOUSNESS="0"
export OMNIMIND_PROJECT_ROOT="$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH}"

echo -e "${BLUE}Environment Configuration:${NC}"
echo -e "  OMNIMIND_INIT_ORCHESTRATOR: ${GREEN}${OMNIMIND_INIT_ORCHESTRATOR}${NC} (disabled)"
echo -e "  OMNIMIND_INIT_CONSCIOUSNESS: ${GREEN}${OMNIMIND_INIT_CONSCIOUSNESS}${NC} (disabled)"
echo ""

# Start backend on port 8000
echo -e "${GREEN}▶ Starting Backend (Port 8000) - LEAN MODE${NC}"
echo -e "  This configuration:"
echo -e "    ✓ Disables Orchestrator initialization"
echo -e "    ✓ Disables Consciousness metrics"
echo -e "    ✓ Keeps essential services only"
echo -e "    ✓ Should start in <5 seconds"
echo ""

nohup python -m uvicorn web.backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${OMNIMIND_WORKERS:-2}" \
  > "$PROJECT_ROOT/logs/backend_8000.log" 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_ROOT/logs/backend_8000.pid"
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "  Log: ${GREEN}tail -f logs/backend_8000.log${NC}"
echo ""

# Wait for backend to be responsive
echo -e "${YELLOW}⏳ Waiting for backend to respond...${NC}"
READY=false
TIMEOUT=30
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -s --max-time 2 http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is responding!${NC}"
        READY=true
        break
    fi

    echo -n "."
    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

echo ""

if [ "$READY" = "true" ]; then
    # Get health status
    echo -e "${BLUE}Health Status:${NC}"
    curl -s http://localhost:8000/health/ | python -m json.tool 2>/dev/null || echo "(unable to parse)"

    echo ""
    echo -e "${GREEN}🎉 Backend is ready!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Test API: ${GREEN}curl http://localhost:8000/health/${NC}"
    echo -e "  2. View logs: ${GREEN}tail -f logs/backend_8000.log${NC}"
    echo -e "  3. To enable heavy services later:"
    echo -e "     ${GREEN}export OMNIMIND_INIT_ORCHESTRATOR=1${NC}"
    echo -e "     ${GREEN}export OMNIMIND_INIT_CONSCIOUSNESS=1${NC}"
    echo -e "     ${GREEN}pkill -f 'uvicorn.*main:app' && ./start_ultrasimple.sh${NC}"
    echo ""

    # Tail logs
    echo -e "${BLUE}=== Backend Logs (Ctrl+C to stop) ===${NC}"
    tail -f "$PROJECT_ROOT/logs/backend_8000.log"
else
    echo -e "${RED}❌ Backend failed to respond within ${TIMEOUT}s${NC}"
    echo ""
    echo -e "${RED}Last 30 lines of logs:${NC}"
    tail -n 30 "$PROJECT_ROOT/logs/backend_8000.log"
    exit 1
fi
