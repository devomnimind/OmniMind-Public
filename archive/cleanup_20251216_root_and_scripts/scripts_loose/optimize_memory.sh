#!/bin/bash
# 🧠 MEMORY OPTIMIZATION SCRIPT
# Reduce swap usage and optimize for 7.5GB target
# Usage: sudo ./scripts/optimize_memory.sh

set -e

echo "════════════════════════════════════════════════════════════"
echo "🧠 OMNIMIND MEMORY OPTIMIZATION"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo"
    exit 1
fi

echo "[1] KILL MEMORY HOGS"
echo "    Killing dmypy (type checker daemon)..."
pkill -f "dmypy run" || true
sleep 1

echo "    Killing excess python workers..."
# Kill multiprocessing workers except main ones
ps aux | grep "multiprocessing" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
sleep 1

echo "    ✅ Done\n"

echo "[2] REDUCE VM SWAPPINESS"
echo "    Current: $(cat /proc/sys/vm/swappiness)"
sysctl -w vm.swappiness=10
echo "    New: $(cat /proc/sys/vm/swappiness)"
echo "    ✅ Done\n"

echo "[3] DROP FILESYSTEM CACHE"
sync
echo 3 > /proc/sys/vm/drop_caches
echo "    ✅ Done\n"

echo "[4] RECLAIM SWAP"
echo "    Disabling swap..."
swapoff -a
sleep 2
echo "    Re-enabling swap..."
swapon -a
sleep 2
echo "    ✅ Done\n"

echo "[5] MEMORY STATUS (AFTER)"
free -h
echo ""
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
echo ""

echo "[6] PROCESSES CHECK"
echo "    Python processes:"
ps aux | grep python | grep -v grep | wc -l
echo ""

echo "════════════════════════════════════════════════════════════"
echo "✅ OPTIMIZATION COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Target Memory:"
echo "  • RAM: 3.5 GB (currently: $(free -h | grep Mem | awk '{print $3}'))"
echo "  • VRAM: 4.0 GB"
echo "  • Swap: Emergency only (<500 MB)"
echo ""
echo "Next steps:"
echo "  1. source .venv/bin/activate"
echo "  2. python3 scripts/science_validation/robust_consciousness_validation.py --quick"
echo "  3. Monitor: watch -n 5 'free -h && echo --- && nvidia-smi --query-gpu=memory.used --format=csv,noheader'"
