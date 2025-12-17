#!/bin/bash
# 🚀 MCP Startup Script - Inicia todos os servidores OmniMind MCP

set -e

VENV="/home/fahbrain/projects/omnimind/.venv"
PROJECT_ROOT="/home/fahbrain/projects/omnimind"
LOG_DIR="$PROJECT_ROOT/logs"

# Criar diretório de logs se não existir
mkdir -p "$LOG_DIR"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Iniciando Servidores MCP OmniMind${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Ativar venv
source "$VENV/bin/activate"

# Kill processos antigos
echo -e "${YELLOW}Limpando processos antigos...${NC}"
pkill -f "mcp_.*_server|mcp_.*_wrapper" 2>/dev/null || true
sleep 1

# Array de MCPs para iniciar
declare -a MCPS=(
    "omnimind_filesystem:src.integrations.mcp_filesystem_wrapper"
    "omnimind_memory:src.integrations.mcp_memory_server"
    "omnimind_thinking:src.integrations.mcp_thinking_server"
    "omnimind_context:src.integrations.mcp_context_server"
    "omnimind_sanitizer:src.integrations.mcp_sanitizer"
    "omnimind_python:src.integrations.mcp_python_server"
    "omnimind_system:src.integrations.mcp_system_info_server"
    "omnimind_logging:src.integrations.mcp_logging_server"
    "omnimind_git:src.integrations.mcp_git_wrapper"
    "omnimind_sqlite:src.integrations.mcp_sqlite_wrapper"
)

# Iniciar cada MCP
for MCP in "${MCPS[@]}"; do
    NAME="${MCP%%:*}"
    MODULE="${MCP##*:}"

    echo -e "${YELLOW}Iniciando $NAME...${NC}"

    nohup python -m "$MODULE" \
        > "$LOG_DIR/mcp_${NAME}.log" 2>&1 &

    PID=$!
    echo "$PID" > "$LOG_DIR/mcp_${NAME}.pid"

    sleep 0.5

    if ps -p $PID > /dev/null; then
        echo -e "${GREEN}✅ $NAME iniciado (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  $NAME pode ter falha no início, verifique logs${NC}"
    fi
done

sleep 2

# Verificar todos estão rodando
echo -e ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📊 Status dos MCPs:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

RUNNING=$(ps aux | grep -E "mcp_.*_server|mcp_.*_wrapper" | grep -v grep | wc -l)
echo -e "${GREEN}✅ $RUNNING MCPs em execução${NC}"

echo -e "\n${YELLOW}Logs disponíveis em:${NC}"
ls -la "$LOG_DIR"/mcp_*.log 2>/dev/null | awk '{print "  " $NF}' | sort

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ MCPs Inicializados com Sucesso ✨${NC}"
echo -e "${YELLOW}Próxima ação: Recarregue VS Code (Ctrl+Shift+P → Reload Window)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
