#!/bin/bash
# OmniMind Test Suite Runner via Systemd
# Executa toda a suite de testes Python com cobertura completa
# Coleta: coverage, junit XML, warnings, erros, benchmarks

set -euo pipefail

cd /home/fahbrain/projects/omnimind

# Criar diretórios de saída
mkdir -p data/test_results
mkdir -p data/benchmarks
mkdir -p logs

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/test_suite_${TIMESTAMP}.log"
COVERAGE_XML="data/test_results/coverage_${TIMESTAMP}.xml"
JUNIT_XML="data/test_results/junit_${TIMESTAMP}.xml"
COVERAGE_JSON="data/test_results/coverage_${TIMESTAMP}.json"

# Ativar ambiente virtual
source .venv/bin/activate

echo "=========================================="
echo "OmniMind Test Suite - Systemd Execution"
echo "Timestamp: ${TIMESTAMP}"
echo "=========================================="
echo ""

# Executar suite completa com todas as opções e coleta completa
python -m pytest \
    --tb=short \
    --verbose \
    --cov=src \
    --cov-report=html:htmlcov \
    --cov-report=xml:${COVERAGE_XML} \
    --cov-report=json:${COVERAGE_JSON} \
    --cov-report=term-missing \
    --durations=20 \
    --maxfail=100 \
    --strict-markers \
    -rA \
    --log-cli-level=INFO \
    --log-cli-format="%(asctime)s [%(levelname)s] %(name)s: %(message)s" \
    --log-cli-date-format="%Y-%m-%d %H:%M:%S" \
    --junitxml=${JUNIT_XML} \
    tests/ 2>&1 | tee ${LOG_FILE}

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=========================================="
echo "Test Execution Summary"
echo "=========================================="
echo "Exit Code: ${EXIT_CODE}"
echo "Log File: ${LOG_FILE}"
echo "Coverage XML: ${COVERAGE_XML}"
echo "Coverage JSON: ${COVERAGE_JSON}"
echo "JUnit XML: ${JUNIT_XML}"
echo ""

# Extrair estatísticas do log
if [ -f ${LOG_FILE} ]; then
    echo "--- Test Statistics ---"
    grep -E "(passed|failed|skipped|warnings|error)" ${LOG_FILE} | tail -1 || echo "Statistics not found"
    echo ""
    
    echo "--- Coverage Summary ---"
    grep -A 5 "TOTAL" ${LOG_FILE} | head -10 || echo "Coverage summary not found"
    echo ""
    
    echo "--- Failed Tests ---"
    grep -E "FAILED|ERROR" ${LOG_FILE} | head -30 || echo "No failures found"
    echo ""
    
    echo "--- Warnings ---"
    grep -i "warning" ${LOG_FILE} | head -30 || echo "No warnings found"
    echo ""
fi

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "✅ Suite de testes executada com sucesso"
    echo "📊 Relatórios gerados:"
    echo "  - Log: ${LOG_FILE}"
    echo "  - HTML: htmlcov/index.html"
    echo "  - Coverage XML: ${COVERAGE_XML}"
    echo "  - Coverage JSON: ${COVERAGE_JSON}"
    echo "  - JUnit XML: ${JUNIT_XML}"
else
    echo "❌ Suite de testes falhou com código ${EXIT_CODE}"
    echo "📊 Relatórios gerados:"
    echo "  - Log: ${LOG_FILE}"
    echo "  - Coverage XML: ${COVERAGE_XML}"
    echo "  - Coverage JSON: ${COVERAGE_JSON}"
    echo "  - JUnit XML: ${JUNIT_XML}"
fi

exit ${EXIT_CODE}
