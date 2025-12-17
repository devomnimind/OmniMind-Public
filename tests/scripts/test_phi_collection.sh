#!/bin/bash
# Teste rápido de coleta de Φ com múltiplos testes

set -e

cd /home/fahbrain/projects/omnimind

echo "🚀 Teste de Coleta de Φ (Phi) com GPU"
echo "========================================"
echo ""

# Configuração
export CUDA_VISIBLE_DEVICES=0
export TORCH_HOME=/home/fahbrain/.cache/torch
export PYTHONUNBUFFERED=1

# Criar diretório
mkdir -p data/test_reports

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="data/test_reports/phi_test_${TIMESTAMP}.log"
PHI_FILE="data/test_reports/phi_metrics_${TIMESTAMP}.json"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 Iniciando coleta de Φ..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log: $LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Φ Métricas: $PHI_FILE"
echo ""

# Rodar testes de medição de Φ com coleta
python -m pytest tests/consciousness/test_production_consciousness.py::TestMeasurePhi -v -s \
    --tb=short 2>&1 | python scripts/phi_metrics_collector.py | tee "$LOG_FILE"

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Testes finalizados"
echo ""

# Visualizar resultados
if [ -f "$PHI_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 Analisando métricas de Φ..."
    echo ""
    python scripts/phi_analysis_dashboard.py "$PHI_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Arquivo de métricas não encontrado"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Concluído!"
