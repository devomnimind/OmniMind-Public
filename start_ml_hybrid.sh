#!/bin/bash
# Inicialização rápida do ambiente ML Híbrido

echo "🚀 Iniciando ML Híbrido..."

# Verifica limites
echo "📊 Verificando limites..."
python ml_cli_tool.py limits

# Inicia monitor em background
echo "🔍 Iniciando monitor..."
python ml_monitor.py &
MONITOR_PID=$!

echo "✅ Ambiente pronto! PID do monitor: $MONITOR_PID"
echo ""
echo "💡 Comandos disponíveis:"
echo "  python ml_cli_tool.py --help"
echo "  python hybrid_ml_optimizer.py"
echo ""
echo "🛑 Para parar: kill $MONITOR_PID"

# Mantém terminal aberto
wait $MONITOR_PID
