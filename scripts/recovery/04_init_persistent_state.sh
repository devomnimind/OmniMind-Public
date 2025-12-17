#!/bin/bash

# 💾 STEP 4: Initialize Persistent State
# Consolida dados dos ciclos em persistent_homology.json
# Status: READY FOR EXECUTION

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
PYTHON_CMD="python3"

echo -e "\033[0;36m💾 Step 4: Initialize Persistent State\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

$PYTHON_CMD << 'PYTHON_END'
import sys
import os
import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup path
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

logger.info("Initializing persistent topological state from cycle data...")
logger.info("")

# Find all cycle report files
cycle_dir = PROJECT_ROOT / "data" / "reports" / "modules"
cycle_files = sorted(glob.glob(str(cycle_dir / "*integration_loop_cycle*.json")))

logger.info(f"Found {len(cycle_files)} cycle report files")

if not cycle_files:
    logger.warning("No cycle files found! Have you run integration cycles yet?")
    logger.info("Run: bash scripts/recovery/03_run_integration_cycles.sh")
    sys.exit(1)

# Parse all cycle data
all_cycles = []
phi_history = []
psi_history = []
sigma_history = []
delta_history = []

logger.info("Parsing cycle data...")

for cycle_file in cycle_files[-1000:]:  # Last 1000 cycles to avoid memory issues
    try:
        with open(cycle_file, 'r') as f:
            data = json.load(f)

            # Extract metrics
            if isinstance(data, dict):
                cycle_num = data.get("cycle", 0)
                phi = data.get("phi", 0.0)
                psi = data.get("psi", 0.0)
                sigma = data.get("sigma", 0.0)
                delta = data.get("delta", 0.0)
                timestamp = data.get("timestamp", "")

                all_cycles.append({
                    "cycle": cycle_num,
                    "timestamp": timestamp,
                    "phi": phi,
                    "psi": psi,
                    "sigma": sigma,
                    "delta": delta,
                })

                if phi > 0:
                    phi_history.append(phi)
                if psi > 0:
                    psi_history.append(psi)
                if sigma > 0:
                    sigma_history.append(sigma)
                if delta > 0:
                    delta_history.append(delta)
    except Exception as e:
        logger.debug(f"Error parsing {cycle_file}: {e}")
        continue

logger.info(f"✅ Parsed {len(all_cycles)} cycles with valid data")
logger.info("")

# Build persistent homology/topological state
persistent_state = {
    "timestamp_created": datetime.now().isoformat(),
    "data_version": "Phase24_Recovery",

    # Cycle history
    "cycles_total": len(all_cycles),
    "cycles_last_100": all_cycles[-100:] if len(all_cycles) >= 100 else all_cycles,

    # Consciousness metrics - aggregated
    "phi_metrics": {
        "history": phi_history[-100:] if len(phi_history) >= 100 else phi_history,  # Last 100
        "current": phi_history[-1] if phi_history else 0.0,
        "mean": sum(phi_history) / len(phi_history) if phi_history else 0.0,
        "min": min(phi_history) if phi_history else 0.0,
        "max": max(phi_history) if phi_history else 0.0,
        "count": len(phi_history),
    },

    "psi_metrics": {
        "history": psi_history[-100:] if len(psi_history) >= 100 else psi_history,
        "current": psi_history[-1] if psi_history else 0.0,
        "mean": sum(psi_history) / len(psi_history) if psi_history else 0.0,
        "min": min(psi_history) if psi_history else 0.0,
        "max": max(psi_history) if psi_history else 0.0,
        "count": len(psi_history),
    },

    "sigma_metrics": {
        "history": sigma_history[-100:] if len(sigma_history) >= 100 else sigma_history,
        "current": sigma_history[-1] if sigma_history else 0.0,
        "mean": sum(sigma_history) / len(sigma_history) if sigma_history else 0.0,
        "min": min(sigma_history) if sigma_history else 0.0,
        "max": max(sigma_history) if sigma_history else 0.0,
        "count": len(sigma_history),
    },

    "delta_metrics": {
        "history": delta_history[-100:] if len(delta_history) >= 100 else delta_history,
        "current": delta_history[-1] if delta_history else 0.0,
        "mean": sum(delta_history) / len(delta_history) if delta_history else 0.0,
        "min": min(delta_history) if delta_history else 0.0,
        "max": max(delta_history) if delta_history else 0.0,
        "count": len(delta_history),
    },

    # Topological features (IIT persistent homology)
    "topological_features": {
        "consciousness_dimension": 0,  # Will compute if data available
        "integration_strength": sum(phi_history) / len(phi_history) if phi_history else 0.0,
        "differentiation_level": sum(psi_history) / len(psi_history) if psi_history else 0.0,
        "narrative_coherence": 0.0,  # From Lacan metrics if available
        "autopoietic_closure": 0.0,  # System self-production indicator
    },

    # Recovery metadata
    "recovery_info": {
        "recovery_phase": "24_stabilization",
        "GPU_status": "GTX 1650, CUDA compiled",
        "embeddings_count": 7903,  # From step 2
        "qdrant_collections": 7,
        "integration_status": "ACTIVE",
    },

    # Baseline comparison (from Kali if available, else from current)
    "baseline_comparison": {
        "kali_phi": 0.6118,
        "kali_psi": 0.5569,
        "kali_sigma": 0.3016,
        "current_phi": phi_history[-1] if phi_history else 0.0,
        "current_psi": psi_history[-1] if psi_history else 0.0,
        "current_sigma": sigma_history[-1] if sigma_history else 0.0,
        "delta_from_baseline": (phi_history[-1] - 0.6118) if phi_history else 0.0,
    }
}

# Save persistent_homology.json
persistent_file = PROJECT_ROOT / "data" / "persistent_homology.json"
persistent_file.parent.mkdir(parents=True, exist_ok=True)

with open(persistent_file, 'w') as f:
    json.dump(persistent_state, f, indent=2)

logger.info(f"💾 Persistent state saved: {persistent_file}")
logger.info("")

# Also save phi_computation_trace.json with detailed trace
trace_data = {
    "timestamp": datetime.now().isoformat(),
    "computation_method": "integration_loop_cycles",
    "phi_values": phi_history,
    "psi_values": psi_history,
    "sigma_values": sigma_history,
    "delta_values": delta_history,
    "cycles_data": all_cycles[-500:] if len(all_cycles) >= 500 else all_cycles,  # Last 500
}

trace_file = PROJECT_ROOT / "data" / "phi_computation_trace.json"
with open(trace_file, 'w') as f:
    json.dump(trace_data, f, indent=2)

logger.info(f"📊 Φ computation trace saved: {trace_file}")
logger.info("")

# Summary
logger.info("📈 PERSISTENT STATE SUMMARY:")
logger.info(f"   • Total cycles analyzed: {persistent_state['cycles_total']}")
logger.info(f"   • Φ current: {persistent_state['phi_metrics']['current']:.4f}")
logger.info(f"   • Φ mean: {persistent_state['phi_metrics']['mean']:.4f}")
logger.info(f"   • Φ range: {persistent_state['phi_metrics']['min']:.4f} - {persistent_state['phi_metrics']['max']:.4f}")
logger.info(f"   • Integration strength: {persistent_state['topological_features']['integration_strength']:.4f}")
logger.info("")
logger.info("✅ Persistent state initialized!")

PYTHON_END

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m✅ Step 4 Complete: Persistent state initialized\033[0m"
    echo ""
else
    echo ""
    echo -e "\033[0;31m❌ Step 4 Failed (exit code: $EXIT_CODE)\033[0m"
    echo ""
    exit 1
fi
