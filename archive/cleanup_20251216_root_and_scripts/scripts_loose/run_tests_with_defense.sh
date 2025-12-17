#!/bin/bash

# ============================================================================
# 🧠 RUN TESTS WITH OMNIMIND AUTODEFENSE
# ============================================================================
# Executa suite COMPLETA COM TESTES DESTRUTIVOS (SEMANAL):
# - GPU ativada
# - Dev mode
# - Debug ativo
# - Timeouts adaptativos (220-800s)
# - OmniMind TestDefense ativado (detecta testes perigosos)
# - Logs profundos em arquivos com timestamp
#
# 📋 INCLUÍDOS:
#   ✅ Testes normais (unit, integration)
#   ✅ Testes @pytest.mark.slow (timeout > 30s)
#   ✅ Testes @pytest.mark.real (full LLM+Network)
#   ✅ Testes @pytest.mark.chaos (destroem servidor - CHAOS ENGINEERING)
#
# ⏳ DURAÇÃO: ~45-90 min (com chaos engineering)
# 🎯 RODAS: Semanais (validação completa)
#
# Para suite RÁPIDA (diária) sem chaos, use:
#   ./scripts/run_tests_fast.sh
# ============================================================================

set -e

cd /home/fahbrain/projects/omnimind

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="data/test_reports"
mkdir -p "$LOG_DIR"

echo "🧪 OMNIMIND TEST SUITE COM AUTODEFESA"
echo "======================================"
echo "⏱️  Timestamp: $TIMESTAMP"
echo "📊 Testes esperados: ~3952"
echo "🛡️  Modo: Autodefesa ativada"
echo "🚀 GPU: FORÇADA (com fallback)"
echo "======================================"
echo ""

# Validação pré-teste: verificar meta cognition health
echo "🔍 Validando saúde do sistema antes de executar testes..."
if ! python scripts/pre_test_validation.py; then
    echo ""
    echo "❌ VALIDAÇÃO PRÉ-TESTE FALHOU"
    echo "🚫 TESTES NÃO SERÃO EXECUTADOS"
    echo ""
    echo "Por favor, resolva os problemas de meta cognição antes de continuar."
    exit 1
fi
echo "✅ Validação pré-teste passou"
echo ""

# Verificar GPU status ANTES dos testes
echo "🔍 Verificando GPU status..."
python3 << 'GPUCHECK'
import torch
print(f"  torch.cuda.is_available(): {torch.cuda.is_available()}")
print(f"  torch.cuda.device_count(): {torch.cuda.device_count()}")
if torch.cuda.device_count() > 0:
    try:
        print(f"  torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")
    except:
        print(f"  Device detected but name unavailable")
print("")
GPUCHECK

# Comando completo com GPU FORÇADA + Dev + Debug
# CRITICAL: CUDA_VISIBLE_DEVICES=0 força dispositivo 0
# OMNIMIND_FORCE_GPU=true força detecção com device_count fallback
CUDA_VISIBLE_DEVICES=0 \
OMNIMIND_GPU=true \
OMNIMIND_FORCE_GPU=true \
OMNIMIND_DEV=true \
OMNIMIND_DEBUG=true \
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512 \
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

EXIT_CODE=$?

echo ""
echo "======================================"
echo "✅ TESTES FINALIZADOS"
echo "======================================"
echo "📋 Logs salvos em: $LOG_DIR"
echo "   - output_${TIMESTAMP}.log (stdout/stderr)"
echo "   - pytest_${TIMESTAMP}.log (pytest logs)"
echo "   - junit_${TIMESTAMP}.xml (CI/CD report)"
echo "   - report_${TIMESTAMP}.html (dashboard)"
echo ""
echo "🛡️  Verificar AUTODEFESA no final do output para testes perigosos"
echo "======================================"

exit $EXIT_CODE
