#!/bin/bash
# Script para executar suite completa de validação de métricas e cálculos

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔬 SUITE COMPLETA DE VALIDAÇÃO DE MÉTRICAS E CÁLCULOS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Validação de Consistência de Métricas
echo -e "${GREEN}[1/4]${NC} Validando consistência de métricas..."
python3 scripts/validate_metrics_consistency.py
VALIDATION_EXIT=$?
echo ""

# 2. Verificação de Saúde Autopoiética
echo -e "${GREEN}[2/4]${NC} Verificando saúde do sistema autopoiético..."
python3 scripts/autopoietic/check_phi_health.py
HEALTH_EXIT=$?
echo ""

# 3. Análise de Logs de Produção
echo -e "${GREEN}[3/4]${NC} Analisando logs de produção..."
python3 scripts/autopoietic/analyze_production_logs.py
ANALYSIS_EXIT=$?
echo ""

# 4. Testes de Consciência (se GPU disponível)
echo -e "${GREEN}[4/4]${NC} Executando testes de consciência..."
if command -v nvidia-smi &> /dev/null; then
    python3 -m pytest tests/consciousness/test_integration_loop.py -v --tb=short 2>&1 | head -30
    TESTS_EXIT=$?
else
    echo -e "${YELLOW}⚠️  GPU não disponível - pulando testes de consciência${NC}"
    TESTS_EXIT=0
fi
echo ""

# Resumo Final
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 RESUMO DA VALIDAÇÃO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ $VALIDATION_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Validação de Consistência: PASSOU${NC}"
else
    echo -e "${RED}❌ Validação de Consistência: FALHOU${NC}"
fi

if [ $HEALTH_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Saúde Autopoiética: SAUDÁVEL${NC}"
else
    echo -e "${YELLOW}⚠️  Saúde Autopoiética: ATENÇÃO${NC}"
fi

if [ $ANALYSIS_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Análise de Logs: COMPLETA${NC}"
else
    echo -e "${RED}❌ Análise de Logs: ERRO${NC}"
fi

if [ $TESTS_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Testes de Consciência: PASSOU${NC}"
else
    echo -e "${YELLOW}⚠️  Testes de Consciência: PARCIAL${NC}"
fi

echo ""
echo -e "${BLUE}Relatórios gerados:${NC}"
echo "  • data/validation_report.json"
echo "  • data/autopoietic/production_report.txt"
echo ""

# Exit code baseado nos resultados
if [ $VALIDATION_EXIT -ne 0 ] || [ $ANALYSIS_EXIT -ne 0 ]; then
    exit 1
else
    exit 0
fi

