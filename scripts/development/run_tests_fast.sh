#!/bin/bash

# ============================================================================
# ⚡ OMNIMIND FAST TEST SUITE
# ============================================================================
# Executa suite rápida para validação de código (DIÁRIA):
# - GPU FORÇADA (com fallback device_count detection)
# - Logs detalhados e timestamped com DEBUG verboso
# - Coverage completo com relatórios JSON, HTML e XML
# - Métricas JSON de execução (via MetricsCollector)
# - Exportação completa de todos os dados
# - Pula testes lentos/chaos/destrutivos
# - Foco em lógica, mocks e integridade
#
# 🚫 EXCLUÍDOS:
#   - Testes @pytest.mark.chaos (destroem servidor - WEEKLY ONLY)
#
# ✅ INCLUÍDOS:
#   - Testes @pytest.mark.slow (cálculos, estatísticas, GPU - DEVEM rodar no modo rápido)
#   - Testes @pytest.mark.real SEM @pytest.mark.chaos (GPU+LLM+Network, não destroem servidor)
#
# ⏳ DURAÇÃO: ~15-20 min
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

# Arquivos de saída
OUTPUT_LOG="$LOG_DIR/output_fast_${TIMESTAMP}.log"
PYTEST_LOG="$LOG_DIR/pytest_fast_${TIMESTAMP}.log"
JUNIT_XML="$LOG_DIR/junit_fast_${TIMESTAMP}.xml"
HTML_REPORT="$LOG_DIR/report_fast_${TIMESTAMP}.html"
COVERAGE_JSON="$LOG_DIR/coverage_fast_${TIMESTAMP}.json"
COVERAGE_HTML="$LOG_DIR/coverage_fast_${TIMESTAMP}_html"
COVERAGE_XML="$LOG_DIR/coverage_fast_${TIMESTAMP}.xml"
METRICS_JSON="$LOG_DIR/metrics_report_fast_${TIMESTAMP}.json"
CONSOLIDATED_OUTPUT="$LOG_DIR/consolidated_fast_${TIMESTAMP}.log"

echo "⚡ OMNIMIND FAST TEST SUITE"
echo "======================================"
echo "⏱️  Timestamp: $TIMESTAMP"
echo "🛡️  Modo: Rápido (Sem Chaos, COM Slow - GPU/Cálculos)"
echo "🚀 GPU: FORÇADA (com fallback)"
echo "📈 Coverage: ATIVADO (JSON, HTML, XML)"
echo "🐛 Debug: VERBOSO (DEBUG level)"
echo "📋 Exportação: COMPLETA (todos os dados)"
echo "======================================"
echo ""

# Contar testes dinamicamente (SEM PRÉ-VALIDAÇÃO - REMOVER BLOQUEIO)
echo "📊 Contando testes disponíveis..."
EXPECTED_TESTS=$(pytest --collect-only -q tests/ -m "not chaos" 2>/dev/null | tail -1 || echo "calculando...")
if [ "$EXPECTED_TESTS" != "calculando..." ] && [ -n "$EXPECTED_TESTS" ]; then
    echo "📊 Testes encontrados: $EXPECTED_TESTS"
else
    echo "📊 Testes: calculando durante execução..."
fi
echo ""

# Verificar GPU status ANTES dos testes (OTIMIZADO)
echo "🔍 Verificando GPU/CUDA status..."
python3 << 'GPUCHECK'
import torch
print(f"  ✅ torch.cuda.is_available(): {torch.cuda.is_available()}")
print(f"  ✅ torch.cuda.device_count(): {torch.cuda.device_count()}")
if torch.cuda.device_count() > 0:
    try:
        print(f"  ✅ torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")
    except:
        print(f"  ⚠️  Device detectado mas nome indisponível")
print("")
GPUCHECK

# Executa pytest com GPU FORÇADA, logs verbosos, coverage e métricas
# CRITICAL: CUDA_VISIBLE_DEVICES=0 força dispositivo 0
# OMNIMIND_FORCE_GPU=true força detecção com device_count fallback
# --cov: Ativa coverage
# --cov-report: Gera relatórios em múltiplos formatos
# --log-cli-level=DEBUG: Logs verbosos no console
# --log-cli-format: Formato detalhado dos logs
# -vv: Verbose máximo
# -s: Não captura output (mostra prints)
# --tb=long: Traceback longo para debug
# --cache-clear: Remove cache pytest (fix permissions sudo)
CUDA_VISIBLE_DEVICES=0 \
OMNIMIND_GPU=true \
OMNIMIND_FORCE_GPU=true \
OMNIMIND_DEV=true \
OMNIMIND_DEBUG=true \
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
python3 -m pytest tests/ \
  -vv \
  --tb=long \
  -m "not chaos" \
  --cache-clear \
  --log-cli-level=DEBUG \
  --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s" \
  --log-cli-date-format="%Y-%m-%d %H:%M:%S" \
  --log-file="$PYTEST_LOG" \
  --log-file-level=DEBUG \
  --junit-xml="$JUNIT_XML" \
  --html="$HTML_REPORT" \
  --self-contained-html \
  --cov=src \
  --cov-report=json:"$COVERAGE_JSON" \
  --cov-report=html:"$COVERAGE_HTML" \
  --cov-report=xml:"$COVERAGE_XML" \
  --cov-report=term-missing \
  --durations=10 \
  -s \
  2>&1 | tee "$OUTPUT_LOG"

