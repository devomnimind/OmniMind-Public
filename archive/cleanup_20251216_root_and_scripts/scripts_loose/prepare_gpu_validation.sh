#!/bin/bash
# Script melhorado para detecção de GPU e limpeza de processos
# Antes de executar validação científica
# Atualizado: 12 Dezembro 2025

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}🔧 PRÉ-PROCESSAMENTO PARA VALIDAÇÃO GPU${NC}"
echo -e "${BLUE}===============================================${NC}"

# 1. DETECTAR GPU DISPONÍVEL
echo -e "\n${YELLOW}1️⃣  DETECÇÃO DE GPU${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ nvidia-smi não encontrado. GPU não disponível.${NC}"
    exit 1
fi

GPU_INFO=$(nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader,nounits)
while IFS=',' read -r gpu_id gpu_name gpu_memory driver; do
    gpu_id=$(echo "$gpu_id" | xargs)
    gpu_name=$(echo "$gpu_name" | xargs)
    gpu_memory=$(echo "$gpu_memory" | xargs)
    driver=$(echo "$driver" | xargs)
    echo -e "${GREEN}   ✅ GPU $gpu_id: $gpu_name (${gpu_memory}MB) - Driver: $driver${NC}"
done <<< "$GPU_INFO"

# 2. MATAR PROCESSOS QUE OCUPAM GPU DESNECESSARIAMENTE
echo -e "\n${YELLOW}2️⃣  LIMPEZA DE PROCESSOS GPU DESNECESSÁRIOS${NC}"

# Matar instâncias extras de uvicorn (deixar apenas 8000)
for port in 8080 3001 3000 5000; do
    pids=$(ss -tlnp 2>/dev/null | grep ":$port" | grep -oP 'pid=\K[0-9]+' || true)
    if [ -n "$pids" ]; then
        while read -r pid; do
            if [ -n "$pid" ]; then
                ps_output=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "")
                if echo "$ps_output" | grep -q "uvicorn\|backend"; then
                    echo -e "   🔪 Matando uvicorn:$port (PID: $pid)"
                    kill -9 "$pid" 2>/dev/null || true
                fi
            fi
        done <<< "$pids"
    fi
done

sleep 1
echo -e "   ${GREEN}✅ Limpeza concluída${NC}"

# 3. VERIFICAR MEMÓRIA DISPONÍVEL
echo -e "\n${YELLOW}3️⃣  VERIFICAÇÃO DE MEMÓRIA DISPONÍVEL${NC}"

# Memória GPU
gpu_free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
gpu_total=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
gpu_used=$((gpu_total - gpu_free))

echo -e "   📊 GPU: ${gpu_free}MB livre de ${gpu_total}MB (${gpu_used}MB em uso)"

if [ "$gpu_free" -lt 2000 ]; then
    echo -e "   ${RED}⚠️  AVISO: Menos de 2GB GPU livre! Considerando modo clássico (--disable-quantum)${NC}"
    QUANTUM_MODE="--disable-quantum"
elif [ "$gpu_free" -lt 3000 ]; then
    echo -e "   ${YELLOW}⚠️  AVISO: Entre 2-3GB GPU livre. Considerando modo leve (--quantum-lite)${NC}"
    QUANTUM_MODE="--quantum-lite"
else
    echo -e "   ${GREEN}✅ Suficiente GPU para modo quantum completo${NC}"
    QUANTUM_MODE=""
fi

# Memória RAM
mem_info=$(free -h | grep "^Mem:" | awk '{print $3, $2}')
echo -e "   📊 RAM: $mem_info"

# Swap
swap_info=$(free -h | grep "^Swap:" | awk '{print $3, $2}')
echo -e "   📊 Swap: $swap_info"

# 4. EXIBIR RECOMENDAÇÃO
echo -e "\n${YELLOW}4️⃣  RECOMENDAÇÕES${NC}"
echo -e "   Modo quantum recomendado: ${QUANTUM_MODE:-COMPLETO}"
echo -e "   Cores CPU: $(nproc)"
echo -e "   Load Average: $(uptime | awk -F'load average:' '{print $2}')"

# 5. EXECUTAR VALIDAÇÃO COM MODO APROPRIADO
echo -e "\n${BLUE}===============================================${NC}"
echo -e "${GREEN}🚀 INICIANDO VALIDAÇÃO CIENTÍFICA${NC}"
echo -e "${BLUE}===============================================${NC}\n"

# Exportar variáveis CUDA otimizadas para GTX 1650 (4GB)
export CUDA_VISIBLE_DEVICES="0"
export CUDA_LAUNCH_BLOCKING="1"
export PYTORCH_ALLOC_CONF="max_split_size_mb:32"  # Novo (não deprecated)
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:32"  # Legacy, mantido para compatibilidade
export OMP_NUM_THREADS="2"  # Reduzido de 4, libgomp ainda falha
export MKL_NUM_THREADS="1"

# Ativar venv se existir
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Executar script com modo apropriado
if [ -n "$QUANTUM_MODE" ]; then
    echo "Executando com modo: $QUANTUM_MODE"
    python "$PROJECT_ROOT/scripts/run_500_cycles_scientific_validation.py" $QUANTUM_MODE "$@"
else
    python "$PROJECT_ROOT/scripts/run_500_cycles_scientific_validation.py" "$@"
fi
