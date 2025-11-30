#!/bin/bash

# Script para monitorar testes em tempo real
# Uso: ./monitor_tests.sh [lines=50] [interval=5]

LINES="${1:-50}"
INTERVAL="${2:-5}"
LOG_FILE="data/test_reports/pytest_full.log"

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║             🧪 PYTEST MONITORAMENTO EM TEMPO REAL                         ║"
echo "║          Arquivo: $LOG_FILE                                   ║"
echo "║          Atualizando a cada ${INTERVAL}s (últimas ${LINES} linhas)                   ║"
echo "║          Ctrl+C para parar                                                ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

check_status() {
    if pgrep -f "pytest tests/" > /dev/null; then
        echo "✅ PYTEST EM EXECUÇÃO"
    else
        echo "❌ PYTEST FINALIZADO"
    fi
    
    if [ -f "$LOG_FILE" ]; then
        TOTAL_LINES=$(wc -l < "$LOG_FILE")
        echo "📝 Linhas no log: $TOTAL_LINES"
        
        # Contar resultados parciais
        if grep -q "passed\|failed\|error" "$LOG_FILE"; then
            PASSED=$(grep -c "PASSED" "$LOG_FILE" || echo "0")
            FAILED=$(grep -c "FAILED" "$LOG_FILE" || echo "0")
            echo "📊 Parcial: $PASSED passed, $FAILED failed"
        fi
    else
        echo "⚠️  Log não encontrado ainda"
    fi
    echo ""
}

while true; do
    clear
    check_status
    echo "────────────────────────────────────────────────────────────────────────"
    if [ -f "$LOG_FILE" ]; then
        tail -n "$LINES" "$LOG_FILE"
    fi
    echo "────────────────────────────────────────────────────────────────────────"
    echo "⏱️  Próxima atualização em ${INTERVAL}s... (Ctrl+C para parar)"
    sleep "$INTERVAL"
done
