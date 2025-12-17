#!/bin/bash
# ✅ VS Code VENV + CUDA 12 Configuration Test
# Purpose: Verify new venv is active in VS Code terminal with CUDA 12.4

echo "=========================================="
echo "✅ VS Code VENV + CUDA 12 Configuration Test"
echo "=========================================="
echo ""

# Test 1: VIRTUAL_ENV is set
echo "1️⃣ Checking VIRTUAL_ENV variable..."
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ VIRTUAL_ENV not set"
    echo "   Solution: Close and reopen VS Code terminal"
else
    echo "✅ VIRTUAL_ENV = $VIRTUAL_ENV"
fi
echo ""

# Test 2: Python from venv
echo "2️⃣ Checking Python path..."
PYTHON_PATH=$(which python)
if [[ "$PYTHON_PATH" == *".venv"* ]]; then
    echo "✅ Python from venv: $PYTHON_PATH"
else
    echo "❌ Python NOT from venv: $PYTHON_PATH"
    echo "   Solution: Close and reopen VS Code terminal"
fi
echo ""

# Test 3: Python version
echo "3️⃣ Checking Python version..."
PYTHON_VERSION=$(python --version)
echo "   Version: $PYTHON_VERSION"
if [[ "$PYTHON_VERSION" == *"3.12"* ]]; then
    echo "✅ Correct version (3.12.x)"
else
    echo "⚠️  Unexpected version"
fi
echo ""

# Test 4: CUDA 12 environment
echo "4️⃣ Checking CUDA 12 configuration..."
if [ "$CUDA_HOME" = "/usr/local/cuda-12" ]; then
    echo "✅ CUDA_HOME = /usr/local/cuda-12"
else
    echo "❌ CUDA_HOME = $CUDA_HOME (expected /usr/local/cuda-12)"
fi
echo ""

# Test 5: LD_LIBRARY_PATH
echo "5️⃣ Checking LD_LIBRARY_PATH..."
if [[ "$LD_LIBRARY_PATH" == *"cuda-12"* ]]; then
    echo "✅ CUDA 12 in LD_LIBRARY_PATH"
    echo "   LD_LIBRARY_PATH starts with: ${LD_LIBRARY_PATH:0:80}..."
else
    echo "⚠️  CUDA 12 not in LD_LIBRARY_PATH"
fi
echo ""

# Test 6: Torch CUDA availability
echo "6️⃣ Checking Torch CUDA..."
python -c "import torch; print(f'✅ Torch CUDA available: {torch.cuda.is_available()}'); print(f'   Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>/dev/null || echo "❌ Error importing torch"
echo ""

# Test 7: Qiskit Aer GPU
echo "7️⃣ Checking Qiskit Aer GPU..."
python -c "from qiskit_aer import AerSimulator; sim = AerSimulator(method='statevector', device='GPU'); print(f'✅ Qiskit GPU Backend: {sim.name}'); print(f'   Available Devices: {sim.available_devices()}')" 2>/dev/null || echo "❌ Error importing qiskit_aer"
echo ""

# Test 8: Check for CUDA 11 contamination
echo "8️⃣ Checking for CUDA 11 contamination..."
CUDA11_COUNT=$(pip list | grep -E "cu11|cuda-11" | wc -l)
if [ "$CUDA11_COUNT" -eq 0 ]; then
    echo "✅ ZERO CUDA 11 packages (clean environment)"
else
    echo "❌ Found $CUDA11_COUNT CUDA 11 packages (contamination!)"
    pip list | grep -E "cu11|cuda-11"
fi
echo ""

# Test 9: Quick GPU performance test
echo "9️⃣ Running GPU performance test..."
python -c "
import torch
import time

x = torch.randn(1000, 1000).cuda()
y = torch.randn(1000, 1000).cuda()

start = time.time()
for _ in range(100):
    z = torch.matmul(x, y)
elapsed = time.time() - start

print(f'✅ GPU Matrix Multiplication (100x1000x1000): {elapsed:.3f}s')
print(f'   Throughput: {(1000*1000*1000*100) / (elapsed*1e9):.1f} GFLOPs')
" 2>/dev/null || echo "❌ GPU test failed"
echo ""

echo "=========================================="
echo "✅ Configuration Test Complete!"
echo "=========================================="
echo ""
echo "📝 Notes:"
echo "  • If any test failed: Close and reopen VS Code"
echo "  • If CUDA 11 contamination: Delete .venv and rebuild"
echo "  • For full validation: python final_check.py"
echo ""
