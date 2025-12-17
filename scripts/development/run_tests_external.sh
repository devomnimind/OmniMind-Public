#!/bin/bash

# ============================================================================
# 🖥️  OMNIMIND FAST TEST SUITE - EXECUÇÃO EXTERNA
# ============================================================================
# Executa suite rápida SEM VS Code aberto (libera memória/recursos)
# Salva todos os logs e relatórios para análise posterior
#
# VANTAGENS:
#   - Mais memória disponível (sem VS Code)
#   - Mais CPU disponível (sem Copilot/extensions)
#   - GPU mais limpa (sem preview de código)
#   - Relatórios salvos para análise offline
#
# USO:
#   # Feche o VS Code e execute:
#   bash scripts/development/run_tests_external.sh
#
#   # Depois, analise os logs:
#   bash scripts/development/analyze_test_logs.sh
#
# ============================================================================

set -e

cd /home/fahbrain/projects/omnimind

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="data/test_reports"
mkdir -p "$LOG_DIR"

# Arquivos de saída
OUTPUT_LOG="$LOG_DIR/external_output_${TIMESTAMP}.log"
PYTEST_LOG="$LOG_DIR/external_pytest_${TIMESTAMP}.log"
JUNIT_XML="$LOG_DIR/external_junit_${TIMESTAMP}.xml"
COVERAGE_JSON="$LOG_DIR/external_coverage_${TIMESTAMP}.json"
COVERAGE_HTML="$LOG_DIR/external_coverage_${TIMESTAMP}_html"
COVERAGE_XML="$LOG_DIR/external_coverage_${TIMESTAMP}.xml"
METRICS_JSON="$LOG_DIR/external_metrics_${TIMESTAMP}.json"
CONSOLIDATED_OUTPUT="$LOG_DIR/external_consolidated_${TIMESTAMP}.log"

echo "🖥️  OMNIMIND FAST TEST SUITE - EXECUÇÃO EXTERNA"
echo "======================================"
echo "⏱️  Timestamp: $TIMESTAMP"
echo "🧠 Memória disponível (MB):"
free -m | grep Mem | awk '{print "   Total: " $2 ", Livre: " $7 ", Usado: " $3}'
echo "🎮 GPU status:"
nvidia-smi --query-gpu=memory.total,memory.free,memory.used --format=csv,noheader | awk '{print "   Total: " $1 ", Livre: " $3 ", Usado: " $5}'
echo "======================================"
echo ""

# Contar testes
echo "📊 Contando testes disponíveis..."
EXPECTED_TESTS=$(python3 -m pytest --collect-only -q tests/ -m "not chaos" 2>/dev/null | tail -1 || echo "calculando...")
if [ "$EXPECTED_TESTS" != "calculando..." ] && [ -n "$EXPECTED_TESTS" ]; then
    echo "📊 Testes encontrados: $EXPECTED_TESTS"
else
    echo "📊 Testes: calculando durante execução..."
fi
echo ""

# Executar pytest com GPU forçada
echo "🚀 Iniciando pytest..."
echo ""

CUDA_VISIBLE_DEVICES=0 \
OMNIMIND_GPU=true \
OMNIMIND_FORCE_GPU=true \
OMNIMIND_DEV=true \
OMNIMIND_DEBUG=true \
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
python3 -m pytest tests/ \
  -vv \
  --tb=long \
  -m "not chaos" \
  --cache-clear \
  --log-cli-level=DEBUG \
  --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s" \
  --log-cli-date-format="%Y-%m-%d %H:%M:%S" \
  --log-file="$PYTEST_LOG" \
  --log-file-level=DEBUG \
  --junit-xml="$JUNIT_XML" \
  --cov=src \
  --cov-report=json:"$COVERAGE_JSON" \
  --cov-report=html:"$COVERAGE_HTML" \
  --cov-report=xml:"$COVERAGE_XML" \
  --cov-report=term-missing \
  --durations=10 \
  -s \
  2>&1 | tee "$OUTPUT_LOG"

EXIT_CODE=$?

# Aguardar garantir que arquivos foram escritos
sleep 2

# Consolidar métricas
if [ -f "data/test_reports/metrics_report.json" ]; then
    echo ""
    echo "📊 Copiando métricas JSON..."
    cp "data/test_reports/metrics_report.json" "$METRICS_JSON"
    echo "   ✅ Métricas: $METRICS_JSON"
fi

# Consolidar tudo em um arquivo
echo ""
echo "📦 Consolidando dados..."
{
    echo "=========================================="
    echo "OMNIMIND EXTERNAL TEST SUITE - CONSOLIDADO"
    echo "=========================================="
    echo "Timestamp: $TIMESTAMP"
    echo "Exit Code: $EXIT_CODE"
    echo ""
    echo "=========================================="
    echo "1. STDOUT/STDERR COMPLETO"
    echo "=========================================="
    cat "$OUTPUT_LOG"
    echo ""
    echo "=========================================="
    echo "2. MÉTRICAS JSON"
    echo "=========================================="
    if [ -f "$METRICS_JSON" ]; then
        cat "$METRICS_JSON"
    else
        echo "⚠️  Métricas não geradas"
    fi
    echo ""
    echo "=========================================="
    echo "3. RELATÓRIOS GERADOS"
    echo "=========================================="
    echo "📝 Pytest log: $PYTEST_LOG"
    echo "📊 Junit XML: $JUNIT_XML"
    echo "📊 Coverage JSON: $COVERAGE_JSON"
    echo "📊 Coverage HTML: $COVERAGE_HTML"
    echo "📊 Coverage XML: $COVERAGE_XML"
    echo ""
} > "$CONSOLIDATED_OUTPUT"

echo ""
echo "✅ TESTES FINALIZADOS"
echo "======================================"
echo "📋 Arquivo consolidado:"
echo "   $CONSOLIDATED_OUTPUT"
echo ""
echo "📊 Relatórios salvos em:"
echo "   📁 $LOG_DIR/"
echo ""
echo "💡 Próximos passos:"
echo "   1. Ver logs: less $CONSOLIDATED_OUTPUT"
echo "   2. Analisar erros: grep ERROR $CONSOLIDATED_OUTPUT | head -20"
echo "   3. Ver métricas: cat $METRICS_JSON | jq"
echo "   4. Ver coverage: xdg-open $COVERAGE_HTML/index.html"
echo ""

exit $EXIT_CODE
