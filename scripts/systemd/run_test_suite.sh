#!/bin/bash
# OmniMind Test Suite Runner via Systemd
# Executa toda a suite de testes Python com cobertura completa

cd /home/fahbrain/projects/omnimind

# Ativar ambiente virtual
source .venv/bin/activate

# Executar suite completa com todas as opções
python -m pytest \
    --tb=short \
    --verbose \
    --cov=src \
    --cov-report=html \
    --cov-report=xml \
    --cov-report=term-missing \
    --durations=10 \
    --maxfail=5 \
    --strict-markers \
    --disable-warnings \
    --log-cli-level=INFO \
    --log-cli-format="%(asctime)s [%(levelname)s] %(name)s: %(message)s" \
    --log-cli-date-format="%Y-%m-%d %H:%M:%S" \
    --junitxml=test_results_systemd.xml \
    tests/

# Capturar resultado
exit_code=$?

# Gerar relatório de cobertura adicional se necessário
if [ $exit_code -eq 0 ]; then
    echo "✅ Suite de testes executada com sucesso"
    echo "📊 Relatórios gerados:"
    echo "  - HTML: htmlcov/index.html"
    echo "  - XML: coverage.xml"
    echo "  - JUnit: test_results_systemd.xml"
else
    echo "❌ Suite de testes falhou com código $exit_code"
fi

exit $exit_code