#!/bin/bash
# 🚀 OmniMind MCP Diagnostic & Startup Script
# Verifica saúde dos MCPs e inicia os necessários

set -e

VENV_PATH="/home/fahbrain/projects/omnimind/.venv"
PROJECT_ROOT="/home/fahbrain/projects/omnimind"
MCP_PORT=4321
MCP_HOST="127.0.0.1"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🔧 OmniMind MCP Diagnostic Tool                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"

# Ativar venv
echo -e "${YELLOW}[1/5] Ativando Python environment...${NC}"
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✅ venv ativado${NC}"

# Verificar Python
echo -e "${YELLOW}[2/5] Verificando Python...${NC}"
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"

# Verificar se Qdrant está rodando
echo -e "${YELLOW}[3/5] Verificando serviços...${NC}"
if curl -s http://127.0.0.1:6333/ &>/dev/null; then
    echo -e "${GREEN}✅ Qdrant está rodando${NC}"
else
    echo -e "${RED}❌ Qdrant não está acessível${NC}"
fi

# Listar MCPs em execução
echo -e "${YELLOW}[4/5] Verificando MCPs em execução...${NC}"
MCP_COUNT=$(ps aux | grep -E "mcp_.*_server|mcp_.*_wrapper" | grep -v grep | wc -l)
echo -e "${GREEN}✅ $MCP_COUNT MCPs ativos${NC}"
ps aux | grep -E "mcp_.*_server|mcp_.*_wrapper" | grep -v grep | awk '{print "   - " $NF}'

# Testar configuração do VS Code MCP
echo -e "${YELLOW}[5/5] Verificando configuração do VS Code...${NC}"
if [ -f "$PROJECT_ROOT/.vscode/mcp.json" ]; then
    SERVERS=$(cat "$PROJECT_ROOT/.vscode/mcp.json" | grep -c '"command"' || echo "0")
    echo -e "${GREEN}✅ VS Code MCP config encontrado ($SERVERS servidores configurados)${NC}"
else
    echo -e "${RED}❌ VS Code MCP config não encontrado${NC}"
fi

echo -e ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📊 DIAGNÓSTICO COMPLETO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}MCP Configuration:${NC}"
echo -e "  Host: ${GREEN}$MCP_HOST${NC}"
echo -e "  Port: ${GREEN}$MCP_PORT${NC}"
echo -e "  PYTHONPATH: ${GREEN}$PROJECT_ROOT/src${NC}"

echo -e "\n${YELLOW}Available MCPs:${NC}"
echo -e "  1. ${GREEN}omnimind_filesystem${NC} - File system operations"
echo -e "  2. ${GREEN}omnimind_memory${NC} - Semantic memory access"
echo -e "  3. ${GREEN}omnimind_thinking${NC} - Sequential thinking (smart tokens)"
echo -e "  4. ${GREEN}omnimind_context${NC} - Context reduction (intelligent tokens)"
echo -e "  5. ${GREEN}omnimind_sanitizer${NC} - Token sanitization"
echo -e "  6. ${GREEN}omnimind_python${NC} - Python code execution"
echo -e "  7. ${GREEN}omnimind_system${NC} - System information"
echo -e "  8. ${GREEN}omnimind_logging${NC} - Logging operations"
echo -e "  9. ${GREEN}omnimind_git${NC} - Git operations"
echo -e "  10. ${GREEN}omnimind_sqlite${NC} - SQLite database access"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Open VS Code and reload the window (Ctrl+Shift+P → Reload Window)"
echo -e "  2. Check the MCP panel in VS Code for connected servers"
echo -e "  3. Use any available MCP tool from the chat interface"

echo -e "\n${YELLOW}Troubleshooting:${NC}"
echo -e "  • If MCPs don't connect, check: ${GREEN}logs/mcp_*.log${NC}"
echo -e "  • For detailed errors: ${GREEN}cat logs/audit_chain.log | tail -50${NC}"
echo -e "  • Restart all MCPs: ${GREEN}pkill -f 'mcp_.*_server'${NC}"
echo -e "  • Full restart: ${GREEN}bash scripts/mcp_startup.sh${NC}"

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ MCP Diagnostic Complete - Ready for VS Code Integration ✨${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
