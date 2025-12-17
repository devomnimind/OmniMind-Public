#!/bin/bash
set -euo pipefail

# Determine project root
BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$BASEDIR"

export PYTHONPATH=$BASEDIR

# Internal Servers Configuration
# memory: 4321
# sequential_thinking: 4322
# context: 4323

echo "🚀 Starting Internal MCP Servers..."

# Ensure logs directory exists
mkdir -p logs

start_server() {
    local name=$1
    local module=$2
    local port=$3

    echo "📦 Starting Internal $name MCP ($port)..."
    # Set MCP_PORT explicitly to override defaults
    MCP_PORT=$port nohup python -m "$module" > "logs/mcp_internal_$name.log" 2>&1 &
    echo $! > "logs/mcp_internal_$name.pid"
    echo "   PID: $!"
}

start_server "memory" "src.integrations.mcp_memory_server" 4321
start_server "sequential_thinking" "src.integrations.mcp_thinking_server" 4322
start_server "context" "src.integrations.mcp_context_server" 4323

echo "✅ Internal MCP Servers started."
