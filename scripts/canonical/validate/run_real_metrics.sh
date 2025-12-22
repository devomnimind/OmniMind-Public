#!/bin/bash
# RODAR MÉTRICAS REAIS DO SISTEMA
# Este script executa testes REAIS (sem @patch) e coleta números
# Resultado: dados honestos para o paper, sejam quais forem

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "🚀 COLETA DE MÉTRICAS REAIS - OmniMind"
echo "======================================================================"
echo ""
echo "⚠️  AVISO IMPORTANTE:"
echo "   - Este script executa testes REAIS (sem @patch)"
echo "   - Pode levar 30+ minutos"
echo "   - Valores são reportados EXATAMENTE como medidos"
echo "   - NÃO há ajuste ou falsificação de números"
echo ""

# Ativa venv
source .venv/bin/activate

# Cria diretório de relatórios
mkdir -p data/test_reports

echo "======================================================================"
echo "📊 ETAPA 1: Coleta de Métricas com Python"
echo "======================================================================"
echo ""

python3 scripts/utilities/analysis/collect_real_metrics.py 2>&1 | tee data/test_reports/real_metrics_run.log

echo ""
echo "======================================================================"
echo "✅ COLETA COMPLETA"
echo "======================================================================"
echo ""
echo "Arquivos gerados:"
ls -lh data/test_reports/real_metrics_* 2>/dev/null || echo "  (nenhum arquivo ainda)"
echo ""

echo "Para ver os resultados:"
echo "  cat data/test_reports/real_metrics_*_summary.txt"
echo "  jq . data/test_reports/real_metrics_*.json"
echo ""
