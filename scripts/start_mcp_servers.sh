#!/bin/bash
set -euo pipefail

echo "🚀 Iniciando servidores MCP do OmniMind..."

BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASEDIR/.."

# Carregar variáveis de ambiente
if [[ -f ".env" ]]; then
    source .env
fi

# Função para iniciar um servidor MCP
start_mcp_server() {
    local server_name=$1
    local server_script=$2
    
    echo "📦 Iniciando MCP $server_name..."
    
    if [[ -f "$server_script" ]]; then
        nohup python "$server_script" > "logs/mcp_$server_name.log" 2>&1 &
        echo $! > "logs/mcp_$server_name.pid"
        echo "✅ MCP $server_name iniciado (PID: $!)"
    else
        echo "⚠️ Script $server_script não encontrado para $server_name"
    fi
}

# Iniciar todos os servidores MCP
MCP_SERVERS=(
    "filesystem:src/integrations/mcp/filesystem_server.py"
    "memory:src/integrations/mcp/memory_server.py"
    "sequential_thinking:src/integrations/mcp/sequential_thinking_server.py"
    "context:src/integrations/mcp/context_server.py"
    "git:src/integrations/mcp/git_server.py"
    "python:src/integrations/mcp/python_server.py"
    "sqlite:src/integrations/mcp/sqlite_server.py"
    "system_info:src/integrations/mcp/system_info_server.py"
    "logging:src/integrations/mcp/logging_server.py"
)

for server_info in "${MCP_SERVERS[@]}"; do
    IFS=':' read -r name script <<< "$server_info"
    start_mcp_server "$name" "$script"
    sleep 1
done

echo ""
echo "🎯 Todos os servidores MCP foram iniciados!"
echo "📊 Para verificar status: ps aux | grep mcp"
echo "🛑 Para parar: pkill -f mcp"
