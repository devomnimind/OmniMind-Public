#!/bin/bash
# Script para parar o sistema OmniMind em produção

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}🛑 Parando Sistema OmniMind...${NC}"
echo ""

# Parar Ciclo Principal
if [ -f "logs/main_cycle.pid" ]; then
    MAIN_PID=$(cat logs/main_cycle.pid)
    if ps -p $MAIN_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Parando Ciclo Principal (PID: $MAIN_PID)...${NC}"
        kill $MAIN_PID 2>/dev/null
        sleep 2
        if ps -p $MAIN_PID > /dev/null 2>&1; then
            kill -9 $MAIN_PID 2>/dev/null
        fi
        echo -e "${GREEN}✅${NC} Ciclo Principal parado"
    fi
fi

# Parar processos Python
echo -e "${YELLOW}Parando processos Python...${NC}"
pkill -f "python -m src.main" 2>/dev/null && echo -e "${GREEN}✅${NC} src.main parado" || true
pkill -f "python web/backend/main.py" 2>/dev/null && echo -e "${GREEN}✅${NC} Backend parado" || true
pkill -f "uvicorn web.backend.main:app" 2>/dev/null && echo -e "${GREEN}✅${NC} Uvicorn parado" || true
sleep 2

# Parar Frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Parando Frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null
        sleep 1
        echo -e "${GREEN}✅${NC} Frontend parado"
    fi
fi
pkill -f "vite" 2>/dev/null && echo -e "${GREEN}✅${NC} Vite parado" || true

# Parar eBPF
pkill -f "bpftrace.*monitor_mcp_bpf" 2>/dev/null && echo -e "${GREEN}✅${NC} eBPF Monitor parado" || true

echo ""
echo -e "${GREEN}✅ Sistema OmniMind parado${NC}"

