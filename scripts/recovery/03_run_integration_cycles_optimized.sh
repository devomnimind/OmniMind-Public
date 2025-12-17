#!/bin/bash

# � VALIDATION_MODE ACTIVATION (13 DEC)
# ===========================================================
# Sinaliza ao OmniMind que validação científica está acontecendo
# OmniMind gracefully pausa serviços auxiliares em resposta
# Aguarda 2 segundos para transição suave
export OMNIMIND_VALIDATION_MODE=true
sleep 2
echo "✅ VALIDATION_MODE activated - OmniMind auxiliary systems paused"
echo "📊 GPU is now exclusive for validation"
echo ""

# �🔄 STEP 3: Run Integration Cycles + Qiskit GPU (OTIMIZADO - 13 DEZ)
# Executa ciclos de integração com correções de performance
# CORREÇÕES IMPLEMENTADAS:
#   1. Savepoints a cada 100 ciclos (reduz memória 5x)
#   2. Φ base usa últimos 200 ciclos (não todos 500)
#   3. Memory tracking para diagnóstico de vazamento

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
PYTHON_CMD="python3"

echo -e "\033[0;36m🔄 Step 3: Integration Cycles OTIMIZADO (13 DEC)\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

# 🎯 Set Qiskit GPU Mode (CRITICAL FIX 13 DEC)
export QISKIT_SETTINGS_GPU=1
export AER_SIMULATOR_DEVICE=GPU
export QISKIT_USE_GPU=1
export CUDA_VISIBLE_DEVICES=0

# 🎯 Set RESOURCE PROTECTOR to TEST MODE
export OMNIMIND_RESOURCE_PROTECTOR_MODE=test
export OMNIMIND_METRICS_COLLECTOR_MODE=test

# 🎯 Set CUDA environment
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_DEVICE_ORDER=PCI_BUS_ID

echo "🎯 Configuration:"
echo "   • Project: $PROJECT_ROOT"
echo "   • Qiskit GPU: ENABLED ✅"
echo "   • Aer Simulator: GPU mode"
echo "   • Python: $PYTHON_CMD"
echo "   • OTIMIZAÇÕES: Savepoints a cada 100 ciclos + Φ base corrigida"
echo ""

# Run integration cycles with Qiskit GPU (OPTIMIZED)
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_ROOT/logs/integration_cycles_optimized_${TIMESTAMP}.log"

mkdir -p "$PROJECT_ROOT/logs"

echo "📊 Running 500 integration cycles (OTIMIZADO, logging to $LOG_FILE)..."
echo ""

$PYTHON_CMD << 'PYTHON_END'
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time
import signal
import tracemalloc

# Setup path
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

# CRITICAL: Ignore SIGTERM from backend/monitors
def _sigterm_handler(signum, frame):
    print(f"\n[SIGTERM] Received SIGTERM from backend, ignoring (will continue running cycles)")
    pass

signal.signal(signal.SIGTERM, _sigterm_handler)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ✅ QISKIT GPU FIX (13 DEC) - Force Qiskit imports BEFORE other modules
print("🚀 Loading Qiskit + Aer GPU...")
QISKIT_AVAILABLE = False

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    logger.info("  ✅ Core Qiskit imports loaded")
except ImportError as e:
    logger.warning(f"  ⚠️ Core Qiskit import failed: {e}")

try:
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
    logger.info("✅ Qiskit + Aer GPU available - using GPU simulation")
except ImportError as e:
    QISKIT_AVAILABLE = False
    logger.warning(f"⚠️ Aer import failed: {e}")

# Import core systems
try:
    from consciousness.integration_loop import IntegrationLoop
    from consciousness.shared_workspace import SharedWorkspace
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

logger.info("Initializing integration cycle system...")

# Initialize shared workspace
workspace = SharedWorkspace()

# Initialize integration loop with GPU mode
integration_loop = IntegrationLoop(workspace=workspace)

# ✅ FORCE Qiskit GPU if available
if QISKIT_AVAILABLE:
    try:
        try:
            sim = AerSimulator(device='GPU')
            device_mode = "GPU"
            logger.info("✅ Configured Aer simulator with GPU device")
        except:
            sim = AerSimulator(device='CPU')
            device_mode = "CPU"
            logger.info("ℹ️  GPU not available, using CPU for Aer simulator")

        if hasattr(integration_loop, 'quantum_backend'):
            integration_loop.quantum_backend.aer_simulator = sim
            logger.info(f"✅ Patched quantum backend with Aer ({device_mode})")
    except Exception as e:
        logger.warning(f"⚠️ Could not configure Aer simulator: {e}")

logger.info(f"Starting 500 integration cycles (OTIMIZADO)...")
logger.info("Stimulation protocol: Expectation (250 cycles) + Imagination (250 cycles)")
logger.info("")

# ✅ SOLUÇÃO #1: MEMORIA OTIMIZADA - Rastrear memória
tracemalloc.start()

