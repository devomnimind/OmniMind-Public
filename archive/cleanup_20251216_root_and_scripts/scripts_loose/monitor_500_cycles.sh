#!/bin/bash
# Monitor 500-Ciclos em Tempo Real
# Use em terminal separado durante execução

set -e

MONITOR_DIR="data/monitor/executions"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

get_latest_execution() {
    ls -td "${MONITOR_DIR}"/*/ 2>/dev/null | head -1
}

print_header() {
    clear
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ 🧠 OmniMind 500-Ciclos - Monitor em Tempo Real               ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
}

while true; do
    print_header

    LATEST=$(get_latest_execution)

    if [ -z "$LATEST" ]; then
        echo -e "${YELLOW}⏳ Aguardando primeira execução...${NC}"
        sleep 2
        continue
    fi

    EXEC_NAME=$(basename "$LATEST")
    CYCLE_COUNT=$(ls -1 "${LATEST}"[0-9]*.json 2>/dev/null | wc -l)

    echo -e "${GREEN}✅ Execução: ${EXEC_NAME}${NC}"
    echo -e "${GREEN}📊 Ciclos completados: ${CYCLE_COUNT}/500${NC}"

    # Ler último ciclo para PHI
    if [ $CYCLE_COUNT -gt 0 ]; then
        LAST_CYCLE="${LATEST}${CYCLE_COUNT}.json"
        if [ -f "$LAST_CYCLE" ]; then
            PHI=$(python3 -c "import json; print(json.load(open('$LAST_CYCLE')).get('phi', 0))" 2>/dev/null || echo "?")
            DURATION=$(python3 -c "import json; print(int(json.load(open('$LAST_CYCLE')).get('duration_ms', 0)))" 2>/dev/null || echo "?")

            echo -e "${BLUE}📈 PHI: ${PHI}${NC}"
            echo -e "${BLUE}⏱️  Duração último ciclo: ${DURATION}ms${NC}"
        fi
    fi

    # Progresso
    PERCENT=$((CYCLE_COUNT * 100 / 500))
    FILLED=$((PERCENT / 5))
    EMPTY=$((20 - FILLED))

    echo -ne "${GREEN}Progresso: ["
    for ((i=0; i<FILLED; i++)); do echo -n "▓"; done
    for ((i=0; i<EMPTY; i++)); do echo -n "░"; done
    echo -e "] ${PERCENT}%${NC}"

    # Estimativa
    if [ $CYCLE_COUNT -gt 0 ]; then
        if [ -f "${LATEST}/summary.json" ]; then
            DURATION_TOTAL=$(python3 -c "import json; print(int(json.load(open('${LATEST}/summary.json')).get('duration_seconds', 0)))" 2>/dev/null || echo "?")
            CYCLES_LEFT=$((500 - CYCLE_COUNT))
            AVG_PER_CYCLE=$((DURATION_TOTAL / CYCLE_COUNT))
            ETA=$((CYCLES_LEFT * AVG_PER_CYCLE))

            echo -e "${BLUE}⏱️  Tempo atual: ${DURATION_TOTAL}s${NC}"
            echo -e "${BLUE}📊 Média/ciclo: ${AVG_PER_CYCLE}s${NC}"
            echo -e "${BLUE}⏳ ETA: ~${ETA}s ($((ETA/60))min)${NC}"
        fi
    fi

    # CPU/Memória (se disponível)
    if command -v nvidia-smi &> /dev/null; then
        echo ""
        echo -e "${YELLOW}🎮 GPU Status:${NC}"
        nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits | while IFS=',' read -r mem_used mem_total gpu_util temp; do
            echo "   Memória: ${mem_used}MB / ${mem_total}MB"
            echo "   Utilização: ${gpu_util}%"
            echo "   Temperatura: ${temp}°C"
        done
    fi

    echo ""
    echo -e "${YELLOW}🔄 Atualizando em 5 segundos (Press Ctrl+C para sair)...${NC}"
    sleep 5
done
