#!/bin/bash
# OmniMind Sequential Initialization - Inicialização sequencial robusta
# Inicia todos os serviços em ordem, verificando saúde antes de prosseguir

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Calcular PROJECT_ROOT
if [ -n "${OMNIMIND_PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT="$OMNIMIND_PROJECT_ROOT"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    while [ "$SCRIPT_DIR" != "/" ]; do
        if [ -f "$SCRIPT_DIR/.env" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
            PROJECT_ROOT="$SCRIPT_DIR"
            break
        fi
        SCRIPT_DIR="$(dirname "$SCRIPT_DIR")"
    done
    [ -z "${PROJECT_ROOT:-}" ] && PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
fi

cd "$PROJECT_ROOT" || exit 1

# Função de health check com retry
check_health() {
    local url=$1
    local max_retries=${2:-10}
    local retry_interval=${3:-2}
    
    for i in $(seq 1 $max_retries); do
        if curl -s --max-time 3 "$url" > /dev/null 2>&1; then
            return 0
        fi
        [ $i -lt $max_retries ] && sleep $retry_interval
    done
    return 1
}

# Função para verificar CPU
check_cpu() {
    local max_cpu=${1:-30}
    local cpu=$(ps aux --no-headers -o pcpu -C python 2>/dev/null | awk '{sum+=$1} END {print sum+0}' || echo "0")
    (( $(echo "$cpu < $max_cpu" | bc -l 2>/dev/null || echo "1") ))
}

echo -e "${BLUE}🚀 Iniciando OmniMind Sequencial...${NC}"

# Limpeza
echo "🧹 Limpando processos antigos..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "python.*main" 2>/dev/null || true
sleep 2

# Ativar venv
[ -f "$PROJECT_ROOT/.venv/bin/activate" ] && source "$PROJECT_ROOT/.venv/bin/activate"

# TIER 1: Backend Cluster
echo -e "${GREEN}▶ TIER 1: Backend Cluster${NC}"
"$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh"

echo "⏳ Aguardando Backend Primary (8000)..."
if check_health "http://localhost:8000/health/" 30 3; then
    echo -e "${GREEN}✅ Backend Primary estável${NC}"
else
    echo -e "${RED}❌ Backend Primary falhou${NC}"
    exit 1
fi

# Aguardar CPU estabilizar
echo "⏳ Aguardando CPU estabilizar..."
for i in {1..10}; do
    if check_cpu 30; then
        echo -e "${GREEN}✅ CPU estável${NC}"
        break
    fi
    sleep 3
done

# TIER 2: Serviços Essenciais
echo -e "${GREEN}▶ TIER 2: Serviços Essenciais${NC}"

# MCP Orchestrator
if ! pgrep -f "run_mcp_orchestrator.py" > /dev/null; then
    echo "🌐 Iniciando MCP Orchestrator..."
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py" > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
    sleep 5
    [ -n "$(pgrep -f 'run_mcp_orchestrator.py')" ] && echo -e "${GREEN}✅ MCP Orchestrator iniciado${NC}" || echo -e "${YELLOW}⚠️  MCP Orchestrator pode ter falhado${NC}"
fi

# Ciclo Principal
if [ ! -f "$PROJECT_ROOT/logs/main_cycle.pid" ] || ! ps -p "$(cat $PROJECT_ROOT/logs/main_cycle.pid 2>/dev/null)" > /dev/null 2>&1; then
    echo "🔄 Iniciando Ciclo Principal..."
    nohup python -m src.main > "$PROJECT_ROOT/logs/main_cycle.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/main_cycle.pid"
    sleep 3
    echo -e "${GREEN}✅ Ciclo Principal iniciado${NC}"
fi

# Daemon
echo "🤖 Iniciando Daemon..."
if [ -f "$PROJECT_ROOT/config/dashboard_auth.json" ]; then
    DASH_USER=$(python3 -c "import json; print(json.load(open('$PROJECT_ROOT/config/dashboard_auth.json')).get('user', ''))" 2>/dev/null || echo "admin")
    DASH_PASS=$(python3 -c "import json; print(json.load(open('$PROJECT_ROOT/config/dashboard_auth.json')).get('pass', ''))" 2>/dev/null || echo "")
    [ -n "$DASH_PASS" ] && curl -X POST http://localhost:8000/daemon/start -u "${DASH_USER}:${DASH_PASS}" > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ Daemon iniciado${NC}"
fi

# TIER 3: Serviços Secundários
echo -e "${GREEN}▶ TIER 3: Serviços Secundários${NC}"

# Observer Service
if [ ! -f "$PROJECT_ROOT/logs/observer_service.pid" ] || ! ps -p "$(cat $PROJECT_ROOT/logs/observer_service.pid 2>/dev/null)" > /dev/null 2>&1; then
    echo "📊 Iniciando Observer Service..."
    nohup python "$PROJECT_ROOT/scripts/canonical/system/run_observer_service.py" > "$PROJECT_ROOT/logs/observer_service.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/observer_service.pid"
    sleep 3
    echo -e "${GREEN}✅ Observer Service iniciado${NC}"
fi

# Frontend
if [ -d "web/frontend" ]; then
    cd web/frontend
    [ ! -d "node_modules" ] && npm install > /dev/null 2>&1
    if [ ! -f "$PROJECT_ROOT/logs/frontend.pid" ] || ! ps -p "$(cat $PROJECT_ROOT/logs/frontend.pid 2>/dev/null)" > /dev/null 2>&1; then
        echo "🎨 Iniciando Frontend..."
        nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
        echo $! > "$PROJECT_ROOT/logs/frontend.pid"
        sleep 5
        if check_health "http://localhost:3000" 10 2; then
            echo -e "${GREEN}✅ Frontend iniciado${NC}"
        else
            echo -e "${YELLOW}⚠️  Frontend pode estar iniciando...${NC}"
        fi
    fi
    cd "$PROJECT_ROOT"
fi

echo ""
echo -e "${GREEN}✨ Inicialização Sequencial Completa!${NC}"
echo "📊 Status dos serviços:"
ps aux | grep -E "(uvicorn|python.*main|npm)" | grep -v grep | head -10
