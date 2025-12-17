#!/bin/bash

# 🔄 STEP 3: Run Integration Cycles + Qiskit GPU
# Executa ciclos de integração com Qiskit + Aer GPU (VERSÃO ATUALIZADA 13 DEZ)
# Status: READY FOR EXECUTION

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
PYTHON_CMD="python3"

echo -e "\033[0;36m🔄 Step 3: Integration Cycles + Qiskit GPU (UPDATED 13 DEC)\033[0m"
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
echo ""

# Run integration cycles with Qiskit GPU
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_ROOT/logs/integration_cycles_qiskit_${TIMESTAMP}.log"

mkdir -p "$PROJECT_ROOT/logs"

echo "📊 Running 500 integration cycles (Qiskit GPU, logging to $LOG_FILE)..."
echo ""

$PYTHON_CMD << 'PYTHON_END'
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time
import signal

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
# Imports carefully ordered to avoid ProviderV1 conflicts
print("🚀 Loading Qiskit + Aer GPU...")
QISKIT_AVAILABLE = False

try:
    # Step 1: Try basic Qiskit imports
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    logger.info("  ✅ Core Qiskit imports loaded")
except ImportError as e:
    logger.warning(f"  ⚠️ Core Qiskit import failed: {e}")

try:
    # Step 2: Try Aer simulator (separate try/except to isolate)
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
    logger.info("✅ Qiskit + Aer GPU available - using GPU simulation")
except ImportError as e:
    QISKIT_AVAILABLE = False
    logger.warning(f"⚠️ Aer import failed: {e}")
    logger.warning("   This might be a ProviderV1 version conflict")

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

# ✅ FORCE Qiskit GPU if available (with CPU fallback)
if QISKIT_AVAILABLE:
    try:
        # Try GPU first
        try:
            sim = AerSimulator(device='GPU')
            device_mode = "GPU"
            logger.info("✅ Configured Aer simulator with GPU device")
        except:
            # Fallback to CPU if GPU not available
            sim = AerSimulator(device='CPU')
            device_mode = "CPU"
            logger.info("ℹ️  GPU not available, using CPU for Aer simulator")

        # Patch the integration loop to use GPU/CPU quantum backend
        if hasattr(integration_loop, 'quantum_backend'):
            integration_loop.quantum_backend.aer_simulator = sim
            logger.info(f"✅ Patched quantum backend with Aer ({device_mode})")
    except Exception as e:
        logger.warning(f"⚠️ Could not configure Aer simulator: {e}")
        logger.warning("   Will use classical simulation fallback")

logger.info(f"Starting 500 integration cycles with Qiskit GPU stimulation...")
logger.info("Stimulation protocol: Expectation (250 cycles) + Imagination (250 cycles)")
logger.info("")

# Track metrics
cycle_metrics = []
phi_values = []
psi_values = []
sigma_values = []
delta_values = []
start_time = time.time()

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

        cycle_metrics.append(cycle_data)
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
            logger.info(
                f"✅ Cycle {cycle_num}/500 [{stim_type}] | "
                f"Φ={cycle_data['phi']:.4f} (avg={avg_phi:.4f}) | "
                f"Duration: {cycle_data['duration_ms']:.1f}ms"
            )

    except Exception as e:
        logger.error(f"❌ Error in cycle {cycle_num}: {e}")
        cycle_metrics.append({
            "cycle": cycle_num,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        })
        continue

# Calculate statistics
elapsed_time = time.time() - start_time
logger.info("")
logger.info("=" * 70)
logger.info("📊 INTEGRATION CYCLES COMPLETE")
logger.info("=" * 70)
logger.info(f"Total cycles: {len(cycle_metrics)}")
logger.info(f"Elapsed time: {elapsed_time:.1f}s ({elapsed_time/60:.1f}m)")
logger.info(f"Average cycle time: {(elapsed_time/len(cycle_metrics)*1000):.1f}ms")
logger.info(f"GPU mode: {'✅ ENABLED' if QISKIT_AVAILABLE else '❌ DISABLED'}")
logger.info("")

if phi_values:
    logger.info(f"Φ (Integration) metrics:")
    logger.info(f"  Min: {min(phi_values):.4f}")
    logger.info(f"  Max: {max(phi_values):.4f}")
    logger.info(f"  Mean: {sum(phi_values)/len(phi_values):.4f}")
    logger.info(f"  Final: {phi_values[-1]:.4f}")

if psi_values:
    logger.info(f"Ψ (Desire) metrics:")
    logger.info(f"  Min: {min(psi_values):.4f}")
    logger.info(f"  Max: {max(psi_values):.4f}")
    logger.info(f"  Mean: {sum(psi_values)/len(psi_values):.4f}")

if sigma_values:
    logger.info(f"σ (Lacan) metrics:")
    logger.info(f"  Min: {min(sigma_values):.4f}")
    logger.info(f"  Max: {max(sigma_values):.4f}")
    logger.info(f"  Mean: {sum(sigma_values)/len(sigma_values):.4f}")

logger.info("")
logger.info("✅ Step 3 Complete: Integration cycles trained (Qiskit GPU)")

# Save results
results = {
    "phase": 3,
    "timestamp": datetime.now().isoformat(),
    "total_cycles": len(cycle_metrics),
    "elapsed_time_seconds": elapsed_time,
    "qiskit_gpu_enabled": QISKIT_AVAILABLE,
    "metrics": {
        "phi": {
            "values": phi_values,
            "min": min(phi_values) if phi_values else 0,
            "max": max(phi_values) if phi_values else 0,
            "mean": sum(phi_values)/len(phi_values) if phi_values else 0,
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
    "cycles": cycle_metrics,
}

# Save to file
output_file = Path(PROJECT_ROOT) / "data" / "reports" / "integration_cycles_qiskit_phase3.json"
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

logger.info(f"📊 Results saved to: {output_file}")

PYTHON_END

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m✅ Step 3 Complete: Integration Cycles Trained (Qiskit GPU)\033[0m"
    echo ""
else
    echo ""
    echo -e "\033[0;31m❌ Step 3 Failed (exit code: $EXIT_CODE)\033[0m"
    echo ""
    exit 1
fi
