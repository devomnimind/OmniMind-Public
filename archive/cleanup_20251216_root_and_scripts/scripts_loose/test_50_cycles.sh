#!/bin/bash

# 🔬 TEST: 50 Integration Cycles - Monitor what kills the process
# Track memory, GPU, CPU - diagnose if process dies

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

echo "════════════════════════════════════════════════════════════════"
echo "🔬 TEST: 50 Integration Cycles (Memory + GPU Monitoring)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check system limits BEFORE running
echo "📊 System Limits & Configuration:"
echo "─────────────────────────────────────────────────────────────────"
echo "Hard memory limit (ulimit -v): $(ulimit -v 2>/dev/null || echo 'unlimited')"
echo "Soft memory limit (ulimit -m): $(ulimit -m 2>/dev/null || echo 'unlimited')"
echo "Max processes (ulimit -u): $(ulimit -u 2>/dev/null || echo '4096')"
echo "Max file descriptors: $(ulimit -n 2>/dev/null || echo '1024')"
echo ""

# Set GPU environment (optimized Ubuntu)
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
unset CUDA_LAUNCH_BLOCKING
export QISKIT_IN_PARALLEL=FALSE
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2

echo "✅ GPU environment configured"
echo ""

# Start background monitoring
LOG_FILE="logs/cycles_test_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# Monitor GPU/Memory every 2 seconds
monitor_system() {
    while true; do
        timestamp=$(date '+%H:%M:%S')
        if command -v nvidia-smi &> /dev/null; then
            gpu_mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
            gpu_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1)
            echo "[$timestamp] GPU Memory: ${gpu_mem}MB | GPU Util: ${gpu_util}%" >> "$LOG_FILE"
        fi

        cpu_mem=$(free -m | awk 'NR==2{printf("%d", $3)}')
        cpu_util=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{printf("%.0f", 100 - $1)}')
        echo "[$timestamp] CPU Memory: ${cpu_mem}MB | CPU: ${cpu_util}%" >> "$LOG_FILE"

        sleep 2
    done
}

# Start monitoring in background
monitor_system &
MONITOR_PID=$!

# Cleanup on exit
cleanup() {
    echo ""
    echo "Killing monitor process..."
    kill $MONITOR_PID 2>/dev/null || true
    echo "📋 Full log saved to: $LOG_FILE"
}

trap cleanup EXIT

echo "🚀 Running 50 Integration Cycles..."
echo "─────────────────────────────────────────────────────────────────"
echo ""

python3 << 'PYTHON_CODE'
import sys
import gc
import tracemalloc
from src.consciousness.integration_loop import IntegrationLoop

# ✅ Enable memory tracking
tracemalloc.start()

try:
    loop = IntegrationLoop()
    results = []
    errors = []

    for cycle_num in range(50):
        try:
            # Execute cycle
            result = loop.execute_cycle_sync(collect_metrics=True)
            results.append(result.phi_estimate)

            # Get current memory usage
            current, peak = tracemalloc.get_traced_memory()
            current_mb = current / 1024 / 1024
            peak_mb = peak / 1024 / 1024

            # Print progress every 10 cycles
            if (cycle_num + 1) % 10 == 0:
                print(f"✅ Cycle {cycle_num+1:3d}/50: Φ={result.phi_estimate:.4f}, " +
                      f"t={result.cycle_duration_ms:.1f}ms, " +
                      f"MEM={current_mb:.1f}MB/{peak_mb:.1f}MB")
            else:
                print(f"  Cycle {cycle_num+1:3d}/50: Φ={result.phi_estimate:.4f}, " +
                      f"t={result.cycle_duration_ms:.1f}ms", end='', flush=True)
                if (cycle_num + 1) % 10 != 0:
                    print()  # newline

            # ✅ Garbage collection EVERY CYCLE (aggressive - prevent memory bloat)
            # Was every 10 cycles, now every cycle to prevent leak
            gc.collect()

        except Exception as e:
            error_msg = f"Cycle {cycle_num+1}: {str(e)}"
            errors.append(error_msg)
            print(f"\n❌ {error_msg}")
            traceback.print_exc()
            # Don't stop, continue to next cycle
            continue

    print("\n")
    print("════════════════════════════════════════════════════════════════")
    print("📊 RESULTS")
    print("════════════════════════════════════════════════════════════════")

    if results:
        avg_phi = sum(results) / len(results)
        min_phi = min(results)
        max_phi = max(results)
        print(f"✅ Completed: {len(results)}/50 cycles")
        print(f"   Avg Φ: {avg_phi:.4f}")
        print(f"   Min Φ: {min_phi:.4f}")
        print(f"   Max Φ: {max_phi:.4f}")

    if errors:
        print(f"\n⚠️  Errors encountered: {len(errors)}")
        for err in errors[:5]:
            print(f"   - {err}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")

    # Final memory snapshot
    current, peak = tracemalloc.get_traced_memory()
    print(f"\n💾 Memory Usage:")
    print(f"   Current: {current / 1024 / 1024:.1f} MB")
    print(f"   Peak: {peak / 1024 / 1024:.1f} MB")

    # Success if we got through 50
    if len(results) == 50:
        print("\n🎉 SUCCESS: All 50 cycles completed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  PARTIAL: {len(results)}/50 cycles (check logs for errors)")
        sys.exit(1)

except KeyboardInterrupt:
    print("\n\n⏹️  Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    traceback.print_exc()
    sys.exit(2)

PYTHON_CODE

EXIT_CODE=$?
echo ""
echo "════════════════════════════════════════════════════════════════"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ TEST PASSED: 50 cycles completed successfully!"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "⚠️  TEST PARTIAL: Some cycles completed, check log for errors"
else
    echo "❌ TEST FAILED: Process died prematurely"
fi

echo ""
echo "📋 Monitoring log: $LOG_FILE"
echo "📊 Check for:"
echo "   • GPU memory growing unbounded?"
echo "   • CPU memory growing?"
echo "   • Sudden spikes before crash?"
echo ""
echo "════════════════════════════════════════════════════════════════"
