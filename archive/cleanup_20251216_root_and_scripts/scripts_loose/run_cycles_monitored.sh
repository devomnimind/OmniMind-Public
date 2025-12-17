#!/bin/bash

# 🔍 RUN CYCLES WITH DETAILED MONITORING
# Log cada linha do processo para ver exatamente onde morre

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

# Setup logging
MONITOR_LOG="logs/detailed_monitor_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$MONITOR_LOG")"

echo "🔍 DETAILED CYCLE MONITORING" | tee -a "$MONITOR_LOG"
echo "================================================" | tee -a "$MONITOR_LOG"
echo "Log: $MONITOR_LOG" | tee -a "$MONITOR_LOG"
echo "" | tee -a "$MONITOR_LOG"

# Set GPU environment (minimal - threads=2, memory=256)
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=2
export QISKIT_IN_PARALLEL=FALSE

# Disable monitors
export OMNIMIND_DISABLE_RESOURCE_PROTECTOR=1
export OMNIMIND_DISABLE_ALERT_SYSTEM=1

echo "[$(date)] Environment set" | tee -a "$MONITOR_LOG"
echo "[$(date)] Running Python with detailed logging..." | tee -a "$MONITOR_LOG"
echo "" | tee -a "$MONITOR_LOG"

# Run Python directly with monitoring
python3 << 'EOF' 2>&1 | tee -a "$MONITOR_LOG"
import sys
import os
import traceback
import signal
import time
from datetime import datetime

sys.path.insert(0, 'src')

# Handler para signals
def signal_handler(signum, frame):
    print(f"\n[SIGNAL {signum}] Received at cycle {cycle_num if 'cycle_num' in locals() else '?'}")
    sys.exit(128 + signum)

signal.signal(signal.SIGTERM, signal_handler)

cycle_num = 0
try:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Importing IntegrationLoop...")
    sys.stdout.flush()

    from src.consciousness.integration_loop import IntegrationLoop
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Import complete")
    sys.stdout.flush()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating IntegrationLoop instance...")
    sys.stdout.flush()

    loop = IntegrationLoop()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ IntegrationLoop created")
    sys.stdout.flush()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting 50 cycles...")
    sys.stdout.flush()

    for cycle_num in range(1, 51):
        try:
            print(f"[CYCLE {cycle_num:02d}] Starting...", end='', flush=True)

            start = time.time()
            result = loop.execute_cycle_sync(collect_metrics=True)
            elapsed = time.time() - start

            phi_val = getattr(result, 'phi_estimate', 0.0)
            duration = getattr(result, 'cycle_duration_ms', 0)
            modules = getattr(result, 'modules_executed', [])

            print(f" ✅ ({elapsed:.2f}s) Φ={phi_val:.4f} [{', '.join(modules[:3])}...]")
            sys.stdout.flush()

        except KeyboardInterrupt:
            print(f"\n[INTERRUPT] Cycle {cycle_num} interrupted by user")
            break
        except Exception as e:
            print(f" ❌ Error: {str(e)[:60]}")
            traceback.print_exc()
            sys.stdout.flush()

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ Completed {cycle_num} cycles!")
    sys.exit(0)

except Exception as e:
    print(f"\n[FATAL] {str(e)}")
    traceback.print_exc()
    sys.exit(1)

EOF

EXIT=$?
echo "" | tee -a "$MONITOR_LOG"
echo "════════════════════════════════════════" | tee -a "$MONITOR_LOG"
echo "Exit code: $EXIT" | tee -a "$MONITOR_LOG"

if [ $EXIT -eq 0 ]; then
    echo "✅ SUCCESS" | tee -a "$MONITOR_LOG"
elif [ $EXIT -eq 143 ]; then
    echo "❌ SIGTERM (killed)" | tee -a "$MONITOR_LOG"
elif [ $EXIT -eq 137 ]; then
    echo "❌ SIGKILL (force killed)" | tee -a "$MONITOR_LOG"
else
    echo "❌ Exit code $EXIT" | tee -a "$MONITOR_LOG"
fi

echo "" | tee -a "$MONITOR_LOG"
echo "Full log: $MONITOR_LOG" | tee -a "$MONITOR_LOG"
