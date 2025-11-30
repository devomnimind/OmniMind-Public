#!/bin/bash
###############################################################################
# Script para executar a suite completa de 3919 testes em background
# Salva logs para auditoria e depuração
# Tempo esperado: 2-4 horas
###############################################################################

set -e

cd /home/fahbrain/projects/omnimind

# Criar diretório de logs
mkdir -p data/test_reports

# Data/hora do início
START_TIME=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="data/test_reports/pytest_full_suite_${START_TIME}.log"

echo "🚀 Iniciando suite completa de 3919 testes..."
echo "📝 Logs salvos em: $LOG_FILE"
echo "⏱️  Tempo estimado: 2-4 horas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Executar testes
pytest tests/ \
  -v \
  --tb=short \
  -W ignore::DeprecationWarning \
  --timeout=600 \
  --maxfail=999 \
  --durations=20 \
  2>&1 | tee "$LOG_FILE"

# Estatísticas
TOTAL_LINES=$(wc -l < "$LOG_FILE")
PASSED=$(grep -c "PASSED" "$LOG_FILE" || echo 0)
FAILED=$(grep -c "FAILED" "$LOG_FILE" || echo 0)
ERRORS=$(grep -c "ERROR" "$LOG_FILE" || echo 0)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Testes PASSED: $PASSED"
echo "❌ Testes FAILED: $FAILED"
echo "⚠️  Testes ERRORS: $ERRORS"
echo "📊 Total de linhas de log: $TOTAL_LINES"
echo "📁 Arquivo: $LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
