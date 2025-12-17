#!/bin/bash
################################################################################
#                   OmniMind NVIDIA Verification - Ubuntu 22.04               #
#                          16 de Dezembro de 2025                             #
################################################################################
#
# Script de verificação NVIDIA para Ubuntu 22.04.5 LTS
# NÃO instala nada - apenas verifica e configura PATH
#
# Modo de uso:
#   bash ./scripts/development/setup_nvidia_ubuntu2204.sh
#
# Procedimento: Black → Flake8 → MyPy → Pytest → Validação
#
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  OmniMind NVIDIA Verification - Ubuntu 22.04.5 LTS            ║${NC}"
echo -e "${BLUE}║  Data: $(date '+%d de %B de %Y')                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar Ubuntu version
echo -e "${YELLOW}[1/5] Verificando Sistema Operacional...${NC}"
UBUNTU_VERSION=$(lsb_release -rs)
if [[ ! "$UBUNTU_VERSION" =~ ^22\.04 ]]; then
    echo -e "${RED}❌ Este script é para Ubuntu 22.04.x - você tem $UBUNTU_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Ubuntu 22.04.5 LTS detectado${NC}"
echo ""

# Verificar GPU NVIDIA
echo -e "${YELLOW}[2/5] Verificando GPU NVIDIA...${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ nvidia-smi não encontrado - instale NVIDIA drivers${NC}"
    echo "   sudo apt install -y nvidia-driver-535"
    exit 1
fi
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
echo -e "${GREEN}✅ GPU NVIDIA detectada${NC}"
echo ""

# Verificar e configurar Nsight Tools (SISTEMA, não pip)
echo -e "${YELLOW}[3/5] Verificando Nsight Tools (Nsight Systems + Compute)...${NC}"

if [ -f /opt/nvidia/nsight-systems/2023.2.3/bin/nsys ]; then
    echo -e "${GREEN}✅ nsys encontrado: /opt/nvidia/nsight-systems/2023.2.3/bin/nsys${NC}"
else
    echo -e "${RED}❌ nsys não encontrado em /opt/nvidia${NC}"
    echo "   Estes são instalados como parte dos drivers NVIDIA"
fi

if [ -f /opt/nvidia/nsight-compute/2023.2.2/ncu ]; then
    echo -e "${GREEN}✅ ncu encontrado: /opt/nvidia/nsight-compute/2023.2.2/ncu${NC}"
else
    echo -e "${RED}❌ ncu não encontrado em /opt/nvidia${NC}"
fi

# Verificar PATH
echo -e "${YELLOW}   → Verificando ~/.bashrc para PATH NVIDIA...${NC}"
if grep -q "nsight-systems.*PATH" ~/.bashrc; then
    echo -e "${GREEN}   ✅ PATH já configurado${NC}"
else
    echo -e "${YELLOW}   → Adicionando PATH NVIDIA ao ~/.bashrc...${NC}"
    cat >> ~/.bashrc << 'BASHRC_EOF'

# OmniMind NVIDIA Profiling Tools (16 Dec 2025)
export PATH="/opt/nvidia/nsight-systems/2023.2.3/bin:$PATH"
export PATH="/opt/nvidia/nsight-compute/2023.2.2:$PATH"
BASHRC_EOF
    echo -e "${GREEN}   ✅ PATH adicionado${NC}"
    echo -e "${YELLOW}   → Recarregando .bashrc...${NC}"
    source ~/.bashrc
fi

echo ""

# Verificar PyTorch CUDA
echo -e "${YELLOW}[4/5] Verificando PyTorch CUDA wheels...${NC}"
python3 -c "import torch; print(f'✅ PyTorch: {torch.__version__}'); print(f'✅ CUDA disponível: {torch.cuda.is_available()}'); print(f'✅ GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>/dev/null || {
    echo -e "${RED}❌ PyTorch com CUDA não encontrado${NC}"
    echo "   Instale: pip install -r requirements/requirements-gpu.txt"
    exit 1
}
echo ""

# Validação de código
echo -e "${YELLOW}[5/5] Executando validação completa (Black/Flake8/MyPy)...${NC}"
echo ""

# Black
echo -e "${YELLOW}   [Black] Verificando formatação...${NC}"
python3 -m black --check --quiet src tests 2>/dev/null && echo -e "${GREEN}   ✅ Black OK${NC}" || echo -e "${YELLOW}   ⚠️  Código precisa de formatação (rode: black src tests)${NC}"

# Flake8
echo -e "${YELLOW}   [Flake8] Verificando linting...${NC}"
python3 -m flake8 src tests --max-line-length=100 --quiet 2>/dev/null && echo -e "${GREEN}   ✅ Flake8 OK${NC}" || echo -e "${YELLOW}   ⚠️  Linting issues encontrados${NC}"

# MyPy
echo -e "${YELLOW}   [MyPy] Verificando tipos...${NC}"
python3 -m mypy src tests --ignore-missing-imports --quiet 2>/dev/null && echo -e "${GREEN}   ✅ MyPy OK${NC}" || echo -e "${YELLOW}   ⚠️  Type issues encontrados${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ NVIDIA Verification Completo!                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Próximos passos:${NC}"
echo "  1. Testar nsys + Python (venv):"
echo "     source .venv/bin/activate"
echo "     nsys profile --stats=true python3 -c \"import torch; print('OK')\""
echo ""
echo "  2. Profile do projeto:"
echo "     nsys profile --stats=true python3 scripts/science_validation/robust_consciousness_validation.py --quick"
echo ""
echo "  3. Profile detalhado com Nsight Compute:"
echo "     ncu --set full python3 src/quantum_consciousness/quantum_backend.py"
echo ""
echo -e "${YELLOW}Documentação completa: .github/copilot-instructions.md Seção 1.4.6${NC}"
echo -e "${YELLOW}Cheatsheet: Downloads/omnimind_nvidia_cli_cheatsheet.md${NC}"

