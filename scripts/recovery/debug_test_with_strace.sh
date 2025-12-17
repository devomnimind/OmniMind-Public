#!/bin/bash

# Debug test com strace para ver sinais
PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

export OMNIMIND_RESOURCE_PROTECTOR_MODE=test
export OMNIMIND_METRICS_COLLECTOR_MODE=test
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=2
export QISKIT_IN_PARALLEL=FALSE

echo "🔍 DEBUG: Running test with strace to capture signals and syscalls..."
echo "Looking for: SIGTERM, SIGKILL, process death, exit calls"
echo ""

mkdir -p logs

# Run with strace to capture all system calls and signals
timeout 120 strace -f -e trace=kill,exit,exit_group,signal -o logs/strace_debug.log python3 << 'EOF' 2>&1 | tee logs/test_debug.log
import sys
import os
sys.path.insert(0, 'src')

from datetime import datetime
from src.consciousness.integration_loop import IntegrationLoop

try:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating IntegrationLoop...")
    loop = IntegrationLoop()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting cycles...")

    for cycle_num in range(1, 51):
        try:
            print(f"[CYCLE {cycle_num:02d}] Starting...", end='', flush=True)
            result = loop.execute_cycle_sync(collect_metrics=False)
            print(f" ✅")
            sys.stdout.flush()
        except KeyboardInterrupt:
            print(f"\n[INTERRUPT]")
            break
        except Exception as e:
            print(f" ❌ {type(e).__name__}: {str(e)[:50]}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Completed {cycle_num} cycles")

except Exception as e:
    print(f"\n[FATAL] {e}")
    import traceback
    traceback.print_exc()

EOF

echo ""
echo "════════════════════════════════════════"
echo "Strace output (signals and kills):"
echo "════════════════════════════════════════"
grep -E "SIGTERM|SIGKILL|SIG[0-9]|exit|kill" logs/strace_debug.log | head -20

echo ""
echo "Log file: logs/test_debug.log"
echo "Strace log: logs/strace_debug.log"
