#!/bin/bash

# 🔬 TEST: CUDA_LAUNCH_BLOCKING impact on Ubuntu GPU
# Compare: WITH vs WITHOUT synchronous mode

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

echo "════════════════════════════════════════════════════════════════"
echo "🔬 TEST: CUDA_LAUNCH_BLOCKING Impact (Ubuntu GTX 1650)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ✅ Check if OmniMind services are running
echo "🔍 Checking OmniMind services..."
python3 << 'SERVICE_CHECK'
import socket
import sys

services = {
    'Qdrant': ('localhost', 6333),
    'Redis': ('localhost', 6379),
}

all_ok = True
for name, (host, port) in services.items():
    try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.close()
        print(f"  ✅ {name}: Running on {host}:{port}")
    except Exception as e:
        print(f"  ❌ {name}: NOT running (expected for GPU test)")
        all_ok = False

if not all_ok:
    print("\n⚠️  Some services not running - GPU test may be limited")
    print("    If needed, start with: bash scripts/recovery/01_init_qdrant_collections.sh")

SERVICE_CHECK

echo ""

# Test 1: WITHOUT CUDA_LAUNCH_BLOCKING (OPTIMIZED)
echo "📊 TEST 1: WITHOUT CUDA_LAUNCH_BLOCKING (GPU parallelization)"
echo "─────────────────────────────────────────────────────────────────"

# ✅ Use new PyTorch var name (PYTORCH_ALLOC_CONF instead of PYTORCH_CUDA_ALLOC_CONF)
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:512"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
unset CUDA_LAUNCH_BLOCKING
export QISKIT_IN_PARALLEL=FALSE
export OMP_NUM_THREADS=4

START_TIME=$(date +%s%N)

python3 << 'PYTHON_CODE'
import time
from src.consciousness.integration_loop import IntegrationLoop

loop = IntegrationLoop()
results = []

# Run 5 quick cycles (benchmark) using SYNC method
for i in range(5):
    try:
        result = loop.execute_cycle_sync(collect_metrics=True)
        results.append(result.phi_estimate)
        print(f"  Cycle {i+1:2d}: Φ={result.phi_estimate:.4f}, t={result.cycle_duration_ms:.1f}ms")
    except Exception as e:
        print(f"  Cycle {i+1:2d}: ERROR - {str(e)[:60]}")
        break

if results:
    avg_phi = sum(results) / len(results)
    print(f"\n✅ Test 1 completed: Avg Φ={avg_phi:.4f}")
else:
    print(f"\n⚠️  Test 1: No valid cycles (services may not be running)")
PYTHON_CODE

END_TIME=$(date +%s%N)
TEST1_MS=$(( (END_TIME - START_TIME) / 1000000 ))
echo "⏱️  Time: ${TEST1_MS}ms for 5 cycles"
echo ""

# Test 2: WITH CUDA_LAUNCH_BLOCKING (SYNC - for comparison)
echo "📊 TEST 2: WITH CUDA_LAUNCH_BLOCKING=1 (sync mode - Kali workaround)"
echo "─────────────────────────────────────────────────────────────────"

export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:512"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1
export QISKIT_IN_PARALLEL=FALSE
export OMP_NUM_THREADS=4

START_TIME=$(date +%s%N)

python3 << 'PYTHON_CODE'
import time
from src.consciousness.integration_loop import IntegrationLoop

loop = IntegrationLoop()
results = []

# Run 5 quick cycles (benchmark) using SYNC method
for i in range(5):
    try:
        result = loop.execute_cycle_sync(collect_metrics=True)
        results.append(result.phi_estimate)
        print(f"  Cycle {i+1:2d}: Φ={result.phi_estimate:.4f}, t={result.cycle_duration_ms:.1f}ms")
    except Exception as e:
        print(f"  Cycle {i+1:2d}: ERROR - {str(e)[:60]}")
        break

if results:
    avg_phi = sum(results) / len(results)
    print(f"\n✅ Test 2 completed: Avg Φ={avg_phi:.4f}")
else:
    print(f"\n⚠️  Test 2: No valid cycles (services may not be running)")
PYTHON_CODE

END_TIME=$(date +%s%N)
TEST2_MS=$(( (END_TIME - START_TIME) / 1000000 ))
echo "⏱️  Time: ${TEST2_MS}ms for 5 cycles"
echo ""

# Analysis
echo "════════════════════════════════════════════════════════════════"
echo "📈 ANALYSIS"
echo "════════════════════════════════════════════════════════════════"
SPEEDUP=$(echo "scale=2; $TEST2_MS / $TEST1_MS" | bc)
echo "Test 1 (WITHOUT sync):  ${TEST1_MS}ms"
echo "Test 2 (WITH sync):     ${TEST2_MS}ms"
echo "Speedup: ${SPEEDUP}x faster WITHOUT CUDA_LAUNCH_BLOCKING"
echo ""

if (( $(echo "$SPEEDUP > 1.5" | bc -l) )); then
    echo "✅ RECOMMENDATION: Remove CUDA_LAUNCH_BLOCKING"
    echo "   Ubuntu + CUDA 13 doesn't need synchronization"
    echo "   GPU parallelization works well"
else
    echo "⚠️  RECOMMENDATION: Keep CUDA_LAUNCH_BLOCKING=1"
    echo "   Synchronization provides better stability on this system"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
