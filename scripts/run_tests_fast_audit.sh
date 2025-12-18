#!/bin/bash

# ============================================================================
# 🔍 OMNIMIND FAST TEST SUITE - MODO AUDITORIA
# ============================================================================
# Versão otimizada para auditoria com:
# - Verbosidade reduzida (apenas erros, falhas, warnings)
# - Logs focados em problemas (FAILED, ERROR, WARNING)
# - Saída limpa para análise rápida
# - Captura detalhada de erros críticos
#
# 🎯 USO: Auditoria rápida, análise de problemas, CI/CD
# ⏳ DURAÇÃO: ~15-20 min (mesma do modo normal)
# ============================================================================

set -e

cd /home/fahbrain/projects/omnimind

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="data/test_reports"
mkdir -p "$LOG_DIR"

# Arquivos de saída (modo auditoria)
ERRORS_LOG="$LOG_DIR/errors_audit_${TIMESTAMP}.log"
FAILURES_LOG="$LOG_DIR/failures_audit_${TIMESTAMP}.log"
WARNINGS_LOG="$LOG_DIR/warnings_audit_${TIMESTAMP}.log"
SUMMARY_LOG="$LOG_DIR/summary_audit_${TIMESTAMP}.log"
CONSOLIDATED_AUDIT="$LOG_DIR/audit_consolidated_${TIMESTAMP}.log"

echo "🔍 OMNIMIND FAST TEST SUITE - MODO AUDITORIA"
echo "=============================================="
echo "⏱️  Timestamp: $TIMESTAMP"
echo "🛡️  Modo: Auditoria (Apenas Erros/Falhas/Warnings)"
echo "🚀 GPU: FORÇADA (com fallback)"
echo "📈 Coverage: ATIVADO (JSON, HTML, XML)"
echo "🐛 Debug: REDUZIDO (apenas problemas)"
echo "=============================================="
echo ""

# Validação pré-teste (silenciosa)
if ! python scripts/pre_test_validation.py > /dev/null 2>&1; then
    echo "❌ VALIDAÇÃO PRÉ-TESTE FALHOU"
    echo "🚫 TESTES NÃO SERÃO EXECUTADOS"
    exit 1
fi

# Executa pytest com foco em erros
# CRITICAL:
# - --tb=short: Traceback curto (mais limpo)
# - --log-cli-level=WARNING: Apenas warnings e acima (reduz verbosidade)
# - --quiet: Menos output no console
# - --no-header: Remove header do pytest
# - Captura apenas erros/falhas via grep
CUDA_VISIBLE_DEVICES=0 \
OMNIMIND_GPU=true \
OMNIMIND_FORCE_GPU=true \
OMNIMIND_DEV=true \
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
pytest tests/ \
  -m "not chaos" \
  --tb=short \
  --quiet \
  --no-header \
  --log-cli-level=WARNING \
  --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s" \
  --log-cli-date-format="%Y-%m-%d %H:%M:%S" \
  --log-file="$LOG_DIR/pytest_audit_${TIMESTAMP}.log" \
  --log-file-level=WARNING \
  --junit-xml="$LOG_DIR/junit_audit_${TIMESTAMP}.xml" \
  --cov=src \
  --cov-report=json:"$LOG_DIR/coverage_audit_${TIMESTAMP}.json" \
  --cov-report=html:"$LOG_DIR/coverage_audit_${TIMESTAMP}_html" \
  --cov-report=xml:"$LOG_DIR/coverage_audit_${TIMESTAMP}.xml" \
  --cov-report=term-missing \
  --durations=10 \
  2>&1 | tee "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" | \
  grep -E "(FAILED|ERROR|WARNING|FAILURE|AssertionError|Exception|Traceback|insufficient|Insufficient|CUDA out of memory|Connection refused|timeout|Timeout|Meta.*cogn|metacognition|entropy.*exceeds)" || true

EXIT_CODE=${PIPESTATUS[0]}

# Extrair apenas erros, falhas e warnings dos logs
echo ""
echo "📊 Extraindo erros, falhas e warnings..."
echo ""

# Extrair FAILED tests
grep -E "FAILED|FAILURE" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" > "$FAILURES_LOG" 2>/dev/null || touch "$FAILURES_LOG"

# Extrair ERROR tests
grep -E "ERROR|Exception|Traceback" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" > "$ERRORS_LOG" 2>/dev/null || touch "$ERRORS_LOG"

# Extrair WARNINGS
grep -E "WARNING|Warning" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" > "$WARNINGS_LOG" 2>/dev/null || touch "$WARNINGS_LOG"

