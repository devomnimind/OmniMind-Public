#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║            OMNIMIND MCP STARTUP SCRIPT - All 7 MCPs                       ║
# ║  Creator: GitHub Copilot                                                  ║
# ║  Purpose: Start all 7 external MCPs with proper configuration             ║
# ║  Date: 18 de Dezembro de 2025                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_PATH/bin/python3"

# MCP Configuration
declare -A MCPS=(
    [4331]="src.integrations.mcp_filesystem_server:Filesystem"
    [4332]="src.integrations.mcp_git_wrapper:Git"
    [4333]="src.integrations.mcp_python_server:Python"
    [4334]="src.integrations.mcp_sqlite_wrapper:SQLite"
    [4335]="src.integrations.mcp_system_info_server:System-Info"
    [4336]="src.integrations.mcp_logging_server:Logging"
    [4337]="src.integrations.mcp_supabase_wrapper:Supabase"
)

# PID tracking
declare -A MCP_PIDS
PIDFILE="/tmp/omnimind_mcps.pids"

# ════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${CYAN}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

cleanup_ports() {
    log_info "Limping up ports 4331-4337..."
    for port in {4331..4337}; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            fuser -k $port/tcp 2>/dev/null || true
            log_warning "Porta $port liberada"
        fi
    done
    sleep 1
}

check_venv() {
    if [ ! -f "$PYTHON_BIN" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        log_info "Please run: python3 -m venv $VENV_PATH && source $VENV_PATH/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    log_success "Virtual environment encontrado"
}

start_mcp() {
    local port=$1
    local module_and_name=$2
    IFS=':' read -r module name <<< "$module_and_name"

    log_info "Iniciando MCP: $name (porta $port, módulo $module)"

    # Start in background with environment variable
    MCP_PORT=$port "$PYTHON_BIN" -m "$module" > /tmp/mcp_${port}.log 2>&1 &
    local pid=$!
    MCP_PIDS[$port]=$pid

    # Save to file
    echo "$port:$pid:$name:$module" >> "$PIDFILE"

    log_success "MCP $name iniciado (PID: $pid, porta: $port)"
}

wait_for_startup() {
    log_info "Aguardando inicialização dos MCPs..."
    sleep 3

    log_info "Verificando connectivity..."
    local ready=0
    for port in "${!MCPS[@]}"; do
        local result=$(curl -s --connect-timeout 1 --max-time 1 \
            "http://127.0.0.1:$port/mcp" \
            -X POST \
            -H 'Content-Type: application/json' \
            -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' 2>/dev/null || echo "")

        if echo "$result" | grep -q '"result"'; then
            log_success "Porta $port respondendo"
            ready=$((ready + 1))
        else
            log_warning "Porta $port ainda não respondendo"
        fi
    done

    return $((7 - ready))
}

save_pids() {
    > "$PIDFILE"  # Clear file
    for port in "${!MCP_PIDS[@]}"; do
        local pid=${MCP_PIDS[$port]}
        local module_name=${MCPS[$port]}
        IFS=':' read -r module name <<< "$module_name"
        echo "$port:$pid:$name:$module" >> "$PIDFILE"
    done
    log_success "PIDs salvos em $PIDFILE"
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN SCRIPT
# ════════════════════════════════════════════════════════════════════════════

log_header "OMNIMIND MCP STARTUP - All 7 External MCPs"

# Validation
check_venv
cleanup_ports

# Startup all MCPs
log_info "Iniciando todos os 7 MCPs..."
echo ""

for port in $(echo "${!MCPS[@]}" | tr ' ' '\n' | sort -n); do
    start_mcp "$port" "${MCPS[$port]}"
done

echo ""
save_pids

# Wait and verify
wait_for_startup
wait_result=$?

echo ""
log_header "STARTUP RESULT"

# Final status
for port in $(echo "${!MCPS[@]}" | tr ' ' '\n' | sort -n); do
    local pid=${MCP_PIDS[$port]}
    local module_name=${MCPS[$port]}
    IFS=':' read -r module name <<< "$module_name"

    if kill -0 "$pid" 2>/dev/null; then
        log_success "MCP $name (porta $port) - EM EXECUÇÃO"
    else
        log_error "MCP $name (porta $port) - FALHA NA INICIALIZAÇÃO"
    fi
done

echo ""
echo -e "${CYAN}📊 RESUMO:${NC}"
echo "  Total de MCPs: 7"
echo "  Status: $([ $wait_result -eq 0 ] && echo "✅ TODOS OPERACIONAIS" || echo "⚠️ ALGUNS AGUARDANDO")"
echo ""
echo -e "${CYAN}🔧 Comandos úteis:${NC}"
echo "  Ver logs:              tail -f /tmp/mcp_*.log"
echo "  Parar todos:           kill \$(cat $PIDFILE | cut -d: -f2 | tr '\n' ' ')"
echo "  Status:                ps aux | grep mcp_"
echo "  Testar MCP:            curl -X POST http://127.0.0.1:4331/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{}'"
echo ""

exit $wait_result
