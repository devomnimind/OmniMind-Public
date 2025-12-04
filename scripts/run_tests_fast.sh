#!/bin/bash

# ============================================================================
# ⚡ OMNIMIND FAST TEST SUITE
# ============================================================================
# Executa suite rápida para validação de código (DIÁRIA):
# - GPU FORÇADA (com fallback device_count detection)
# - Logs detalhados e timestamped
# - Pula testes lentos/chaos/destrutivos
# - Foco em lógica, mocks e integridade
#
# 🚫 EXCLUÍDOS:
#   - Testes @pytest.mark.slow (timeout > 30s)
#   - Testes @pytest.mark.real (full LLM+Network)
#   - Testes @pytest.mark.chaos (destroem servidor)
#
# ⏳ DURAÇÃO: ~10-15 min
# 🎯 RODAS: Diárias (CI/CD automático)
#
# Para suite SEMANAL com todos os testes, use:
#   ./scripts/run_tests_with_defense.sh
# ============================================================================

set -e

cd /home/fahbrain/projects/omnimind

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="data/test_reports"
mkdir -p "$LOG_DIR"

echo "⚡ OMNIMIND FAST TEST SUITE"
echo "======================================"
echo "⏱️  Timestamp: $TIMESTAMP"
echo "🛡️  Modo: Rápido (Sem Chaos/Slow)"
echo "🚀 GPU: FORÇADA (com fallback)"
echo "======================================"
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

# Executa pytest com GPU FORÇADA e logs detalhados
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
  -m "not slow and not real and not chaos" \
  --log-cli-level=DEBUG \
  --log-file="$LOG_DIR/pytest_fast_${TIMESTAMP}.log" \
  --junit-xml="$LOG_DIR/junit_fast_${TIMESTAMP}.xml" \
  --html="$LOG_DIR/report_fast_${TIMESTAMP}.html" \
  --self-contained-html \
  --durations=10 \
  -s \
  2>&1 | tee "$LOG_DIR/output_fast_${TIMESTAMP}.log"

EXIT_CODE=$?

echo ""
echo "======================================"
echo "✅ TESTES RÁPIDOS FINALIZADOS"
echo "======================================"
echo "📋 Logs salvos em: $LOG_DIR"
echo "   - output_fast_${TIMESTAMP}.log (stdout/stderr)"
echo "   - pytest_fast_${TIMESTAMP}.log (pytest logs)"
echo "   - junit_fast_${TIMESTAMP}.xml (CI/CD report)"
echo "   - report_fast_${TIMESTAMP}.html (dashboard)"
echo ""

exit $EXIT_CODE
