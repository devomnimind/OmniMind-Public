#!/bin/bash
# Ensure we are in the project root
# CORREÇÃO: Calcular PROJECT_ROOT de forma robusta (mesma lógica de start_omnimind_system.sh)
if [ -n "${OMNIMIND_PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT="$OMNIMIND_PROJECT_ROOT"
else
    # Procurar pela raiz do projeto procurando arquivos de identidade
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT=""
    while [ "$SCRIPT_DIR" != "/" ]; do
        if [ -f "$SCRIPT_DIR/.env" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ] || [ -f "$SCRIPT_DIR/config/omnimind.yaml" ]; then
            PROJECT_ROOT="$SCRIPT_DIR"
            break
        fi
        SCRIPT_DIR="$(dirname "$SCRIPT_DIR")"
    done
    # Fallback: assumir que estamos em scripts/canonical/system
    if [ -z "$PROJECT_ROOT" ]; then
        PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
    fi
fi
cd "$PROJECT_ROOT" || { echo "❌ Erro: Não foi possível entrar em $PROJECT_ROOT"; exit 1; }

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
source .venv/bin/activate

# Ensure PATH includes .venv/bin
export PATH="$(pwd)/.venv/bin:$PATH"

echo -e "${GREEN}🌐 Iniciando MCP Servers + eBPF Monitor...${NC}\n"

# 1. Iniciar MCP Orchestrator
echo -e "${YELLOW}[1/2] Iniciando MCP Orchestrator...${NC}"
# CORREÇÃO: Usar caminho completo do script
MCP_ORCHESTRATOR_SCRIPT="$PROJECT_ROOT/scripts/canonical/system/run_mcp_orchestrator.py"
if [ -f "$MCP_ORCHESTRATOR_SCRIPT" ]; then
    chmod +x "$MCP_ORCHESTRATOR_SCRIPT" 2>/dev/null || true
    nohup "$PROJECT_ROOT/.venv/bin/python" "$MCP_ORCHESTRATOR_SCRIPT" > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > "$PROJECT_ROOT/logs/mcp_orchestrator.pid" 2>/dev/null || true
else
    echo -e "${RED}⚠️  Script não encontrado: $MCP_ORCHESTRATOR_SCRIPT${NC}"
    echo -e "${YELLOW}   Tentando iniciar servidores MCP diretamente via módulo...${NC}"
    # Fallback: tentar iniciar via módulo Python
    nohup "$PROJECT_ROOT/.venv/bin/python" -m src.integrations.mcp_orchestrator > "$PROJECT_ROOT/logs/mcp_orchestrator.log" 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > "$PROJECT_ROOT/logs/mcp_orchestrator.pid" 2>/dev/null || true
fi
sleep 3

# 2. Iniciar eBPF Monitor Contínuo
echo -e "${YELLOW}[2/2] Iniciando eBPF Monitor Contínuo...${NC}"
if command -v bpftrace &> /dev/null; then
    EBPF_LOG="$(pwd)/logs/ebpf_monitor.log"
    mkdir -p logs
    # Parar eBPF anterior
    sudo pkill -f "bpftrace.*monitor_mcp_bpf" || true
    sleep 1
    # Iniciar em background
    sudo bash -c "nohup bpftrace '$(pwd)/scripts/canonical/system/monitor_mcp_bpf.bt' > '${EBPF_LOG}' 2>&1 &"
    sleep 2
    echo -e "${GREEN}✅ eBPF Monitor ativo${NC}"
    echo -e "   📊 Log: tail -f ${EBPF_LOG}\n"
else
    echo -e "${RED}⚠️  bpftrace não encontrado. Instale com: sudo apt install bpftrace${NC}"
fi

echo -e "${GREEN}✨ MCP Servers iniciados com sucesso!${NC}"
echo -e "   🌐 MCP Orchestrator: PID ${MCP_PID}"
echo -e "   📊 eBPF Monitor: Contínuo"
echo -e "   📁 Logs: logs/\n"

# Aguardar
wait $MCP_PID

