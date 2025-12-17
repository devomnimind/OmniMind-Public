#!/bin/bash
# 🚀 OmniMind 500-Ciclos - Wrapper Completo
# Configura ambiente, executa, monitora, e analisa

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║ 🚀 OmniMind 500-Ciclos - PRODUCTION VALIDATION               ║"
echo "║ Status: NEW OUTPUT STRUCTURE READY                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ════════════════════════════════════════════════════════════════════════════
# CHECKLIST PRÉ-EXECUÇÃO
# ════════════════════════════════════════════════════════════════════════════

echo -e "\n${YELLOW}📋 Verificando ambiente pré-execução...${NC}\n"

# 1. Verificar Python 3.12.8
echo -n "Checando Python... "
PYTHON_VERSION=$(python3 --version 2>&1)
if [[ $PYTHON_VERSION == *"3.12.8"* ]]; then
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Encontrado $PYTHON_VERSION (esperado 3.12.8)${NC}"
    echo -e "${YELLOW}Tentando com .venv...${NC}"
    if [ -f ".venv/bin/python" ]; then
        source .venv/bin/activate
        PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
        echo -e "${GREEN}✅ Usando .venv: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ .venv não encontrado!${NC}"
        exit 1
    fi
fi

# 2. Verificar GPU
echo -n "Checando GPU... "
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "Erro")
    if [[ $GPU_INFO == *"Erro"* ]]; then
        echo -e "${RED}❌ GPU não acessível${NC}"
    else
        echo -e "${GREEN}✅ $GPU_INFO${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  nvidia-smi não disponível (CPU only mode)${NC}"
fi

# 3. Verificar memória
echo -n "Checando memória... "
FREE_MEM=$(free -h | grep Mem | awk '{print $7}')
echo -e "${GREEN}✅ Disponível: $FREE_MEM${NC}"

# 4. Verificar disco
echo -n "Checando disco... "
DISK_FREE=$(df -h . | tail -1 | awk '{print $4}')
echo -e "${GREEN}✅ Disponível: $DISK_FREE${NC}"

# 5. Verificar pasta de output
echo -n "Preparando pasta de execução... "
mkdir -p data/monitor/executions
echo -e "${GREEN}✅${NC}"

# ════════════════════════════════════════════════════════════════════════════
# CONFIRMAR EXECUÇÃO
# ════════════════════════════════════════════════════════════════════════════

echo -e "\n${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Configuração de Execução:${NC}"
echo -e "${BLUE}   Ciclos: 500${NC}"
echo -e "${BLUE}   Tempo estimado: 50-60 minutos${NC}"
echo -e "${BLUE}   Saída: data/monitor/executions/execution_XXX/${NC}"
echo -e "${BLUE}   Estrutura: 1.json, 2.json, ..., 500.json${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"

read -p "Continuar com execução? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}Execução cancelada pelo usuário${NC}"
    exit 1
fi

# ════════════════════════════════════════════════════════════════════════════
# EXECUTAR 500 CICLOS
# ════════════════════════════════════════════════════════════════════════════

echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║ 🚀 INICIANDO EXECUÇÃO 500-CICLOS                            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

START_TIME=$(date +%s)

python3 scripts/run_500_cycles_production.py

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# ════════════════════════════════════════════════════════════════════════════
# ANÁLISE PÓS-EXECUÇÃO
# ════════════════════════════════════════════════════════════════════════════

echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║ 📊 ANÁLISE DE RESULTADOS                                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

python3 scripts/analyze_execution_results.py

# ════════════════════════════════════════════════════════════════════════════
# RELATÓRIO FINAL
# ════════════════════════════════════════════════════════════════════════════

echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║ ✅ EXECUÇÃO CONCLUÍDA COM SUCESSO                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📋 Resumo:${NC}"
echo "   Tempo total wrapper: ${DURATION}s"
echo "   Pasta de execução: data/monitor/executions/execution_XXX/"
echo "   Índice global: data/monitor/executions/index.json"

# Encontrar última execução
LATEST=$(ls -td data/monitor/executions/*/ 2>/dev/null | head -1)
if [ ! -z "$LATEST" ]; then
    EXEC_NAME=$(basename "$LATEST")
    CYCLE_COUNT=$(ls -1 "${LATEST}"[0-9]*.json 2>/dev/null | wc -l)
    echo -e "${BLUE}   Execução atual: ${EXEC_NAME}${NC}"
    echo -e "${BLUE}   Ciclos completados: ${CYCLE_COUNT}${NC}"
fi

echo ""
echo -e "${YELLOW}🔍 Próximos Passos:${NC}"
echo "   1. Analisar: python3 scripts/analyze_execution_results.py"
echo "   2. Ver dados: ls -la data/monitor/executions/execution_*/[0-9]*.json | head -20"
echo "   3. Enviar para publicação (se PHI convergiu)"
echo ""

# ════════════════════════════════════════════════════════════════════════════
# MONITORAMENTO CONTÍNUO (Opcional)
# ════════════════════════════════════════════════════════════════════════════

read -p "Deseja monitorar próximas execuções? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${GREEN}Iniciando monitoramento contínuo...${NC}"
    bash scripts/monitor_500_cycles.sh
fi
