#!/bin/bash
# 🚀 SCRIPT PARA RODAR SUITE COM TIMEOUTS ADAPTATIVOS

set -e

cd /home/fahbrain/projects/omnimind

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ 🎯 SUITE DE TESTES - TIMEOUTS ADAPTATIVOS + LACAN VALIDATION  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Configuração:"
echo "  - Modo: TEST (OMNIMIND_MODE=test)"
echo "  - Timeouts: 90s → 120s → 180s → 240s (progressivo)"
echo "  - SecurityAgent: ATIVO (testes reais)"
echo "  - Métricas: Coletadas (Φ, consciência, duração)"
echo "  - Objetivo: Diagnosticar falhas REAIS vs timeout artificial"
echo ""
echo "⏱️  Tempo esperado:"
echo "  - Primeiro startup: 40-50 segundos"
echo "  - Recuperação pos-crash: 30-45 segundos"
echo "  - Suite completa: Variável (depende dos testes)"
echo ""

# Garante que servidor antigo está parado
echo "🔄 Limpando servidores antigos..."
pkill -9 -f "uvicorn|python.*web.backend" 2>/dev/null || true
sleep 2

# Executa suite
echo "🚀 Iniciando suite..."
echo ""

export OMNIMIND_MODE=test
export QDRANT_URL=http://localhost:6333
export PYTHONUNBUFFERED=1

# Opção 1: Full suite (comentar se quiser rodar subconjunto)
# python -m pytest tests/ -v --tb=short 2>&1 | tee test_suite_run.log

# Opção 2: Apenas testes de integração (mais rápido para testes)
python -m pytest tests/integrations/ -v --tb=short -x 2>&1 | tee test_suite_run.log

# Opção 3: Apenas chaos tests (para validar timeouts)
# python -m pytest tests/test_chaos_resilience.py -v --tb=short 2>&1 | tee test_suite_run.log

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ ✅ Suite finalizada                                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📈 Relatório:"
if [ -f data/test_reports/metrics_report.json ]; then
  echo "  📊 Métricas coletadas:"
  python -m json.tool data/test_reports/metrics_report.json | head -20
fi

if [ -f test_suite_run.log ]; then
  echo ""
  echo "📝 Log completo salvo em: test_suite_run.log"
  echo ""
  echo "🔍 Resumo rápido:"
  echo "  - Testes passados:"
  grep -c "PASSED" test_suite_run.log || echo "    0"
  echo "  - Testes falhados:"
  grep -c "FAILED" test_suite_run.log || echo "    0"
  echo "  - Timeouts observados:"
  grep -c "Timeout" test_suite_run.log || echo "    0"
fi

