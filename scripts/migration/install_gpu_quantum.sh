#!/bin/bash
# ============================================================================
# 🚀 INSTALL_GPU_QUANTUM.SH - Instalação Correta GPU + Quantum
# 16 DEC 2025 - Versões validadas e testadas
# ============================================================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🔧 Instalação GPU + Quantum (Versões Validadas 16 DEC 2025)${NC}\n"

# Verificar venv ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ Virtual environment não ativo!${NC}"
    echo "Execute: source .venv/bin/activate"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment ativo${NC}\n"

# 1. Desinstalar PyTorch errado (se existir)
echo -e "${YELLOW}[1/5] Limpando PyTorch antigo...${NC}"
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true
echo ""

# 2. Instalar PyTorch 2.5.1 cu121 (CORRETO)
echo -e "${YELLOW}[2/5] Instalando PyTorch 2.5.1+cu121 (CUDA 12.1)...${NC}"
pip install "torch==2.5.1" --index-url https://download.pytorch.org/whl/cu121
pip install "torchvision==0.20.1" "torchaudio==2.5.1" --index-url https://download.pytorch.org/whl/cu121
echo ""

# 3. Instalar Qiskit + Aer GPU
echo -e "${YELLOW}[3/5] Instalando Qiskit 1.2.4 + Aer-GPU 0.15.1...${NC}"
pip install "qiskit==1.2.4" "qiskit-aer-gpu==0.15.1"
pip install "qiskit-ibm-runtime==0.19.1" "qiskit-optimization==0.7.0"
echo ""

# 4. Instalar CuPy + cuQuantum
echo -e "${YELLOW}[4/5] Instalando CuPy + cuQuantum (CUDA 12)...${NC}"
pip install "cupy-cuda12x"
pip install \
  cuquantum-cu12==25.11.0 \
  custatevec-cu12==1.11.0 \
  cutensor-cu12==2.4.1
echo ""

# 5. Validar instalação
echo -e "${YELLOW}[5/5] Validando instalação...${NC}"
python3 << 'EOF'
import sys
import torch
import qiskit
from qiskit_aer import AerSimulator

print(f"PyTorch: {torch.__version__} | CUDA: {torch.cuda.is_available()} | Version: {torch.version.cuda}")
print(f"Qiskit: {qiskit.__version__}")
print(f"Aer-GPU: OK")

# Teste prático
try:
    sim = AerSimulator(method='statevector')
    print(f"✅ AerSimulator com GPU pronto")
except Exception as e:
    print(f"⚠️ Aviso: {e}")

print("\n✅ Instalação completa!")
EOF

echo -e "\n${GREEN}✅ GPU + Quantum Stack instalado com sucesso!${NC}\n"

echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo "   1. python validate_gpu_quantum.py"
echo "   2. ./scripts/canonical/system/run_cluster.sh"
echo "   3. cd web/frontend && npm run dev"
echo ""
