#!/bin/bash

# 🔄 RESTAURAR: Qiskit para versões ANTIGAS validadas (13 DEZ)
# Remove Qiskit 2.2.3 novo (incompatível) e volta para versões antigas

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo -e "\033[0;36m🔄 Restaurando Qiskit para versões ANTIGAS validadas\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

echo "📋 Removendo Qiskit 2.2.3 (NOVO - incompatível)..."
pip uninstall -y qiskit qiskit-aer qiskit-algorithms qiskit-optimization 2>/dev/null || true

echo ""
echo "📥 Instalando versões ANTIGAS validadas..."
echo "   Target: Qiskit 0.43.x (versão antiga estável)"
echo ""

# Install OLDER compatible versions
pip install --upgrade \
    'qiskit<1.0,>=0.43.0' \
    'qiskit-aer<0.13,>=0.12.0' \
    'qiskit-algorithms>=0.1.0' \
    'qiskit-optimization>=0.5.0' \
    --no-cache-dir

echo ""
echo "✅ Testando Qiskit imports (versão antiga)..."
python3 << 'PYTHON_END'
import sys

print("Testing Qiskit (old version) imports...")

# Test 1: Basic imports
try:
    from qiskit import QuantumCircuit, QuantumRegister
    print("  ✅ QuantumCircuit, QuantumRegister")
except ImportError as e:
    print(f"  ❌ QuantumCircuit/QuantumRegister: {e}")
    sys.exit(1)

# Test 2: Aer simulator
try:
    from qiskit_aer import AerSimulator
    print("  ✅ AerSimulator")
except ImportError as e:
    print(f"  ❌ AerSimulator: {e}")
    sys.exit(1)

# Test 3: Check versions
try:
    import qiskit
    import qiskit_aer
    print(f"  ✅ Qiskit version: {qiskit.__version__}")
    print(f"  ✅ Qiskit-Aer version: {qiskit_aer.__version__}")
except Exception as e:
    print(f"  ⚠️  {e}")

# Test 4: Create test circuit
try:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    print("  ✅ QuantumCircuit creation")
except Exception as e:
    print(f"  ❌ QuantumCircuit creation: {e}")
    sys.exit(1)

print("")
print("✅ Qiskit OLD versions working!")

PYTHON_END

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Restauração concluída!"
    echo ""
    echo "📋 Versões instaladas:"
    pip list | grep -i qiskit
    echo ""
else
    echo ""
    echo "❌ Restauração falhou"
    exit 1
fi
