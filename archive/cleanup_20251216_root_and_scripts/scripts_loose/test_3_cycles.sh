#!/bin/bash

# 🚀 QUICK TEST: 3 ciclos para verificar se memory leak foi corrigido

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

echo "════════════════════════════════════════════════════════════════"
echo "🚀 QUICK TEST: 3 Integration Cycles (Memory Optimized)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Set OPTIMIZED environment
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
unset CUDA_LAUNCH_BLOCKING
export QISKIT_IN_PARALLEL=FALSE
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2

echo "📊 Environment:"
echo "   PYTORCH_ALLOC_CONF=backend:cudaMallocAsync,max_split_size_mb:256"
echo "   OMP_NUM_THREADS=2 (was 4)"
echo "   GC=every cycle (aggressive)"
echo ""

python3 << 'PYTHON_CODE'
import sys
import gc
import time
import tracemalloc
sys.path.insert(0, 'src')

tracemalloc.start()

try:
    from consciousness.integration_loop import IntegrationLoop

    print("1. Initializing IntegrationLoop...")
    loop = IntegrationLoop()
    print("   ✅ Initialized")
    print("")

    results = []
    for cycle_num in range(3):
        try:
            start_time = time.time()
            result = loop.execute_cycle_sync(collect_metrics=True)
            elapsed = time.time() - start_time

            results.append(result.phi_estimate)
            current, peak = tracemalloc.get_traced_memory()
            current_mb = current / 1024 / 1024
            peak_mb = peak / 1024 / 1024

            print(f"✅ Cycle {cycle_num+1}/3:")
            print(f"   Φ={result.phi_estimate:.4f}")
            print(f"   Time={elapsed:.1f}s")
            print(f"   Memory: {current_mb:.1f}MB / {peak_mb:.1f}MB")

            # Aggressive GC every cycle
            gc.collect()

        except Exception as e:
            print(f"❌ Cycle {cycle_num+1}: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            break

    print("")
    print("════════════════════════════════════════════════════════════════")
    print("📊 SUMMARY")
    print("════════════════════════════════════════════════════════════════")

    if results:
        avg_phi = sum(results) / len(results)
        print(f"✅ Completed: {len(results)}/3 cycles")
        print(f"   Avg Φ: {avg_phi:.4f}")

    current, peak = tracemalloc.get_traced_memory()
    print(f"\n💾 Final Memory:")
    print(f"   Current: {current / 1024 / 1024:.1f} MB")
    print(f"   Peak: {peak / 1024 / 1024:.1f} MB")

    if len(results) == 3:
        print("\n✅ SUCCESS: All 3 cycles passed!")
        print("Ready for test_50_cycles.sh")
        sys.exit(0)
    else:
        print(f"\n⚠️  Only {len(results)}/3 completed - memory issue?")
        sys.exit(1)

except KeyboardInterrupt:
    print("\n⏹️  Interrupted")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ FATAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(2)
PYTHON_CODE

echo ""
echo "════════════════════════════════════════════════════════════════"
