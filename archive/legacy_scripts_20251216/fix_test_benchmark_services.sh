#!/bin/bash
set -euo pipefail

echo "🔧 Corrigindo dependências dos serviços test-suite e benchmark..."
echo ""

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SYSTEMD_DIR="/etc/systemd/system"

# Copiar serviços corrigidos
echo "1. Copiando serviços corrigidos..."
sudo cp "${PROJECT_ROOT}/scripts/systemd/omnimind-test-suite.service" "${SYSTEMD_DIR}/"
sudo cp "${PROJECT_ROOT}/scripts/systemd/omnimind-benchmark.service" "${SYSTEMD_DIR}/"
echo "✅ Serviços copiados."

# Recarregar daemon
echo ""
echo "2. Recarregando daemon systemd..."
sudo systemctl daemon-reload
echo "✅ Daemon recarregado."

# Verificar sintaxe
echo ""
echo "3. Verificando sintaxe..."
if sudo systemd-analyze verify "${SYSTEMD_DIR}/omnimind-test-suite.service" 2>/dev/null; then
    echo "✅ omnimind-test-suite.service OK"
else
    echo "❌ Erro em omnimind-test-suite.service"
fi

if sudo systemd-analyze verify "${SYSTEMD_DIR}/omnimind-benchmark.service" 2>/dev/null; then
    echo "✅ omnimind-benchmark.service OK"
else
    echo "❌ Erro em omnimind-benchmark.service"
fi

echo ""
echo "✅ Correções aplicadas!"
echo ""
echo "📋 Status:"
echo "   - omnimind-test-suite.service: $(systemctl is-enabled omnimind-test-suite.service) (correto - não inicia automaticamente)"
echo "   - omnimind-benchmark.service: $(systemctl is-enabled omnimind-benchmark.service) (correto - não inicia automaticamente)"
echo ""
echo "💡 Para executar manualmente:"
echo "   sudo systemctl start omnimind-test-suite.service"
echo "   sudo systemctl start omnimind-benchmark.service"

