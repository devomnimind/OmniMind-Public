#!/bin/bash
# Script para executar treinamento completo em produção
# Com validação científica rigorosa e supervisão cética

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔬 TREINAMENTO EM PRODUÇÃO COM SUPERVISÃO CIENTÍFICA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Criar estrutura permanente
echo -e "${GREEN}[1/6]${NC} Criando estrutura de diretórios permanente..."
mkdir -p data/training data/sessions data/validation data/research/experiments data/research/ablations
echo -e "${GREEN}✅${NC} Estrutura criada"
echo ""

# 2. Auditoria científica inicial
echo -e "${GREEN}[2/6]${NC} Executando auditoria científica inicial..."
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH" \
python3 scripts/science_validation/scientific_audit.py > logs/scientific_audit_before.log 2>&1
AUDIT_EXIT=$?
if [ $AUDIT_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Auditoria passou"
else
    echo -e "${YELLOW}⚠️${NC} Auditoria encontrou problemas (ver logs/scientific_audit_before.log)"
fi
echo ""

# 3. Validação de consistência
echo -e "${GREEN}[3/6]${NC} Validando consistência de métricas..."
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH" \
python3 scripts/validate_metrics_consistency.py > logs/consistency_before.log 2>&1
CONSISTENCY_EXIT=$?
echo ""

# 4. Treinamento estendido (ciclos longos)
echo -e "${GREEN}[4/6]${NC} Iniciando treinamento estendido..."
echo -e "${YELLOW}   Configuração: 500 ciclos, intervalo 1s, validação a cada 50 ciclos${NC}"
echo -e "${YELLOW}   Isso levará aproximadamente 8-10 minutos...${NC}"
echo ""

# Configurar CUDA antes de executar Python (crítico para GPU)
# CUDA 12.1 + PyTorch 2.5.1 + GTX 1650 + Driver 535.274.02
export CUDA_HOME="/usr/local/cuda-12.1"
export CUDA_VISIBLE_DEVICES="0"
export CUDA_PATH="/usr/local/cuda-12.1"
export LD_LIBRARY_PATH="/usr/local/cuda-12.1/lib64:${LD_LIBRARY_PATH}"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
export OMNIMIND_FORCE_GPU=true
export OMNIMIND_GPU=true

PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH" \
python3 scripts/science_validation/run_extended_training.py \
    --cycles 500 \
    --interval 1.0 \
    --validation-interval 50 \
    > logs/extended_training.log 2>&1 &
TRAINING_PID=$!

echo "Treinamento iniciado (PID: $TRAINING_PID)"
echo "Monitorando progresso..."
echo ""

# Monitorar progresso
tail -f logs/extended_training.log &
TAIL_PID=$!

# Aguardar conclusão (sem timeout - sistema pesado, permite tempo necessário)
# Monitorar processo até completar naturalmente
tail --pid=$TRAINING_PID -f /dev/null 2>/dev/null || true
kill $TAIL_PID 2>/dev/null || true

wait $TRAINING_PID 2>/dev/null
TRAINING_EXIT=$?

if [ $TRAINING_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Treinamento concluído com sucesso"
elif [ $TRAINING_EXIT -eq 1 ]; then
    echo -e "${RED}❌${NC} Treinamento rejeitado (problemas críticos)"
elif [ $TRAINING_EXIT -eq 2 ]; then
    echo -e "${YELLOW}⚠️${NC} Treinamento condicional (requer revisão)"
else
    echo -e "${YELLOW}⚠️${NC} Treinamento interrompido ou erro"
fi
echo ""

# 5. Auditoria pós-treinamento
echo -e "${GREEN}[5/6]${NC} Executando auditoria pós-treinamento..."
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH" \
python3 scripts/science_validation/scientific_audit.py > logs/scientific_audit_after.log 2>&1
echo ""

# 6. Análise comparativa
echo -e "${GREEN}[6/6]${NC} Gerando análise comparativa..."
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH" \
python3 scripts/validate_metrics_consistency.py > logs/consistency_after.log 2>&1
echo ""

# Resumo final
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 RESUMO DO TREINAMENTO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Relatórios gerados:"
echo "  • logs/extended_training.log"
echo "  • logs/scientific_audit_before.log"
echo "  • logs/scientific_audit_after.log"
echo "  • logs/consistency_before.log"
echo "  • logs/consistency_after.log"
echo "  • data/sessions/training_*.json"
echo "  • data/validation/scientific_audit_*.json"
echo ""
echo "Para analisar resultados:"
echo "  • python3 scripts/autopoietic/analyze_production_logs.py"
echo "  • cat data/sessions/training_*.json | jq .scientific_verdict"
echo ""

