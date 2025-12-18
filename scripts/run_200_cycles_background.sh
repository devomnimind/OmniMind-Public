#!/bin/bash
# Script para executar 200 ciclos em background

cd /home/fahbrain/projects/omnimind

# Ativar venv
source .venv/bin/activate

# Arquivos de saída
LOG_FILE="data/monitor/phi_200_cycles.log"
PID_FILE="data/monitor/phi_200_cycles.pid"

# Criar diretório se não existir
mkdir -p data/monitor

# Verificar se já está rodando
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  Processo já está rodando (PID: $OLD_PID)"
        echo "   Para parar: kill $OLD_PID"
        exit 1
    else
        echo "🧹 Removendo PID file antigo..."
        rm "$PID_FILE"
    fi
fi

# Executar em background
echo "🚀 Iniciando execução de 200 ciclos em background..."
echo "📝 Log: $LOG_FILE"
echo "📊 Progresso: data/monitor/phi_200_cycles_progress.json"
echo "📈 Métricas: data/monitor/phi_200_cycles_metrics.json"
echo ""

nohup python scripts/run_200_cycles_production.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# Salvar PID
echo $NEW_PID > "$PID_FILE"

echo "✅ Processo iniciado (PID: $NEW_PID)"
echo ""
echo "📋 Comandos úteis:"
echo "   Ver progresso: cat data/monitor/phi_200_cycles_progress.json | jq"
echo "   Ver log: tail -f $LOG_FILE"
echo "   Parar: kill $NEW_PID"
echo "   Status: ps -p $NEW_PID"