# Criar resumo consolidado para auditoria
{
    echo "=========================================="
    echo "OMNIMIND AUDIT REPORT - RESUMO CONSOLIDADO"
    echo "=========================================="
    echo "Timestamp: $TIMESTAMP"
    echo "Exit Code: $EXIT_CODE"
    echo ""

    # Contar ocorrências
    FAILED_COUNT=$(wc -l < "$FAILURES_LOG" 2>/dev/null || echo "0")
    ERROR_COUNT=$(wc -l < "$ERRORS_LOG" 2>/dev/null || echo "0")
    WARNING_COUNT=$(wc -l < "$WARNINGS_LOG" 2>/dev/null || echo "0")

    echo "=========================================="
    echo "ESTATÍSTICAS"
    echo "=========================================="
    echo "❌ Falhas (FAILED): $FAILED_COUNT"
    echo "🔴 Erros (ERROR): $ERROR_COUNT"
    echo "⚠️  Avisos (WARNING): $WARNING_COUNT"
    echo ""

    # Padrões críticos
    echo "=========================================="
    echo "PADRÕES CRÍTICOS DETECTADOS"
    echo "=========================================="

    # Insufficient history
    INSUFFICIENT_HISTORY=$(grep -i "insufficient.*history\|history.*insufficient" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" 2>/dev/null | wc -l || echo "0")
    if [ "$INSUFFICIENT_HISTORY" -gt 0 ]; then
        echo "⚠️  Insufficient History: $INSUFFICIENT_HISTORY ocorrências"
        echo "   (Dados insuficientes para cálculos completos)"
    fi

    # CUDA OOM
    CUDA_OOM=$(grep -i "CUDA out of memory" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" 2>/dev/null | wc -l || echo "0")
    if [ "$CUDA_OOM" -gt 0 ]; then
        echo "🔴 CUDA OOM: $CUDA_OOM ocorrências"
    fi

    # Meta cognition failures
    METACOGNITION=$(grep -i "meta.*cogn.*failed\|metacognition.*failed" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" 2>/dev/null | wc -l || echo "0")
    if [ "$METACOGNITION" -gt 0 ]; then
        echo "🔴 Meta Cognition Failures: $METACOGNITION ocorrências"
    fi

    # Entropy warnings
    ENTROPY=$(grep -i "entropy.*exceeds\|entropy.*warning" "$LOG_DIR/pytest_output_audit_${TIMESTAMP}.log" 2>/dev/null | wc -l || echo "0")
    if [ "$ENTROPY" -gt 0 ]; then
        echo "⚠️  Entropy Warnings: $ENTROPY ocorrências"
    fi

    echo ""

    # Falhas detalhadas
    if [ "$FAILED_COUNT" -gt 0 ]; then
        echo "=========================================="
        echo "FALHAS DETALHADAS (FAILED)"
        echo "=========================================="
        head -50 "$FAILURES_LOG"
        if [ "$FAILED_COUNT" -gt 50 ]; then
            echo "... (mais $((FAILED_COUNT - 50)) linhas em $FAILURES_LOG)"
        fi
        echo ""
    fi

    # Erros detalhados
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "=========================================="
        echo "ERROS DETALHADOS (ERROR)"
        echo "=========================================="
        head -50 "$ERRORS_LOG"
        if [ "$ERROR_COUNT" -gt 50 ]; then
            echo "... (mais $((ERROR_COUNT - 50)) linhas em $ERRORS_LOG)"
        fi
        echo ""
    fi

    # Warnings críticos (apenas os mais importantes)
    if [ "$WARNING_COUNT" -gt 0 ]; then
        echo "=========================================="
        echo "WARNINGS CRÍTICOS (amostra)"
        echo "=========================================="
        grep -E "insufficient|Insufficient|CUDA|entropy|meta.*cogn" "$WARNINGS_LOG" 2>/dev/null | head -30 || echo "Nenhum warning crítico encontrado"
        echo ""
    fi

} > "$CONSOLIDATED_AUDIT"

# Exibir resumo no console
echo "=========================================="
echo "✅ AUDITORIA FINALIZADA"
echo "=========================================="
echo "📋 Relatórios salvos em: $LOG_DIR"
echo ""
echo "📄 Arquivos Gerados:"
echo "   ❌ failures_audit_${TIMESTAMP}.log ($FAILED_COUNT falhas)"
echo "   🔴 errors_audit_${TIMESTAMP}.log ($ERROR_COUNT erros)"
echo "   ⚠️  warnings_audit_${TIMESTAMP}.log ($WARNING_COUNT avisos)"
echo "   📊 audit_consolidated_${TIMESTAMP}.log (resumo completo)"
echo "   📈 coverage_audit_${TIMESTAMP}.json (coverage)"
echo "   📋 junit_audit_${TIMESTAMP}.xml (CI/CD)"
echo ""
echo "💡 Análise rápida:"
echo "   • Ver resumo: cat $CONSOLIDATED_AUDIT"
echo "   • Ver falhas: cat $FAILURES_LOG"
echo "   • Ver erros: cat $ERRORS_LOG"
echo "   • Ver warnings: cat $WARNINGS_LOG"
echo ""

exit $EXIT_CODE

