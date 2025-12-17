#!/bin/bash
set -euo pipefail

echo "🚀 Iniciando servidores MCP do OmniMind..."

BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Iniciar Internal e External
bash "$BASEDIR/start_mcp_internal.sh"
bash "$BASEDIR/start_mcp_external.sh"

echo ""
echo "🎯 Todos os servidores MCP foram iniciados!"
echo "📊 Para verificar status: ps aux | grep mcp"
echo "🛑 Para parar: pkill -f mcp"
