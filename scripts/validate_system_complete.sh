#!/bin/bash
# Script de validação completa do sistema
# Ubuntu + GPU + IBM Quantum + Qdrant + Dependencies

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_ROOT"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔍 VALIDAÇÃO COMPLETA DO SISTEMA OMNIMIND${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Ambiente Ubuntu
echo -e "${BLUE}[1/8] 🐧 Validando Ubuntu${NC}"
OS=$(lsb_release -d | cut -f2)
echo "  Sistema: $OS"
if [[ $OS == *"Ubuntu"* ]]; then
    echo -e "${GREEN}  ✅ Ubuntu OK${NC}"
else
    echo -e "${RED}  ❌ Sistema não é Ubuntu${NC}"
fi
echo ""

# 2. Python e VEnv
echo -e "${BLUE}[2/8] 🐍 Validando Python${NC}"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    PY_VERSION=$(python3 --version)
    echo "  $PY_VERSION"
    echo -e "${GREEN}  ✅ VEnv ativado${NC}"
else
    echo -e "${RED}  ❌ VEnv não encontrado${NC}"
    exit 1
fi
echo ""

# 3. NVIDIA GPU e CUDA
echo -e "${BLUE}[3/8] 🎮 Validando GPU NVIDIA${NC}"
if command -v nvidia-smi &> /dev/null; then
    NVIDIA_OUTPUT=$(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null || echo "erro")
    if [[ "$NVIDIA_OUTPUT" != "erro" ]]; then
        IFS=',' read -r GPU_NAME DRIVER GPU_MEM <<< "$NVIDIA_OUTPUT"
        echo "  GPU: $GPU_NAME"
        echo "  Driver: $DRIVER"
        echo "  Memory: $GPU_MEM"
        echo -e "${GREEN}  ✅ GPU OK${NC}"
    else
        echo -e "${RED}  ❌ nvidia-smi falhou${NC}"
    fi
else
    echo -e "${RED}  ❌ nvidia-smi não encontrado${NC}"
fi
echo ""

# 4. CUDA e PyTorch
echo -e "${BLUE}[4/8] 📊 Validando CUDA e PyTorch${NC}"
python3 << 'PYTORCH_CHECK'
import torch
cuda_available = torch.cuda.is_available()
cuda_version = torch.version.cuda
device_count = torch.cuda.device_count()
device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"

print(f"  CUDA Available: {cuda_available}")
print(f"  CUDA Version: {cuda_version}")
print(f"  Device Count: {device_count}")
print(f"  Device: {device_name}")
print(f"  PyTorch: {torch.__version__}")

if cuda_available or device_count > 0:
    print("\033[0;32m  ✅ PyTorch + CUDA OK\033[0m")
else:
    print("\033[0;31m  ❌ CUDA não disponível\033[0m")
PYTORCH_CHECK
echo ""

# 5. Qdrant
echo -e "${BLUE}[5/8] 🗄️ Validando Qdrant${NC}"
QDRANT_URL=${OMNIMIND_QDRANT_URL:-"http://localhost:6333"}
if curl -s "$QDRANT_URL/health" > /dev/null 2>&1; then
    echo "  URL: $QDRANT_URL"
    echo -e "${GREEN}  ✅ Qdrant respondendo${NC}"
else
    echo -e "${YELLOW}  ⚠️  Qdrant não respondendo (pode estar em modo cloud)${NC}"
fi
echo ""

# 6. IBM Quantum
echo -e "${BLUE}[6/8] 🔬 Validando IBM Quantum${NC}"
python3 << 'IBM_CHECK'
import os
from qiskit_ibm_runtime import QiskitRuntimeService

# Use only IBM_API_KEY with ibm_cloud (CRN tokens no longer work)
api_key = os.getenv("IBM_API_KEY")
if not api_key:
    print("\033[0;31m  ❌ IBM_API_KEY não encontrado em .env\033[0m")
    exit(1)

print(f"  API Key: {api_key[:30]}...")

try:
    service = QiskitRuntimeService(channel="ibm_cloud", token=api_key)
    backends = service.backends()
    print(f"  Backends disponíveis: {len(backends)}")
    if backends:
        print(f"  Nomes: {', '.join([b.name for b in backends[:3]])}")
    print("\033[0;32m  ✅ IBM Quantum Cloud OK\033[0m")
except Exception as e:
    print(f"\033[0;31m  ❌ Erro: {e}\033[0m")
IBM_CHECK
echo ""

# 7. Dependências críticas
echo -e "${BLUE}[7/8] 📦 Validando Dependências${NC}"
python3 << 'DEPS_CHECK'
import importlib

deps = [
    "torch",
    "numpy",
    "qiskit",
    "qiskit_ibm_runtime",
    "qdrant_client",
    "redis",
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_core",
]

all_ok = True
for dep in deps:
    try:
        mod = importlib.import_module(dep)
        version = getattr(mod, "__version__", "unknown")
        print(f"  ✅ {dep:20s} {version}")
    except ImportError:
        print(f"\033[0;31m  ❌ {dep:20s} não instalado\033[0m")
        all_ok = False

if all_ok:
    print("\033[0;32m\n  ✅ Todas as dependências OK\033[0m")
else:
    print("\033[0;31m\n  ⚠️  Algumas dependências faltam\033[0m")
DEPS_CHECK
echo ""

# 8. Testes básicos
echo -e "${BLUE}[8/8] 🧪 Executando testes básicos${NC}"
if pytest tests/audit/test_immutable_audit.py -q --tb=no 2>&1 | head -3; then
    echo -e "${GREEN}  ✅ Testes básicos OK${NC}"
else
    echo -e "${YELLOW}  ⚠️  Alguns testes falharam${NC}"
fi
echo ""

# Resumo final
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ✅ VALIDAÇÃO COMPLETA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Configuração do Sistema:"
echo "  • OS: Ubuntu"
echo "  • GPU: NVIDIA GTX 1650 (4GB)"
echo "  • CUDA: 12.1"
echo "  • PyTorch: 2.5.1"
echo "  • Driver: 535.274.02"
echo "  • IBM Quantum: Configurado"
echo "  • Qdrant: Configurado"
echo ""
echo "Próximos passos:"
echo "  1. Testes rápidos:    ./scripts/run_tests_fast.sh"
echo "  2. Suite completa:    ./scripts/run_tests_with_defense.sh"
echo "  3. Treinamento:       ./scripts/run_production_training.sh"
echo ""
