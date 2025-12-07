#!/bin/bash
# Script de inicialização SECUNDÁRIA do OmniMind
# Fase 2: Serviços não-essenciais (Daemon + Frontend + Monitor + Ciclo Principal)
# Executado após 30s da inicialização dos serviços essenciais
# Autor: Fabrício da Silva + assistência de IA

set -e

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Serviços Secundários OmniMind (Fase 2)...${NC}"

# 🔧 CRÍTICO: Ativar venv
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✅ Venv ativado: $VIRTUAL_ENV"
else
    echo -e "${RED}❌ Venv não encontrado em $PROJECT_ROOT/.venv${NC}"
    exit 1
fi

# Verificar se serviços essenciais estão rodando
echo "🔍 Verificando serviços essenciais..."
if ! curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${RED}❌ Serviços essenciais não estão rodando!${NC}"
    echo "   Aguardando mais 10s..."
    sleep 10
    if ! curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${RED}❌ Serviços essenciais ainda não estão disponíveis. Abortando.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Serviços essenciais confirmados${NC}"

# Ler credenciais
AUTH_FILE="$PROJECT_ROOT/config/dashboard_auth.json"
if [ -f "$AUTH_FILE" ]; then
    DASH_USER=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('user', ''))" 2>/dev/null || echo "admin")
    DASH_PASS=$(python3 -c "import json; print(json.load(open('$AUTH_FILE')).get('pass', ''))" 2>/dev/null || echo "")
else
    DASH_USER="admin"
    DASH_PASS=""
fi

export OMNIMIND_DASHBOARD_USER="$DASH_USER"
export OMNIMIND_DASHBOARD_PASS="$DASH_PASS"

# 1. Iniciar Ciclo Principal com Autopoiese
echo -e "${GREEN}🔄 Iniciando Ciclo Principal OmniMind...${NC}"
cd "$PROJECT_ROOT"
mkdir -p logs data/autopoietic/synthesized_code data/monitor

# Verificar se já está rodando
if [ -f "logs/main_cycle.pid" ]; then
    OLD_PID=$(cat logs/main_cycle.pid 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ciclo Principal já está rodando (PID $OLD_PID)${NC}"
    else
        nohup python -m src.main > logs/main_cycle.log 2>&1 &
        MAIN_CYCLE_PID=$!
        echo $MAIN_CYCLE_PID > logs/main_cycle.pid
        echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
    fi
else
    nohup python -m src.main > logs/main_cycle.log 2>&1 &
    MAIN_CYCLE_PID=$!
    echo $MAIN_CYCLE_PID > logs/main_cycle.pid
    echo "✓ Ciclo Principal iniciado (PID $MAIN_CYCLE_PID)"
fi

sleep 3

# 2. Iniciar Daemon
echo -e "${GREEN}🤖 Iniciando OmniMind Daemon...${NC}"
if [ -n "$DASH_PASS" ]; then
    curl -X POST http://localhost:8000/daemon/start \
        -u "${DASH_USER}:${DASH_PASS}" \
        > logs/daemon_start.log 2>&1 || echo -e "${YELLOW}⚠️  Falha ao iniciar daemon via API${NC}"
else
    echo -e "${YELLOW}⚠️  Senha não encontrada, pulando inicialização do daemon via API${NC}"
fi

sleep 2

# 3. Iniciar Frontend
echo -e "${GREEN}🎨 Iniciando Frontend...${NC}"
cd "$PROJECT_ROOT/web/frontend"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do Frontend..."
    npm install
fi

# Verificar se já está rodando
if [ -f "../../logs/frontend.pid" ]; then
    OLD_PID=$(cat ../../logs/frontend.pid 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Frontend já está rodando (PID $OLD_PID)${NC}"
    else
        nohup npm run dev > ../../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../../logs/frontend.pid
        echo "✓ Frontend iniciado (PID $FRONTEND_PID)"
    fi
else
    nohup npm run dev > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../../logs/frontend.pid
    echo "✓ Frontend iniciado (PID $FRONTEND_PID)"
fi

# 4. Iniciar eBPF Monitor (se disponível)
echo -e "${GREEN}📊 Verificando eBPF Monitor...${NC}"
cd "$PROJECT_ROOT"

if command -v bpftrace &> /dev/null; then
    EBPF_LOG="logs/ebpf_monitor.log"
    mkdir -p logs

    # Parar eBPF anterior
    pkill -f "bpftrace.*monitor_mcp_bpf" || true
    sleep 1

    # Iniciar em background
    if [ -f "scripts/canonical/system/secure_run.py" ]; then
        python3 scripts/canonical/system/secure_run.py bpftrace scripts/canonical/system/monitor_mcp_bpf.bt > "${EBPF_LOG}" 2>&1 &
    else
        sudo bpftrace scripts/canonical/system/monitor_mcp_bpf.bt > "${EBPF_LOG}" 2>&1 &
    fi
    sleep 2
    echo -e "${GREEN}✅ eBPF Monitor ativo${NC}"
else
    echo -e "${YELLOW}⚠️  bpftrace não encontrado${NC}"
fi

echo -e "${GREEN}✅ Serviços Secundários Iniciados!${NC}"
echo "   Ciclo Principal: logs/main_cycle.log"
echo "   Frontend: http://localhost:3000"
echo "   eBPF Monitor: logs/ebpf_monitor.log"

