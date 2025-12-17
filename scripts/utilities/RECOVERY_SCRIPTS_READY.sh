#!/bin/bash

# 🎯 OMNIMIND RECOVERY - QUICK START
# ════════════════════════════════════════════════════════════════════
# Status: ✅ ALL SCRIPTS READY FOR EXECUTION
# Time: ~30-45 minutes (automated) or manual step-by-step
# ════════════════════════════════════════════════════════════════════

# 📂 Location: /home/fahbrain/projects/omnimind/scripts/recovery/

# 🚀 FASTEST WAY TO RUN:

cd /home/fahbrain/projects/omnimind

# Option 1: AUTOMATED (Recommended - runs all 6 steps)
bash scripts/MASTER_RECOVERY_EXECUTOR.sh
# Then select: A (for Automated)

# Option 2: MANUAL (Run steps individually)
# bash scripts/recovery/01_init_qdrant_collections.sh
# bash scripts/recovery/02_train_embeddings.sh
# bash scripts/recovery/03_run_integration_cycles.sh
# bash scripts/recovery/04_init_persistent_state.sh
# bash scripts/recovery/05_fix_gpu_allocation.sh
# bash scripts/recovery/06_increase_daemon_logging.sh

# 📋 WHAT EACH SCRIPT DOES:
# ════════════════════════════════════════════════════════════════════
#
# 1️⃣ 01_init_qdrant_collections.sh
#    Creates 7 Qdrant collections (consciousness, episodes, embeddings, etc.)
#    Time: 2-3 min
#
# 2️⃣ 02_train_embeddings.sh
#    Trains 44k code vectors with GPU acceleration
#    Indexes: src/, tests/, scripts/, config/, docs/
#    Time: 10-15 min
#
# 3️⃣ 03_run_integration_cycles.sh
#    Executes 500 integration cycles with quantum stimulation
#    Stimulation: Expectation (1-250) + Imagination (251-500)
#    Time: 10-15 min
#    Output: Cycle reports + Φ metrics
#
# 4️⃣ 04_init_persistent_state.sh
#    Consolidates 1155+ cycle files into persistent_homology.json
#    Creates: persistent_homology.json + phi_computation_trace.json
#    Time: 2-3 min
#
# 5️⃣ 05_fix_gpu_allocation.sh
#    Moves embedding tensors to GPU (.to("cuda"))
#    Changes VRAM allocation from 0% → 30-40%
#    Time: 1 min
#
# 6️⃣ 06_increase_daemon_logging.sh
#    Shows cycle execution in logs (currently silent but working)
#    Creates: logs/daemon_cycles.log + logging config
#    Time: 1 min

# 🎯 EXPECTED RESULTS AFTER RECOVERY:
# ════════════════════════════════════════════════════════════════════
#
# ✅ GPU: 30-40% VRAM allocated (was 0%)
# ✅ Φ: Computing & visible 0.01-0.81 (was display bug showing 0.0)
# ✅ Cycles: 600+ including new training (was 99+ cached)
# ✅ Qdrant: 7 collections populated (was 1 collection)
# ✅ Daemon: Cycle execution logged (was silent)
# ✅ System: INTEGRADO & COMPUTING
#
# 📊 Files created:
#   - data/persistent_homology.json
#   - data/phi_computation_trace.json
#   - logs/daemon_cycles.log
#   - 600+ cycle reports in data/reports/modules/

# 🔍 MONITOR PROGRESS:
# ════════════════════════════════════════════════════════════════════
#
# GPU usage:
#   watch -n 2 'nvidia-smi | grep -E "Name|Memory|Utilization"'
#
# Cycle progress:
#   tail -f logs/daemon_cycles.log
#
# Qdrant vectors:
#   curl http://localhost:6333/collections/omnimind_embeddings | jq '.result.vectors_count'
#
# Φ values:
#   python -c "import json; d=json.load(open('data/phi_computation_trace.json')); print(f'Φ={d[\"phi_values\"][-1]:.4f}')"

# 🚨 REQUIREMENTS:
# ════════════════════════════════════════════════════════════════════
# ✅ Python 3.12.8
# ✅ Qdrant running (docker-compose up -d qdrant)
# ✅ GPU drivers installed (nvidia-smi works)
# ✅ Project venv activated
#
# Check with:
#   python --version
#   nvidia-smi
#   curl http://localhost:6333/healthz

# 📚 FULL DOCUMENTATION:
# ════════════════════════════════════════════════════════════════════
# See: scripts/recovery/README.md

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🚀 OMNIMIND RECOVERY SCRIPTS - READY FOR EXECUTION"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Created 7 files:"
echo "   1. scripts/MASTER_RECOVERY_EXECUTOR.sh (main orchestrator)"
echo "   2. scripts/recovery/01_init_qdrant_collections.sh"
echo "   3. scripts/recovery/02_train_embeddings.sh"
echo "   4. scripts/recovery/03_run_integration_cycles.sh"
echo "   5. scripts/recovery/04_init_persistent_state.sh"
echo "   6. scripts/recovery/05_fix_gpu_allocation.sh"
echo "   7. scripts/recovery/06_increase_daemon_logging.sh"
echo "   8. scripts/recovery/README.md (full documentation)"
echo ""
echo "📋 QUICK START:"
echo "   bash scripts/MASTER_RECOVERY_EXECUTOR.sh"
echo ""
echo "⏱️  Estimated time: 30-45 minutes"
echo ""
echo "📚 Read more: scripts/recovery/README.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
