#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "🔧 FIX GPU: Downgrade Qiskit 1.4.5 → 1.3.x LTS (GPU Compatible)"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""

# Ensure we're in correct directory
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

echo "STEP 1: Current Status"
echo "─────────────────────────────────────────────────────────────────────────────────"
python3 -c "import qiskit; print(f'Current Qiskit: {qiskit.__version__}')"
echo ""

echo "STEP 2: Clear pip cache to avoid version conflicts"
echo "─────────────────────────────────────────────────────────────────────────────────"
pip cache purge
echo "✅ Cache cleared"
echo ""

echo "STEP 3: Downgrade Qiskit to 1.3.x LTS (GPU compatible)"
echo "─────────────────────────────────────────────────────────────────────────────────"
echo "Installing: qiskit>=1.3.0,<1.4.0 (LTS)"
pip install --force-reinstall --no-cache-dir 'qiskit>=1.3.0,<1.4.0'
echo ""

echo "STEP 4: Ensure Qiskit-Aer GPU is correct version"
echo "─────────────────────────────────────────────────────────────────────────────────"
echo "Installing: qiskit-aer>=0.15.0"
pip install --force-reinstall --no-cache-dir 'qiskit-aer>=0.15.0'
echo ""

echo "STEP 5: Verify fix"
echo "─────────────────────────────────────────────────────────────────────────────────"
python3 << 'VERIFY'
import qiskit
print(f"✅ Qiskit version: {qiskit.__version__}")

# Test convert_to_target
try:
    from qiskit import convert_to_target
    print("✅ convert_to_target available (GPU compatible)")
except ImportError:
    print("❌ convert_to_target still missing!")
    import sys
    sys.exit(1)

# Test GPU simulator
try:
    from qiskit_aer import AerSimulator
    sim = AerSimulator(method='statevector', device='GPU')
    print("✅ GPU simulator initialized successfully")
except Exception as e:
    print(f"❌ GPU simulator failed: {e}")
    import sys
    sys.exit(1)

print("")
print("═" * 80)
print("✅ GPU FIX SUCCESSFUL - Qiskit 1.3.x with GPU support is ready")
print("═" * 80)
VERIFY
echo ""

echo "STEP 6: Setup environment variables"
echo "─────────────────────────────────────────────────────────────────────────────────"
source scripts/setup_gpu_ubuntu.sh
echo "✅ Environment variables configured"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "✅ GPU FIX COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Run 50-cycle GPU test: bash scripts/recovery/03_run_50_cycles.sh"
echo "  2. Monitor GPU usage: nvidia-smi"
echo "  3. If successful, run 500-cycle test: bash scripts/recovery/03_run_500_cycles_no_timeout.sh"
echo ""
