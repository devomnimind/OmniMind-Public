#!/bin/bash

# 🔧 FIX: Qiskit ProviderV1 Import Error (13 DEZ)
# Resolve: "cannot import name 'ProviderV1' from 'qiskit.providers'"

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo -e "\033[0;36m🔧 Fixing Qiskit ProviderV1 Import Error\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

echo "🔍 Current Qiskit versions:"
pip list | grep -i qiskit || echo "No Qiskit packages found"
echo ""

echo "🗑️  Cleaning pip cache..."
pip cache purge

echo "📦 Uninstalling conflicting Qiskit packages..."
pip uninstall -y qiskit qiskit-aer qiskit-algorithms qiskit-optimization qiskit-machine-learning qiskit-ibm-runtime 2>/dev/null || true
pip uninstall -y qiskit-ibm-provider 2>/dev/null || true

echo ""
echo "📥 Installing Qiskit with COMPATIBLE versions..."
echo "   Target: Qiskit 0.46+ (compatible with Python 3.12)"
echo ""

# Install specific versions that work together
pip install --upgrade \
    'qiskit>=0.46.0' \
    'qiskit-aer>=0.13.0' \
    'qiskit-algorithms>=0.2.0' \
    'qiskit-optimization>=0.6.0' \
    --no-cache-dir

echo ""
echo "✅ Testing Qiskit imports..."
python3 << 'PYTHON_END'
import sys

print("Testing Qiskit imports...")

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

# Test 3: Create a test circuit
try:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    print("  ✅ QuantumCircuit creation")
except Exception as e:
    print(f"  ❌ QuantumCircuit creation: {e}")
    sys.exit(1)

# Test 4: AerSimulator with GPU (may fail if no GPU, that's OK)
try:
    sim = AerSimulator(device='GPU')
    print("  ✅ AerSimulator with GPU")
except Exception as e:
    print(f"  ⚠️  AerSimulator GPU: {e}")
    print("  ℹ️  Falling back to CPU (this is OK if no GPU available)")
    try:
        sim = AerSimulator(device='CPU')
        print("  ✅ AerSimulator with CPU (fallback)")
    except Exception as e2:
        print(f"  ❌ AerSimulator CPU fallback: {e2}")
        sys.exit(1)

print("")
print("✅ All Qiskit imports working!")

PYTHON_END

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Qiskit fix complete!"
    echo ""
    echo "🎯 Next step: Run Phase 3 script"
    echo "   bash scripts/recovery/03_run_integration_cycles_qiskit_gpu.sh"
    echo ""
else
    echo ""
    echo "❌ Qiskit fix failed - check error above"
    exit 1
fi
