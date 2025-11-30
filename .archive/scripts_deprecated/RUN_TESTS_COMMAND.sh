#!/bin/bash

################################################################################
#  PYTEST COMMAND - MAXFAIL=999 + DETAILED LOGGING
################################################################################

# Limpar logs antigos
echo "🧹 Limpando logs antigos..."
rm -f test_results_*.log test_output_*.txt pytest_output.log coverage.xml

# Diretório de relatórios
mkdir -p data/test_reports

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="data/test_reports/pytest_${TIMESTAMP}.log"
REPORT_FILE="data/test_reports/pytest_report_${TIMESTAMP}.txt"

echo "📊 Executando testes com maxfail=999 e logging detalhado..."
echo "📁 Relatórios serão salvos em data/test_reports/"
echo ""

# COMANDO COMPLETO COM TODAS AS OPÇÕES
pytest tests/ \
  --maxfail=999 \
  --tb=short \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=json:"data/test_reports/coverage_${TIMESTAMP}.json" \
  --cov-report=html:"data/test_reports/htmlcov_${TIMESTAMP}" \
  --log-cli-level=INFO \
  --log-file="${LOG_FILE}" \
  --log-file-level=DEBUG \
  -v \
  -W ignore::DeprecationWarning \
  --durations=20 \
  2>&1 | tee "${REPORT_FILE}"

# Status final
EXIT_CODE=$?
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Testes concluídos com exit code: ${EXIT_CODE}"
echo ""
echo "📁 Relatórios disponíveis:"
echo "   • Saída: ${REPORT_FILE}"
echo "   • Log: ${LOG_FILE}"
echo "   • Cobertura JSON: data/test_reports/coverage_${TIMESTAMP}.json"
echo "   • Cobertura HTML: data/test_reports/htmlcov_${TIMESTAMP}/index.html"
echo "════════════════════════════════════════════════════════════════"

exit ${EXIT_CODE}

