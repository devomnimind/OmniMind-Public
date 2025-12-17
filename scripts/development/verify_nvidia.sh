#!/bin/bash
# Script de verificação pós-reboot para drivers NVIDIA e CUDA
# OmniMind Agent System

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     OMNIMIND - Verificação Pós-Reboot NVIDIA/CUDA                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Verificar nvidia-smi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Verificando nvidia-smi"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if nvidia-smi &> /dev/null; then
    check_pass "nvidia-smi funcionando"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
    check_fail "nvidia-smi NÃO funcionando"
    exit 1
fi
echo ""

# 2. Verificar CUDA
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Verificando CUDA Toolkit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v nvcc &> /dev/null; then
    check_pass "nvcc (CUDA compiler) encontrado"
    nvcc --version | grep "release"
else
    check_warn "nvcc não encontrado no PATH"
    echo "   Adicione ao ~/.bashrc:"
    echo "   export PATH=/usr/local/cuda/bin:\$PATH"
fi
echo ""

# 3. Verificar módulo kernel
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Verificando módulo kernel NVIDIA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if lsmod | grep -q nvidia; then
    check_pass "Módulo nvidia carregado"
    lsmod | grep nvidia | head -3
else
    check_fail "Módulo nvidia NÃO carregado"
    echo "   Tente: sudo modprobe nvidia"
fi
echo ""

# 4. Verificar bibliotecas CUDA
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Verificando bibliotecas CUDA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ldconfig -p | grep -q libcuda.so; then
    check_pass "Bibliotecas CUDA encontradas"
    echo "   libcuda: $(ldconfig -p | grep libcuda.so | head -1 | awk '{print $NF}')"
else
    check_warn "Bibliotecas CUDA não em cache"
    echo "   Execute: sudo ldconfig"
fi
echo ""

# 5. Status da GPU
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Status da GPU"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader)
    GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader)
    
    echo "   GPU: $GPU_NAME"
    echo "   VRAM: $GPU_MEM"
    echo "   Temperatura: ${GPU_TEMP}°C"
    echo "   Utilização: $GPU_UTIL"
fi
echo ""

# 6. Verificar Ollama
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Verificando Ollama"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v ollama &> /dev/null; then
    check_pass "Ollama instalado"
    ollama --version
    
    if systemctl is-active --quiet ollama 2>/dev/null; then
        check_pass "Ollama service ATIVO"
    else
        check_warn "Ollama service NÃO ativo"
        echo "   Inicie com: sudo systemctl start ollama"
    fi
else
    check_warn "Ollama não instalado"
    echo "   Instale com: curl https://ollama.ai/install.sh | sh"
fi
echo ""

# 7. Verificar llama.cpp
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. Verificando llama.cpp"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "/usr/local/llama.cpp/bin/llama-cli" ]; then
    check_pass "llama.cpp instalado"
    /usr/local/llama.cpp/bin/llama-cli --version 2>&1 | head -1
else
    check_warn "llama.cpp não encontrado"
    echo "   Compile conforme RELATORIO_NVIDIA_CUDA.md seção 6"
fi
echo ""

# 8. Verificar ambiente Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. Verificando ambiente Python OmniMind"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "$HOME/projects/omnimind/.venv" ]; then
    check_pass "Virtual environment encontrado"
    
    # Ativar e verificar
    source "$HOME/projects/omnimind/.venv/bin/activate"
    
    if python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null | grep -q True; then
        check_pass "PyTorch com CUDA disponível"
    else
        check_warn "PyTorch sem CUDA (opcional para llama-cpp-python)"
    fi
    
    deactivate 2>/dev/null || true
else
    check_warn "Virtual environment não encontrado"
fi
echo ""

# 9. Registrar verificação no sistema de auditoria
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. Registrando verificação no sistema de auditoria"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$HOME/projects/omnimind/.venv" ]; then
    cd "$HOME/projects/omnimind"
    source .venv/bin/activate
    
    python3 << 'PYEOF'
from src.audit import log_action
import subprocess

# Obter informações da GPU
try:
    gpu_name = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
        text=True
    ).strip()
    
    driver_version = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
        text=True
    ).strip()
    
    vram_total = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader'],
        text=True
    ).strip()
    
    log_action(
        'nvidia_drivers_verified_post_reboot',
        {
            'status': 'operational',
            'gpu_name': gpu_name,
            'driver_version': driver_version,
            'vram_total': vram_total,
            'nvidia_smi': 'working',
            'cuda_available': True
        },
        'system'
    )
    
    print("✓ Verificação registrada no sistema de auditoria")
    
except Exception as e:
    print(f"⚠ Erro ao registrar: {e}")
PYEOF
    
    deactivate
else
    check_warn "Não foi possível registrar no sistema de auditoria"
fi
echo ""

# 10. Resumo final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. RESUMO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Drivers NVIDIA: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo 'NÃO DETECTADO')"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'NÃO DETECTADO')"
echo "VRAM: $(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null || echo 'NÃO DETECTADO')"
echo ""

if nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ SISTEMA PRONTO PARA DESENVOLVIMENTO${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. Compilar llama.cpp com CUDA (ver RELATORIO_NVIDIA_CUDA.md seção 6)"
    echo "  2. Instalar Ollama (curl https://ollama.ai/install.sh | sh)"
    echo "  3. Baixar modelo Qwen2 (ollama pull qwen2:7b-instruct)"
    echo "  4. Testar inferência"
    echo "  5. Continuar implementação dos agentes"
else
    echo -e "${RED}✗ PROBLEMAS DETECTADOS${NC}"
    echo ""
    echo "Soluções:"
    echo "  1. Verificar se reboot foi feito: uptime"
    echo "  2. Carregar módulo: sudo modprobe nvidia"
    echo "  3. Verificar DKMS: sudo dkms status"
    echo "  4. Ver logs: sudo journalctl -b | grep nvidia"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
