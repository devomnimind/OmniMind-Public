#!/bin/bash
# Script para iniciar Dashboard de Status dos MCPs
# Portas: 4350 (dashboard)
# Verifica saúde de todos MCPs: 4321-4337

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DASHBOARD_PORT=4350

echo "🚀 Iniciando Dashboard de Status dos MCPs..."
echo "   Porto: ${DASHBOARD_PORT}"
echo "   URL: http://127.0.0.1:${DASHBOARD_PORT}/dashboard"

# Verificar se portas dos MCPs estão disponíveis
check_mcps_running() {
    local mcps_running=0
    for port in 4321 4322 4323 4331 4332 4333 4334 4335 4336 4337; do
        if timeout 2 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null; then
            ((mcps_running++))
        fi
    done
    echo "   ✓ $mcps_running/10 MCPs detectados"
}

check_mcps_running

# Iniciar Dashboard
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Check if venv exists and use it, otherwise use python3
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -m src.integrations.mcp_dashboard_server &
DASHBOARD_PID=$!

echo "✅ Dashboard iniciado (PID: $DASHBOARD_PID)"
echo ""
echo "📊 Endpoints disponíveis:"
echo "   • http://127.0.0.1:${DASHBOARD_PORT}/dashboard  - HTML dashboard"
echo "   • http://127.0.0.1:${DASHBOARD_PORT}/status     - JSON status"
echo "   • http://127.0.0.1:${DASHBOARD_PORT}/metrics    - Detailed metrics"

# Aguardar prontonidadefor i in {1..30}; do
    if curl -s "http://127.0.0.1:${DASHBOARD_PORT}/status" >/dev/null 2>&1; then
        echo "✅ Dashboard ready!"
        break
    fi
    if [ $i -eq 1 ]; then
        echo "   Waiting for dashboard to start..."
    fi
    sleep 1
done

wait $DASHBOARD_PID
