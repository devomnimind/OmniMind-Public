#!/bin/bash

# Script para monitorar conclusão da suite de testes
# Uso: ./monitor_suite.sh

LOGFILE="data/test_reports/full_suite_20251201_094631.log"
PID=86970

echo "🔍 Monitorando suite de testes..."
echo "PID: $PID"
echo "Log: $LOGFILE"
echo ""

# Loop até processo terminar
while kill -0 $PID 2>/dev/null; do
    # Contar linhas no log
    LINES=$(wc -l < "$LOGFILE" 2>/dev/null || echo "0")
    
    # Estimativa de progresso (baseado em padrão de suite)
    PERCENT=$((LINES * 100 / 2500))  # Ajustar baseado em linhas esperadas
    
    # Contar testes completos mencionados no log
    TESTS=$(grep -c "test_" "$LOGFILE" 2>/dev/null || echo "0")
    
    # Status da memória (PT)
    MEM=$(ps aux | grep "python.*pytest" | grep -v grep | awk '{print $6}')
    
    echo -ne "\r⏳ Progresso: ~$PERCENT% | Linhas: $LINES | Testes: $TESTS | Mem: ${MEM}KB"
    
    sleep 5
done

echo ""
echo "✅ Suite finalizada!"
echo ""
echo "=== RESULTADO FINAL ==="
if grep -q "passed" "$LOGFILE"; then
    PASSED=$(grep -o "[0-9]* passed" "$LOGFILE" | tail -1)
    echo "✅ $PASSED"
fi
if grep -q "failed" "$LOGFILE"; then
    FAILED=$(grep -o "[0-9]* failed" "$LOGFILE" | tail -1)
    echo "❌ $FAILED"
fi
echo ""
echo "Mostrando últimas 30 linhas do log:"
tail -30 "$LOGFILE"
