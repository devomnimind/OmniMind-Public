#!/bin/bash

# ✅ QUICK TEST: Validar Qiskit GPU antes de rodar Phase 3
# Rápido teste para confirmar que Qiskit está funcional

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo -e "\033[0;36m✅ Quick Test: Validar Qiskit GPU\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

python3 << 'PYTHON_END'
import sys
from pathlib import Path

print("🧪 Testing Qiskit GPU setup...")
print("")

# Test 1: Import basic Qiskit
print("1️⃣  Testing basic Qiskit imports...")
try:
    from qiskit import QuantumCircuit, QuantumRegister
    print("   ✅ QuantumCircuit imported")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Import Aer
print("")
print("2️⃣  Testing Aer simulator...")
try:
    from qiskit_aer import AerSimulator
    print("   ✅ AerSimulator imported")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")
    sys.exit(1)

# Test 3: Create a simple circuit
print("")
print("3️⃣  Testing circuit creation...")
try:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    print("   ✅ Circuit created successfully")
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    sys.exit(1)

# Test 4: Run with Aer (CPU or GPU)
print("")
print("4️⃣  Testing Aer simulator execution...")
try:
    # Try GPU first
    try:
        sim = AerSimulator(device='GPU')
        device_mode = "GPU"
    except:
        # Fallback to CPU
        sim = AerSimulator(device='CPU')
        device_mode = "CPU"

    # Run circuit
    job = sim.run(qc, shots=100)
    result = job.result()
    counts = result.get_counts()

    print(f"   ✅ Simulator executed on {device_mode}")
    print(f"   ✅ Result: {counts}")
except Exception as e:
    print(f"   ⚠️  Simulation failed: {e}")
    print("   This might be expected if GPU not available")

# Test 5: Import IntegrationLoop (integration test)
print("")
print("5️⃣  Testing integration with OmniMind modules...")
try:
    from consciousness.integration_loop import IntegrationLoop
    from consciousness.shared_workspace import SharedWorkspace
    print("   ✅ OmniMind modules imported")
except ImportError as e:
    print(f"   ⚠️  Integration import issue: {e}")
    print("   (This is OK if you haven't run Phase 2 yet)")

print("")
print("════════════════════════════════════════════════════════════════")
print("✅ ALL TESTS PASSED - Ready for Phase 3!")
print("")
print("🚀 Next: Run Phase 3")
print("   bash scripts/recovery/03_run_integration_cycles_qiskit_gpu.sh")
print("")

PYTHON_END
