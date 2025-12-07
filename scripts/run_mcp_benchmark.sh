#!/bin/bash
# Script para rodar eBPF monitoring + stress test MCP
# Uso: ./run_mcp_benchmark.sh [duration] [concurrent]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DURATION=${1:-30}
CONCURRENT=${2:-50}
OUTPUT_DIR="${PROJECT_ROOT}/data/test_reports"
EBPF_OUTPUT="${OUTPUT_DIR}/ebpf_mcp_latency_$(date +%Y%m%d_%H%M%S).txt"

mkdir -p "${OUTPUT_DIR}"

echo "=================================="
echo "🚀 MCP eBPF Benchmark Started"
echo "=================================="
echo "Duration: ${DURATION}s"
echo "Concurrent: ${CONCURRENT}"
echo "Output: ${EBPF_OUTPUT}"
echo "=================================="
echo ""

# Verificar se bpftrace está disponível
if ! command -v bpftrace &> /dev/null; then
    echo "❌ bpftrace não encontrado. Instale com:"
    echo "   sudo apt install bpftrace"
    exit 1
fi

# Verificar se script eBPF existe
EBPF_SCRIPT="${PROJECT_ROOT}/scripts/canonical/system/monitor_mcp_bpf.bt"
if [ ! -f "${EBPF_SCRIPT}" ]; then
    echo "❌ Script eBPF não encontrado: ${EBPF_SCRIPT}"
    exit 1
fi

echo "⏳ Iniciando eBPF monitor em background..."
echo "   Script: ${EBPF_SCRIPT}"

# Roddar eBPF em background (requer sudo)
sudo bpftrace "${EBPF_SCRIPT}" > "${EBPF_OUTPUT}" 2>&1 &
EBPF_PID=$!

echo "   PID: ${EBPF_PID}"
sleep 2  # Dar tempo para eBPF iniciar

echo "⏳ Aguardando 5s para eBPF estabilizar..."
sleep 5

echo ""
echo "🔥 Iniciando stress test..."
cd "${PROJECT_ROOT}"

# Ativar venv e rodar stress test simples
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Rodar stress test simples (sem imports complexos)
PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}" python3 scripts/mcp_stress_simple.py \
    --duration "${DURATION}" \
    --concurrent "${CONCURRENT}" \
    --endpoint "http://localhost:8000/mcp" 2>&1 | tee -a "${EBPF_OUTPUT}"

TEST_EXIT_CODE=$?

echo ""
echo "⏹️  Parando eBPF monitor..."
sudo kill ${EBPF_PID} 2>/dev/null || true
wait ${EBPF_PID} 2>/dev/null || true

echo ""
echo "=================================="
echo "✅ Benchmark Completo"
echo "=================================="
echo ""
echo "📊 Resultados salvos em:"
echo "   ${EBPF_OUTPUT}"
echo ""
echo "📈 Ver resultados:"
echo "   cat ${EBPF_OUTPUT}"
echo ""
echo "=================================="

# Print summary
echo ""
echo "📋 SUMMARY:"
tail -30 "${EBPF_OUTPUT}"

exit ${TEST_EXIT_CODE}