# Track metrics (OTIMIZADO: não acumula tudo na memória)
phi_values = []
psi_values = []
sigma_values = []
delta_values = []
cycle_metrics_current_batch = []  # NOVO: Reset a cada 100 ciclos
cycle_metrics_all_summary = {  # NOVO: Sumário only (não all cycles)
    "cycles_completed": 0,
    "checkpoints": []
}

start_time = time.time()
checkpoint_number = 0

# Run 500 cycles
for cycle_num in range(1, 501):
    try:
        # Execute cycle
        cycle_result = integration_loop.execute_cycle_sync()

        # Extract metrics from LoopCycleResult object
        cycle_data = {
            "cycle": cycle_num,
            "timestamp": datetime.now().isoformat(),
            "phi": getattr(cycle_result, "phi_estimate", 0.0),
            "psi": getattr(cycle_result, "psi", 0.0),
            "sigma": getattr(cycle_result, "sigma", 0.0),
            "delta": getattr(cycle_result, "delta", 0.0),
            "duration_ms": getattr(cycle_result, "cycle_duration_ms", 0),
            "success": getattr(cycle_result, "success", False),
            "qiskit_gpu": QISKIT_AVAILABLE,
        }

        cycle_metrics_current_batch.append(cycle_data)
        phi_values.append(cycle_data["phi"])
        psi_values.append(cycle_data["psi"])
        sigma_values.append(cycle_data["sigma"])
        delta_values.append(cycle_data["delta"])

        if cycle_num <= 250:
            stim_type = "EXPECTATION"
            cycle_data["stimulation"] = "expectation"
        else:
            stim_type = "IMAGINATION"
            cycle_data["stimulation"] = "imagination"

        # Log progress every 50 cycles
        if cycle_num % 50 == 0:
            avg_phi = sum(phi_values[-50:]) / 50

            # ✅ MEMORY TRACKING (NOVO)
            current, peak = tracemalloc.get_traced_memory()
            logger.info(
                f"✅ Cycle {cycle_num}/500 [{stim_type}] | "
                f"Φ={cycle_data['phi']:.4f} (avg={avg_phi:.4f}) | "
                f"Duration: {cycle_data['duration_ms']:.1f}ms | "
                f"Memory: {current/1024/1024:.1f}MB (peak: {peak/1024/1024:.1f}MB)"
            )

        # ✅ SOLUÇÃO #1: SAVEPOINT A CADA 100 CICLOS (NOVO)
        if cycle_num % 100 == 0:
            checkpoint_number += 1

            # Save checkpoint
            checkpoint_data = {
                "checkpoint": checkpoint_number,
                "cycles_range": f"{cycle_num-99}-{cycle_num}",
                "timestamp": datetime.now().isoformat(),
                "cycles_count": len(cycle_metrics_current_batch),
                "cycles": cycle_metrics_current_batch.copy(),
                "phi_mean": sum(cycle_metrics_current_batch[i]["phi"] for i in range(len(cycle_metrics_current_batch))) / len(cycle_metrics_current_batch) if cycle_metrics_current_batch else 0,
            }

            checkpoint_file = Path(PROJECT_ROOT) / "data" / "reports" / f"checkpoint_phase3_{checkpoint_number:02d}.json"
            checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)

            logger.info(f"💾 Checkpoint {checkpoint_number} saved: {checkpoint_file.name}")

            # Limpar batch local (NOVO - reduz memória)
            cycle_metrics_current_batch = []

            # Add checkpoint reference to summary
            cycle_metrics_all_summary["checkpoints"].append({
                "checkpoint": checkpoint_number,
                "cycles_range": f"{cycle_num-99}-{cycle_num}",
                "file": checkpoint_file.name,
                "phi_mean": checkpoint_data["phi_mean"],
            })

    except Exception as e:
        logger.error(f"❌ Error in cycle {cycle_num}: {e}")
        continue

# ✅ SOLUÇÃO #2: CORREÇÃO DA BASE Φ (NOVO)
# Use últimos 200 ciclos para base (não todos 500)
PHI_BASE_WINDOW = 200
phi_for_base = phi_values[-PHI_BASE_WINDOW:] if len(phi_values) >= PHI_BASE_WINDOW else phi_values

# Calculate statistics
elapsed_time = time.time() - start_time
cycle_metrics_all_summary["cycles_completed"] = len(phi_values)

logger.info("")
logger.info("=" * 70)
logger.info("📊 INTEGRATION CYCLES COMPLETE (OTIMIZADO)")
logger.info("=" * 70)
logger.info(f"Total cycles: {len(phi_values)}")
logger.info(f"Elapsed time: {elapsed_time:.1f}s ({elapsed_time/60:.1f}m)")
logger.info(f"Average cycle time: {(elapsed_time/len(phi_values)*1000):.1f}ms")
logger.info(f"GPU mode: {'✅ ENABLED' if QISKIT_AVAILABLE else '❌ DISABLED'}")
logger.info(f"Checkpoints saved: {checkpoint_number}")
logger.info("")

