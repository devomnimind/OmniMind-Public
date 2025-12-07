#!/bin/bash
# Validação de setup eBPF + Systemd para MCP
# Script de diagnóstico: ./validate_mcp_setup.sh

set -e

echo "=================================="
echo "🔍 MCP Setup Validation"
echo "=================================="
echo ""

# 1. Verificar bpftrace
echo "✓ Checking bpftrace..."
if command -v bpftrace &> /dev/null; then
    VERSION=$(bpftrace --version 2>/dev/null | head -1)
    echo "  ✅ bpftrace found: ${VERSION}"
else
    echo "  ❌ bpftrace NOT found. Install: sudo apt install bpftrace"
    exit 1
fi

# 2. Verificar scripts
echo ""
echo "✓ Checking scripts..."
SCRIPTS=(
    "scripts/canonical/system/monitor_mcp_bpf.bt"
    "scripts/test_mcp_stress.py"
    "scripts/run_mcp_benchmark.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo "  ✅ $script (executable)"
    else
        echo "  ❌ $script (missing or not executable)"
    fi
done

# 3. Verificar systemd templates
echo ""
echo "✓ Checking systemd templates..."
USER_SYSTEMD="${HOME}/.config/systemd/user"

for unit in "omnimind-mcp@.service" "omnimind-mcp.target"; do
    if [ -f "${USER_SYSTEMD}/${unit}" ]; then
        echo "  ✅ ${unit}"
    else
        echo "  ❌ ${unit} NOT found in ${USER_SYSTEMD}/"
    fi
done

# 4. Verificar kernel headers
echo ""
echo "✓ Checking kernel headers..."
KERNEL_VERSION=$(uname -r)
HEADERS_PATH="/lib/modules/${KERNEL_VERSION}/build"
if [ -d "${HEADERS_PATH}" ]; then
    echo "  ✅ Kernel headers found: ${HEADERS_PATH}"
else
    echo "  ❌ Kernel headers NOT found. Install: sudo apt install linux-headers-$(uname -r)"
fi

# 5. Verificar MCP orchestrator
echo ""
echo "✓ Checking MCP orchestrator..."
if [ -f "src/integrations/mcp_orchestrator.py" ]; then
    echo "  ✅ mcp_orchestrator.py found"
else
    echo "  ❌ mcp_orchestrator.py NOT found"
fi

# 6. Verificar configuração MCP
echo ""
echo "✓ Checking MCP configuration..."
if [ -f "config/mcp_servers.json" ]; then
    SERVERS=$(grep -o '"[^"]*": {' config/mcp_servers.json | wc -l)
    echo "  ✅ mcp_servers.json found (${SERVERS} servers configured)"
else
    echo "  ❌ mcp_servers.json NOT found"
fi

# 7. Verificar documentação
echo ""
echo "✓ Checking documentation..."
if [ -f "MCP_EBPF_MONITORING_SETUP.md" ]; then
    echo "  ✅ MCP_EBPF_MONITORING_SETUP.md found"
else
    echo "  ❌ MCP_EBPF_MONITORING_SETUP.md NOT found"
fi

# 8. Resumo final
echo ""
echo "=================================="
echo "✅ SETUP VALIDATION COMPLETE"
echo "=================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "  1. Aguarde testes terminarem"
echo "  2. Execute: sudo bash scripts/run_mcp_benchmark.sh 60 100"
echo "  3. Coleta output de: data/test_reports/ebpf_mcp_latency_*.txt"
echo "  4. Compartilhe resultados para decisão LKM"
echo ""
echo "📖 Ver documentação:"
echo "  cat MCP_EBPF_MONITORING_SETUP.md"
echo ""
