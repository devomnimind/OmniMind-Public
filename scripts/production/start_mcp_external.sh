#!/bin/bash
set -euo pipefail

# Determine project root
BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$BASEDIR"

export PYTHONPATH=$BASEDIR

# External Servers Configuration
# filesystem: 4331
# git: 4332
# python: 4333
# sqlite: 4334
# system_info: 4335
# logging: 4336
# supabase: 4337

echo "🚀 Starting External MCP Servers..."

# Ensure logs directory exists
mkdir -p logs

start_server() {
    local name=$1
    local module=$2
    local port=$3

    echo "📦 Starting External $name MCP ($port)..."
    # Set MCP_PORT explicitly to override defaults
    MCP_PORT=$port nohup python -m "$module" > "logs/mcp_external_$name.log" 2>&1 &
    echo $! > "logs/mcp_external_$name.pid"
    echo "   PID: $!"
}

start_server "filesystem" "src.integrations.mcp_filesystem_wrapper" 4331
start_server "git" "src.integrations.mcp_git_wrapper" 4332
start_server "python" "src.integrations.mcp_python_server" 4333
start_server "sqlite" "src.integrations.mcp_sqlite_wrapper" 4334
start_server "system_info" "src.integrations.mcp_system_info_server" 4335
start_server "logging" "src.integrations.mcp_logging_server" 4336
start_server "supabase" "src.integrations.mcp_supabase_wrapper" 4337

echo "✅ External MCP Servers started."
