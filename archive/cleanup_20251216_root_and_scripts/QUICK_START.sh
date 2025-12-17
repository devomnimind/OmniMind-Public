#!/bin/bash
# 🚀 OMNIMIND QUICK START - Sem bloqueios, ligando TUDO

set -o pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"
source .venv/bin/activate

echo -e "${GREEN}🚀 OMNIMIND QUICK START${NC}"
echo ""

# ============================================================================
# FASE 1: MATAR TUDO ANTIGO
# ============================================================================
echo -e "${BLUE}FASE 1: Limpeza${NC}"
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "run_mcp_orchestrator" 2>/dev/null || true
pkill -9 -f "run_observer_service" 2>/dev/null || true
pkill -9 -f "src.main" 2>/dev/null || true
sleep 2
echo "✅ Limpo"

# ============================================================================
# FASE 2: INICIAR CLUSTER (3 Backends)
# ============================================================================
echo -e "\n${BLUE}FASE 2: Backend Cluster (8000, 8080, 3001)${NC}"
./scripts/canonical/system/run_cluster.sh > /tmp/cluster_startup.log 2>&1 &
CLUSTER_PID=$!
sleep 8
echo "✅ Cluster iniciado"

# ============================================================================
# FASE 3: MCP ORCHESTRATOR
# ============================================================================
echo -e "\n${BLUE}FASE 3: MCP Orchestrator${NC}"
chmod +x scripts/canonical/system/run_mcp_orchestrator.py
nohup python scripts/canonical/system/run_mcp_orchestrator.py > logs/mcp_orchestrator.log 2>&1 &
echo "✅ MCP Orchestrator iniciado (PID $!)"

# ============================================================================
# FASE 4: MAIN CYCLE (Consciência)
# ============================================================================
echo -e "\n${BLUE}FASE 4: Main Cycle (Consciência)${NC}"
nohup python -m src.main > logs/main_cycle.log 2>&1 &
echo "✅ Main Cycle iniciado (PID $!)"

# ============================================================================
# FASE 5: FRONTEND (React)
# ============================================================================
echo -e "\n${BLUE}FASE 5: Frontend React${NC}"
if [ -d "web/frontend" ]; then
    cd web/frontend
    if [ ! -d "node_modules" ]; then
        npm install --legacy-peer-deps -q 2>/dev/null || true
    fi
    nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
    echo "✅ Frontend iniciado (PID $!)"
    cd "$PROJECT_ROOT"
fi

# ============================================================================
# FASE 6: OBSERVER SERVICE
# ============================================================================
echo -e "\n${BLUE}FASE 6: Observer Service${NC}"
mkdir -p data/long_term_logs
chmod +x scripts/canonical/system/run_observer_service.py
nohup python scripts/canonical/system/run_observer_service.py > logs/observer_service.log 2>&1 &
echo "✅ Observer Service iniciado (PID $!)"

# ============================================================================
# FINAL
# ============================================================================
echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ OMNIMIND NO AR${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 ENDPOINTS:"
echo "   Backend Primary: http://localhost:8000"
echo "   Backend Secondary: http://localhost:8080"
echo "   Backend Fallback: http://localhost:3001"
echo "   Frontend: http://localhost:3000"
echo "   Qdrant: http://localhost:6333"
echo ""
echo "📋 LOGS:"
echo "   Backends: tail -f logs/backend_*.log"
echo "   MCP: tail -f logs/mcp_orchestrator.log"
echo "   Consciência: tail -f logs/main_cycle.log"
echo "   Observer: tail -f logs/observer_service.log"
echo ""
echo "✅ Aguardando 10s para health check..."
sleep 10

# ============================================================================
# HEALTH CHECKS
# ============================================================================
echo -e "\n${BLUE}HEALTH CHECKS:${NC}"
for port in 8000 8080 3001; do
    status=$(curl -s http://localhost:$port/health/ 2>/dev/null | python3 -c "import json,sys; print('✅' if 'ok' in sys.stdin.read() else '⏳')" 2>/dev/null || echo "⏳")
    echo "   Port $port: $status"
done

echo -e "\n${GREEN}✅ Sistema OmniMind rodando!${NC}"