EXIT_CODE=$?

# Aguardar um momento para garantir que todos os arquivos foram escritos
sleep 2

# Consolidar métricas JSON se existir (gerado pelo MetricsCollector)
if [ -f "data/test_reports/metrics_report.json" ]; then
    echo ""
    echo "📊 Copiando métricas JSON com timestamp..."
    cp "data/test_reports/metrics_report.json" "$METRICS_JSON"
    echo "   ✅ Métricas salvas em: $METRICS_JSON"
fi

# Criar arquivo consolidado com todos os dados
echo ""
echo "📦 Consolidando todos os dados em arquivo único..."
{
    echo "=========================================="
    echo "OMNIMIND FAST TEST SUITE - RELATÓRIO CONSOLIDADO"
    echo "=========================================="
    echo "Timestamp: $TIMESTAMP"
    echo "Exit Code: $EXIT_CODE"
    echo ""
    echo "=========================================="
    echo "1. OUTPUT COMPLETO (stdout/stderr)"
    echo "=========================================="
    cat "$OUTPUT_LOG"
    echo ""
    echo "=========================================="
    echo "2. PYTEST LOGS (DEBUG VERBOSO)"
    echo "=========================================="
    if [ -f "$PYTEST_LOG" ]; then
        cat "$PYTEST_LOG"
    else
        echo "⚠️  Arquivo de log pytest não encontrado"
    fi
    echo ""
    echo "=========================================="
    echo "3. MÉTRICAS DE EXECUÇÃO (JSON)"
    echo "=========================================="
    if [ -f "$METRICS_JSON" ]; then
        cat "$METRICS_JSON"
    else
        echo "⚠️  Arquivo de métricas não encontrado"
    fi
    echo ""
    echo "=========================================="
    echo "4. COVERAGE SUMMARY (JSON)"
    echo "=========================================="
    if [ -f "$COVERAGE_JSON" ]; then
        cat "$COVERAGE_JSON"
    else
        echo "⚠️  Arquivo de coverage JSON não encontrado"
    fi
    echo ""
    echo "=========================================="
    echo "5. JUNIT XML (CI/CD) - Primeiras 50 linhas"
    echo "=========================================="
    if [ -f "$JUNIT_XML" ]; then
        head -50 "$JUNIT_XML"
        echo "... (arquivo completo em: $JUNIT_XML)"
    else
        echo "⚠️  Arquivo JUnit XML não encontrado"
    fi
} > "$CONSOLIDATED_OUTPUT"

echo "   ✅ Arquivo consolidado salvo em: $CONSOLIDATED_OUTPUT"

echo ""
echo "======================================"
echo "✅ TESTES RÁPIDOS FINALIZADOS"
echo "======================================"
echo "📋 Logs e Relatórios salvos em: $LOG_DIR"
echo ""
echo "📄 Arquivos Gerados:"
echo "   📝 output_fast_${TIMESTAMP}.log (stdout/stderr completo)"
echo "   🐛 pytest_fast_${TIMESTAMP}.log (pytest logs DEBUG verboso)"
echo "   📊 metrics_report_fast_${TIMESTAMP}.json (métricas de execução JSON)"
echo "   📈 coverage_fast_${TIMESTAMP}.json (coverage JSON)"
echo "   📈 coverage_fast_${TIMESTAMP}_html/ (coverage HTML - abra index.html)"
echo "   📈 coverage_fast_${TIMESTAMP}.xml (coverage XML)"
echo "   📋 junit_fast_${TIMESTAMP}.xml (CI/CD report)"
echo "   🌐 report_fast_${TIMESTAMP}.html (dashboard HTML)"
echo "   📦 consolidated_fast_${TIMESTAMP}.log (TUDO consolidado)"
echo ""
echo "💡 Dicas:"
echo "   • Ver métricas: cat $METRICS_JSON | jq"
echo "   • Ver coverage: cat $COVERAGE_JSON | jq"
echo "   • Ver tudo: less $CONSOLIDATED_OUTPUT"
echo "   • Abrir coverage HTML: xdg-open $COVERAGE_HTML/index.html"
echo ""

exit $EXIT_CODE
