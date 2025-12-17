#!/bin/bash
# Script de produção Phase 22 - Sistema completo com correções implementadas

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 INICIANDO SISTEMA OMNIMIND - PHASE 22${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Ativar venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo -e "${GREEN}✅${NC} Ambiente virtual ativado"
else
    echo -e "${RED}❌${NC} Venv não encontrado"
    exit 1
fi

# Configurar CUDA
export CUDA_HOME="/usr/local/cuda-12.4"
export CUDA_VISIBLE_DEVICES="0"
export CUDA_PATH="/usr/local/cuda-12.4"
export LD_LIBRARY_PATH="/usr/local/cuda-12.4/lib64:${LD_LIBRARY_PATH}"
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
echo -e "${GREEN}✅${NC} CUDA configurado"

# Limpar processos antigos
echo -e "${YELLOW}[1/5]${NC} Limpando processos antigos..."
pkill -f "python -m src.main" 2>/dev/null || true
pkill -f "python web/backend/main.py" 2>/dev/null || true
pkill -f "uvicorn web.backend.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅${NC} Limpeza concluída"
echo ""

# Criar diretórios necessários
echo -e "${YELLOW}[2/5]${NC} Criando estrutura de diretórios..."
mkdir -p logs data/autopoietic/synthesized_code data/monitor data/training data/sessions data/validation
echo -e "${GREEN}✅${NC} Estrutura criada"
echo ""

# Iniciar Backend
echo -e "${YELLOW}[3/5]${NC} Iniciando Backend..."
cd "$PROJECT_ROOT"
./scripts/canonical/system/run_cluster.sh > logs/backend_start.log 2>&1 &
BACKEND_PID=$!
echo "Backend iniciado (PID: $BACKEND_PID)"
echo "Aguardando inicialização (40s)..."
sleep 40

# Verificar Backend
if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Backend online"
else
    echo -e "${YELLOW}⚠️${NC} Backend pode estar ainda inicializando..."
fi
echo ""

# Iniciar Ciclo Principal (com Autopoiese Phase 22)
echo -e "${YELLOW}[4/5]${NC} Iniciando Ciclo Principal com Autopoiese (Phase 22)..."
cd "$PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH" \
nohup python -m src.main > logs/main_cycle.log 2>&1 &
MAIN_CYCLE_PID=$!
echo $MAIN_CYCLE_PID > logs/main_cycle.pid
echo -e "${GREEN}✅${NC} Ciclo Principal iniciado (PID: $MAIN_CYCLE_PID)"
echo "   Log: tail -f logs/main_cycle.log"
sleep 5
echo ""

# Iniciar Daemon (com delay para não sobrecarregar)
echo -e "${YELLOW}[5/7]${NC} Iniciando Daemon..."
sleep 5
curl -X POST http://localhost:8000/daemon/start \
  -u admin:omnimind2025! \
  > logs/daemon_start.log 2>&1 &
DAEMON_START_PID=$!
echo -e "${GREEN}✅${NC} Daemon start request enviado (PID: $DAEMON_START_PID)"
sleep 2
echo ""

# Iniciar Frontend (porta 3000 - produção)
echo -e "${YELLOW}[6/7]${NC} Iniciando Frontend (porta 3000)..."
cd "$PROJECT_ROOT/web/frontend"
if [ ! -d "node_modules" ]; then
    echo "Instalando dependências..."
    npm install > /dev/null 2>&1
fi
nohup npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../logs/frontend.pid
echo -e "${GREEN}✅${NC} Frontend iniciado (PID: $FRONTEND_PID)"
echo "   Porta: 3000 (produção)"
echo "   Log: tail -f logs/frontend.log"
sleep 3
echo ""

# Iniciar eBPF Monitor (se disponível)
echo -e "${YELLOW}[7/7]${NC} Verificando eBPF Monitor..."
cd "$PROJECT_ROOT"
if command -v bpftrace &> /dev/null; then
    EBPF_LOG="logs/ebpf_monitor.log"
    mkdir -p logs
    python3 scripts/canonical/system/secure_run.py pkill -f "bpftrace.*monitor_mcp_bpf" || true
    sleep 1
    python3 scripts/canonical/system/secure_run.py bpftrace scripts/canonical/system/monitor_mcp_bpf.bt > "${EBPF_LOG}" 2>&1 &
    echo -e "${GREEN}✅${NC} eBPF Monitor ativo"
    echo "   Log: tail -f ${EBPF_LOG}"
else
    echo -e "${YELLOW}⚠️${NC} bpftrace não encontrado (opcional)"
fi
echo ""

# Resumo
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ✅ SISTEMA INICIADO COM SUCESSO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Serviços ativos:"
echo "  • Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "  • Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "  • Ciclo Principal: PID $MAIN_CYCLE_PID"
echo "  • Daemon: Iniciado via API"
echo ""
echo "Logs:"
echo "  • Backend: tail -f logs/backend_8000.log"
echo "  • Ciclo Principal: tail -f logs/main_cycle.log"
echo "  • Frontend: tail -f logs/frontend.log"
echo "  • Daemon: tail -f logs/daemon_start.log"
echo ""
echo "Acessos:"
echo "  • Dashboard: http://localhost:3000"
echo "  • API Health: http://localhost:8000/health/"
echo "  • Métricas Consciência: http://localhost:8000/api/v1/autopoietic/consciousness/metrics?include_raw=true"
echo "  • Status Autopoiético: http://localhost:8000/api/v1/autopoietic/status"
echo ""
echo "Phase 22 - Autopoiese:"
echo "  • Componentes: data/autopoietic/synthesized_code/"
echo "  • Histórico: data/autopoietic/cycle_history.jsonl"
echo "  • Log: tail -f logs/main_cycle.log"
echo ""
echo "Para parar o sistema:"
echo "  ./scripts/stop_production.sh"
echo ""

