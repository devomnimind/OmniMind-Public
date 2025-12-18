#!/bin/bash

# Sequential Initialization Wrapper
# Usa init_sequential_services.py para ordenar inicialização

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
echo -e "${BLUE}║         🔧 Sequential Service Initialization Manager            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Kill any previous processes
echo -e "${YELLOW}🧹 Cleaning up previous processes...${NC}"
pkill -9 -f "python.*main.py" 2>/dev/null || true
pkill -9 -f "uvicorn.*main:app" 2>/dev/null || true
pkill -9 -f "npm run dev" 2>/dev/null || true
sleep 2

# Activate venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo -e "${GREEN}✅ Venv activated${NC}"
fi

# Ensure logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Export for child processes
export OMNIMIND_PROJECT_ROOT="$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH}"

# Start backend directly (not via run_cluster.sh which has issues)
echo -e "\n${GREEN}▶ Starting Backend Primary (8000)${NC}"
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --workers 1 > "$PROJECT_ROOT/logs/backend_8000.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_ROOT/logs/backend_8000.pid"
echo -e "   ${GREEN}PID: $BACKEND_PID${NC}"
echo -e "   Log: tail -f logs/backend_8000.log"

# Wait for primary to respond
echo -e "\n${YELLOW}⏳ Waiting for Backend Primary to be responsive (up to 60s)...${NC}"
READY=false
for i in {1..30}; do
    if curl -s --max-time 3 http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend Primary is ready!${NC}"
        READY=true
        break
    fi
    echo -n "."
    sleep 2
done

if [ "$READY" != "true" ]; then
    echo -e "\n${RED}❌ Backend Primary failed to respond. Check logs/backend_8000.log${NC}"
    tail -n 50 "$PROJECT_ROOT/logs/backend_8000.log"
    exit 1
fi

# Run Python init manager for remaining services
echo -e "\n${GREEN}▶ Starting Sequential Service Initialization Manager${NC}"
python "$PROJECT_ROOT/scripts/canonical/system/init_sequential_services.py"

# Check results
if [ -f "$PROJECT_ROOT/logs/init_results.json" ]; then
    echo -e "\n${GREEN}📊 Initialization results saved to: logs/init_results.json${NC}"
    cat "$PROJECT_ROOT/logs/init_results.json" | python -m json.tool
fi

echo -e "\n${GREEN}✨ Sequential initialization complete!${NC}"
echo -e "${BLUE}To monitor services: tail -f logs/*.log${NC}"
