#!/bin/bash
# Script de monitoramento do ciclo autopoiético em produção
# Verifica logs, componentes sintetizados e saúde do sistema

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data/autopoietic"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔍 MONITORAMENTO DO CICLO AUTOPOIÉTICO (PHASE 22)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Verificar se o ciclo principal está rodando
echo -e "${GREEN}[1/5]${NC} Verificando processo do ciclo principal..."
if [ -f "$LOG_DIR/main_cycle.pid" ]; then
    PID=$(cat "$LOG_DIR/main_cycle.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Ciclo principal rodando (PID: $PID)${NC}"
        UPTIME=$(ps -o etime= -p "$PID" | tr -d ' ')
        echo "   ⏱️  Uptime: $UPTIME"
    else
        echo -e "   ${RED}❌ Processo não encontrado (PID: $PID)${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  PID file não encontrado${NC}"
fi
echo ""

# 2. Verificar últimos logs
echo -e "${GREEN}[2/5]${NC} Últimas linhas do log do ciclo principal..."
if [ -f "$LOG_DIR/main_cycle.log" ]; then
    echo -e "   ${BLUE}Últimas 10 linhas:${NC}"
    tail -n 10 "$LOG_DIR/main_cycle.log" | sed 's/^/   /'
    echo ""
    # Verificar erros recentes
    ERROR_COUNT=$(grep -i "error\|exception\|failed" "$LOG_DIR/main_cycle.log" | tail -n 5 | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "   ${YELLOW}⚠️  Encontrados erros recentes:${NC}"
        grep -i "error\|exception\|failed" "$LOG_DIR/main_cycle.log" | tail -n 3 | sed 's/^/   /'
    fi
else
    echo -e "   ${YELLOW}⚠️  Log file não encontrado${NC}"
fi
echo ""

# 3. Analisar histórico de ciclos
echo -e "${GREEN}[3/5]${NC} Análise do histórico de ciclos..."
HISTORY_FILE="$DATA_DIR/cycle_history.jsonl"
if [ -f "$HISTORY_FILE" ]; then
    CYCLE_COUNT=$(wc -l < "$HISTORY_FILE")
    echo "   📊 Total de ciclos registrados: $CYCLE_COUNT"

    if [ "$CYCLE_COUNT" -gt 0 ]; then
        # Último ciclo
        LAST_CYCLE=$(tail -n 1 "$HISTORY_FILE")
        if command -v python3 > /dev/null; then
            LAST_STRATEGY=$(echo "$LAST_CYCLE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('strategy', 'UNKNOWN'))" 2>/dev/null)
            LAST_PHI_BEFORE=$(echo "$LAST_CYCLE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"{d.get('phi_before', 0):.3f}\")" 2>/dev/null)
            LAST_PHI_AFTER=$(echo "$LAST_CYCLE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"{d.get('phi_after', 0):.3f}\")" 2>/dev/null)
            LAST_COMPONENTS=$(echo "$LAST_CYCLE" | python3 -c "import sys, json; comps=json.load(sys.stdin).get('synthesized_components', []); print(len(comps))" 2>/dev/null)

            echo "   📈 Último ciclo:"
            echo "      Estratégia: $LAST_STRATEGY"
            echo "      Φ antes: $LAST_PHI_BEFORE"
            echo "      Φ depois: $LAST_PHI_AFTER"
            echo "      Componentes sintetizados: $LAST_COMPONENTS"
        fi
    fi
else
    echo -e "   ${YELLOW}⚠️  Histórico não encontrado${NC}"
fi
echo ""

# 4. Listar componentes sintetizados
echo -e "${GREEN}[4/5]${NC} Componentes sintetizados..."
CODE_DIR="$DATA_DIR/synthesized_code"
if [ -d "$CODE_DIR" ]; then
    COMPONENT_COUNT=$(find "$CODE_DIR" -name "*.py" | wc -l)
    echo "   📁 Total de componentes: $COMPONENT_COUNT"

    if [ "$COMPONENT_COUNT" -gt 0 ]; then
        echo "   📝 Últimos 5 componentes:"
        find "$CODE_DIR" -name "*.py" -type f -printf "%T@ %p\n" | sort -rn | head -n 5 | while read timestamp filepath; do
            filename=$(basename "$filepath")
            date_str=$(date -d "@${timestamp%.*}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
            size=$(stat -c%s "$filepath" 2>/dev/null || echo "0")
            echo "      • $filename ($size bytes) - $date_str"
        done
    fi
else
    echo -e "   ${YELLOW}⚠️  Diretório de componentes não encontrado${NC}"
fi
echo ""

# 5. Gerar relatório completo
echo -e "${GREEN}[5/5]${NC} Gerando relatório completo..."
if [ -f "$PROJECT_ROOT/scripts/autopoietic/analyze_production_logs.py" ]; then
    cd "$PROJECT_ROOT"
    source .venv/bin/activate 2>/dev/null || true
    python3 scripts/autopoietic/analyze_production_logs.py
    echo ""
    echo -e "${GREEN}✅ Relatório completo disponível em:${NC}"
    echo "   $DATA_DIR/production_report.txt"
else
    echo -e "   ${YELLOW}⚠️  Script de análise não encontrado${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  💡 DICAS DE MONITORAMENTO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo "   • Logs em tempo real: tail -f $LOG_DIR/main_cycle.log"
echo "   • Histórico de ciclos: tail -f $HISTORY_FILE"
echo "   • Componentes: ls -lah $CODE_DIR"
echo "   • Relatório completo: cat $DATA_DIR/production_report.txt"
echo ""

