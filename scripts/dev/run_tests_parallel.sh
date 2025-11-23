#!/bin/bash
# Script para execução otimizada de testes com paralelização
# Suporte a diferentes modos: rápido, completo, cobertura, etc.

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detectar número de CPUs disponíveis
CPU_COUNT=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "4")
echo -e "${BLUE}🔍 CPUs detectadas: $CPU_COUNT${NC}"

# Função para executar testes
run_tests() {
    local mode="$1"
    local workers="$2"
    local extra_args="$3"

    echo -e "${YELLOW}🧪 Executando testes em modo: $mode${NC}"
    echo -e "${YELLOW}👥 Workers: $workers${NC}"

    case "$mode" in
        "fast")
            # Modo rápido: testes básicos sem cobertura
            pytest tests/ \
                -n "$workers" \
                --dist worksteal \
                -x \
                --tb=short \
                --disable-warnings \
                --maxfail=3 \
                $extra_args
            ;;
        "full")
            # Modo completo: com cobertura
            pytest tests/ \
                -n "$workers" \
                --dist worksteal \
                -v \
                --tb=short \
                --cov=src \
                --cov-report=term-missing \
                --cov-report=html:htmlcov \
                --cov-fail-under=80 \
                $extra_args
            ;;
        "coverage")
            # Modo cobertura detalhada
            pytest tests/ \
                -n "$workers" \
                --dist worksteal \
                --cov=src \
                --cov-report=term-missing \
                --cov-report=html:htmlcov \
                --cov-report=xml \
                --cov-fail-under=85 \
                $extra_args
            ;;
        "serial")
            # Modo serial: para testes que não podem ser paralelizados
            pytest tests/ \
                -v \
                --tb=short \
                -m "serial or not parallel" \
                $extra_args
            ;;
        "smoke")
            # Modo smoke: testes críticos apenas
            pytest tests/ \
                -n "$workers" \
                --dist worksteal \
                -k "test_critical or test_security or test_core" \
                --tb=short \
                $extra_args
            ;;
        *)
            echo -e "${RED}❌ Modo desconhecido: $mode${NC}"
            echo -e "${YELLOW}📋 Modos disponíveis: fast, full, coverage, serial, smoke${NC}"
            exit 1
            ;;
    esac
}

# Função para mostrar ajuda
show_help() {
    echo -e "${BLUE}🚀 Script de Testes Paralelos OmniMind${NC}"
    echo ""
    echo "Uso: $0 [modo] [opções]"
    echo ""
    echo "Modos:"
    echo "  fast      - Testes rápidos sem cobertura (padrão)"
    echo "  full      - Testes completos com cobertura"
    echo "  coverage  - Cobertura detalhada"
    echo "  serial    - Testes que devem rodar em série"
    echo "  smoke     - Apenas testes críticos"
    echo ""
    echo "Opções:"
    echo "  -w, --workers NUM  - Número de workers (auto-detectado por padrão)"
    echo "  -m, --marker MARK  - Executar apenas testes com marcador específico"
    echo "  -k, --keyword KEY  - Filtrar testes por palavra-chave"
    echo "  -h, --help         - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 fast              # Testes rápidos com auto workers"
    echo "  $0 full -w 8         # Testes completos com 8 workers"
    echo "  $0 coverage -m slow  # Cobertura apenas de testes lentos"
    echo "  $0 -k security       # Apenas testes de segurança"
}

# Valores padrão
MODE="fast"
WORKERS="auto"
EXTRA_ARGS=""

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -m|--marker)
            EXTRA_ARGS="$EXTRA_ARGS -m $2"
            shift 2
            ;;
        -k|--keyword)
            EXTRA_ARGS="$EXTRA_ARGS -k $2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        fast|full|coverage|serial|smoke)
            MODE="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Opção desconhecida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Configurar workers
if [ "$WORKERS" = "auto" ]; then
    # Usar número de CPUs como base, mas limitar para evitar sobrecarga
    if [ "$CPU_COUNT" -gt 8 ]; then
        WORKERS=8
    else
        WORKERS=$CPU_COUNT
    fi
fi

# Timestamp de início
START_TIME=$(date +%s)
echo -e "${GREEN}▶️  Iniciando testes em $(date)${NC}"
echo -e "${GREEN}📊 Modo: $MODE | Workers: $WORKERS${NC}"

# Executar testes
if run_tests "$MODE" "$WORKERS" "$EXTRA_ARGS"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo -e "${GREEN}✅ Testes concluídos com sucesso em ${DURATION}s${NC}"

    # Estatísticas adicionais para modo coverage
    if [ "$MODE" = "coverage" ] && [ -f "htmlcov/index.html" ]; then
        echo -e "${BLUE}📊 Relatório de cobertura gerado: htmlcov/index.html${NC}"
        echo -e "${BLUE}🌐 Abrir relatório: python -m http.server 8000 -d htmlcov${NC}"
    fi
else
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo -e "${RED}❌ Testes falharam após ${DURATION}s${NC}"
    exit 1
fi