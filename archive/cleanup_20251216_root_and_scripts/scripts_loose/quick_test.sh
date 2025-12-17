#!/bin/bash

# ============================================================================
# 🧪 OMNIMIND TEST SUITE - QUICK START
# ============================================================================
# Este script inicia os testes com autodefesa ativada
# Pré-requisitos: sudo configurado (execute configure_sudo_omnimind.sh uma vez)
# ============================================================================

set -e

cd /home/fahbrain/projects/omnimind

echo "🧠 OMNIMIND TEST SUITE COM AUTODEFESA"
echo "======================================"
echo ""
echo "✅ Verificações pré-requisito:"

# 1. Verificar sudoers
if sudo -n bash -c "echo 'sudo OK'" 2>/dev/null; then
    echo "   ✅ Sudo configurado (sem pedir senha)"
else
    echo "   ❌ Sudo requer senha. Executar:"
    echo "      bash scripts/configure_sudo_omnimind.sh"
    exit 1
fi

# 2. Limpar processos antigos
echo "   🧹 Limpando processos antigos..."
pkill -f "uvicorn web.backend.main:app" || true
pkill -f "bpftrace.*monitor_mcp_bpf" || true
sleep 2

# 3. Iniciar servidor com sudo (não pede senha)
echo ""
echo "🚀 Iniciando servidor backend..."
sudo -n bash scripts/start_omnimind_system_sudo.sh &
SERVER_PID=$!

# Aguardar servidor subir
echo "⏳ Aguardando servidor inicializar (15s)..."
sleep 15

# Verificar se servidor está online
if curl -s http://localhost:8000/health/ > /dev/null; then
    echo "✅ Servidor online em http://localhost:8000"
else
    echo "❌ Servidor não respondeu"
    exit 1
fi

# 4. Executar testes
echo ""
echo "🧪 Executando suite de testes (~3952 testes)..."
echo "   Modo: GPU=true, Dev=true, Debug=true"
echo "   Autodefesa: ATIVADA (detecta testes perigosos)"
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="data/test_reports"

OMNIMIND_GPU=true \
OMNIMIND_DEV=true \
OMNIMIND_DEBUG=true \
pytest tests/ \
  -vv \
  --tb=short \
  --log-cli-level=DEBUG \
  --log-file="$LOG_DIR/pytest_${TIMESTAMP}.log" \
  --junit-xml="$LOG_DIR/junit_${TIMESTAMP}.xml" \
  --html="$LOG_DIR/report_${TIMESTAMP}.html" \
  --self-contained-html \
  --durations=20 \
  -s \
  2>&1 | tee "$LOG_DIR/output_${TIMESTAMP}.log"

echo ""
echo "======================================"
echo "✅ TESTES FINALIZADOS"
echo "======================================"
echo "📋 Logs em: $LOG_DIR"
echo ""
echo "🛡️  Verificar AUTODEFESA:"
echo "   grep 'RELATÓRIO DE AUTODEFESA' $LOG_DIR/output_${TIMESTAMP}.log"
