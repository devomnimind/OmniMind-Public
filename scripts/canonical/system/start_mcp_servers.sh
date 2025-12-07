#!/bin/bash
# Ensure we are in the project root
cd "$(dirname "$0")/.."

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
"$(pwd)/.venv/bin/python" scripts/run_mcp_orchestrator.py &
MCP_PID=$!
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