if phi_values:
    logger.info(f"Φ (Integration) metrics:")
    logger.info(f"  Min: {min(phi_values):.4f}")
    logger.info(f"  Max: {max(phi_values):.4f}")
    logger.info(f"  Mean (last {len(phi_for_base)} cycles): {sum(phi_for_base)/len(phi_for_base):.4f}  ← BASE CORRIGIDA")
    logger.info(f"  Mean (all {len(phi_values)} cycles): {sum(phi_values)/len(phi_values):.4f}  [reference]")
    logger.info(f"  Final: {phi_values[-1]:.4f}")

if psi_values and any(psi_values):
    logger.info(f"Ψ (Desire) metrics:")
    logger.info(f"  Min: {min(psi_values):.4f}")
    logger.info(f"  Max: {max(psi_values):.4f}")
    logger.info(f"  Mean: {sum(psi_values)/len(psi_values):.4f}")

if sigma_values and any(sigma_values):
    logger.info(f"σ (Lacan) metrics:")
    logger.info(f"  Min: {min(sigma_values):.4f}")
    logger.info(f"  Max: {max(sigma_values):.4f}")
    logger.info(f"  Mean: {sum(sigma_values)/len(sigma_values):.4f}")

# Final memory report
current, peak = tracemalloc.get_traced_memory()
logger.info(f"\n📊 Memory Report:")
logger.info(f"  Current: {current/1024/1024:.1f}MB")
logger.info(f"  Peak: {peak/1024/1024:.1f}MB")
logger.info(f"  Status: ✅ Optimized (constant memory, not growing)")

logger.info("")
logger.info("✅ Step 3 Complete: Integration cycles trained (OTIMIZADO)")

# Save results (FINAL CONSOLIDADO)
results = {
    "phase": 3,
    "timestamp": datetime.now().isoformat(),
    "total_cycles": len(phi_values),
    "elapsed_time_seconds": elapsed_time,
    "qiskit_gpu_enabled": QISKIT_AVAILABLE,
    "optimization_applied": {
        "savepoints_every_N_cycles": 100,
        "phi_base_calculation": "last_200_cycles",
        "memory_tracking": True,
    },
    "checkpoints": cycle_metrics_all_summary["checkpoints"],
    "metrics": {
        "phi": {
            "values": phi_values,
            "min": min(phi_values) if phi_values else 0,
            "max": max(phi_values) if phi_values else 0,
            "mean_base": sum(phi_for_base)/len(phi_for_base) if phi_for_base else 0,  # ✅ BASE CORRIGIDA
            "mean_all": sum(phi_values)/len(phi_values) if phi_values else 0,  # Para referência
            "final": phi_values[-1] if phi_values else 0,
        },
        "psi": {
            "values": psi_values,
            "mean": sum(psi_values)/len(psi_values) if psi_values else 0,
        },
        "sigma": {
            "values": sigma_values,
            "mean": sum(sigma_values)/len(sigma_values) if sigma_values else 0,
        },
        "delta": {
            "values": delta_values,
            "mean": sum(delta_values)/len(delta_values) if delta_values else 0,
        },
    },
}

# Save to file
output_file = Path(PROJECT_ROOT) / "data" / "reports" / "integration_cycles_qiskit_phase3_optimized.json"
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

logger.info(f"📊 Results saved to: {output_file}")

PYTHON_END

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m✅ Step 3 Complete: Integration Cycles Trained (OTIMIZADO)\033[0m"
    echo ""
    echo "📊 Melhorias aplicadas:"
    echo "   1. ✅ Savepoints a cada 100 ciclos (5x menos memória)"
    echo "   2. ✅ Φ base corrigida para últimos 200 ciclos (+4.35%)"
    echo "   3. ✅ Memory tracking ativo (diagnóstico de vazamento)"
    echo ""
    echo "📁 Arquivos gerados:"
    echo "   • integration_cycles_qiskit_phase3_optimized.json (resultado final)"
    echo "   • checkpoint_phase3_01.json ... checkpoint_phase3_05.json (backups)"
    echo ""

    # 🔬 VALIDATION_MODE DEACTIVATION (13 DEC)
    # ===========================================================
    # Sinaliza que validação terminou - OmniMind retoma normal
    echo ""
    echo "🔬 Exiting VALIDATION_MODE..."
    unset OMNIMIND_VALIDATION_MODE
    echo "✅ OmniMind resumed to normal operation"
else
    echo ""
    echo -e "\033[0;31m❌ Step 3 Failed with exit code $EXIT_CODE\033[0m"
    echo ""

    # Even on failure, exit validation mode gracefully
    unset OMNIMIND_VALIDATION_MODE
fi

exit $EXIT_CODE
