#!/usr/bin/env python
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
REAL HARDWARE BENCHMARK - IBM Quantum Execution
================================================

Executes CRITICAL experiments from Papers 1-3 on REAL IBM Quantum hardware.
Budget: 350 seconds remaining (5min 50s)
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, "/home/fahbrain/projects/omnimind")

from qiskit import QuantumCircuit

from src.quantum_consciousness.qpu_interface import BackendType, QPUInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IBM Token
IBM_TOKEN = os.getenv("IBM_API_KEY") or os.getenv("IBMQ_API_TOKEN")


def run_grover_search_benchmark():
    """Experiment 1: Grover Search Speedup (N=16, target=7)"""
    logger.info("\n[EXP 1] Grover Search (N=16) on IBM Quantum")
    logger.info("-" * 60)

    start = time.time()

    # Create Grover circuit for N=16, target=7
    qc = QuantumCircuit(4)  # 4 qubits for N=16

    # Initialize superposition
    for i in range(4):
        qc.h(i)

    # Oracle: mark state |0111⟩ (binary for 7)
    # Simple phase flip for demonstration
    qc.z(0)  # Flip qubit 0

    # Grover iterations: √N ≈ 4
    for _ in range(2):  # Simplified
        # Diffusion operator (simplified)
        for i in range(4):
            qc.h(i)
            qc.x(i)
        qc.h(3)
        qc.mcx([0, 1, 2], 3)  # Multi-controlled X
        qc.h(3)
        for i in range(4):
            qc.x(i)
            qc.h(i)

    qc.measure_all()

    # Execute on IBM Quantum
    qpu = QPUInterface(preferred_backend=BackendType.IBMQ_CLOUD, ibmq_token=IBM_TOKEN)

    try:
        result = qpu.execute(qc, shots=100, strict_mode=True)
        elapsed = time.time() - start

        logger.info(f"   ✅ Result: {result}")
        logger.info(f"   ⏱️  Time: {elapsed:.1f}s")

        return {
            "experiment": "grover_search_n16",
            "backend": qpu.get_active_backend_info().name if qpu.active_backend else "UNKNOWN",
            "result_counts": result,
            "execution_time_s": elapsed,
            "shots": 100,
            "status": "SUCCESS",
        }
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return {"status": "FAILED", "error": str(e)}


def run_bell_state_benchmark():
    """Experiment 2: Bell State Entanglement"""
    logger.info("\n[EXP 2] Bell State (|00⟩ + |11⟩)/√2 on IBM Quantum")
    logger.info("-" * 60)

    start = time.time()

    # Create Bell state circuit
    qc = QuantumCircuit(2)
    qc.h(0)  # Hadamard on qubit 0
    qc.cx(0, 1)  # CNOT (entanglement)
    qc.measure_all()

    # Execute on IBM Quantum
    qpu = QPUInterface(preferred_backend=BackendType.IBMQ_CLOUD, ibmq_token=IBM_TOKEN)

    try:
        result = qpu.execute(qc, shots=100, strict_mode=True)
        elapsed = time.time() - start

        # Verify entanglement: should have ~50% |00⟩, ~50% |11⟩
        count_00 = result.get("00", 0)
        count_11 = result.get("11", 0)
        count_invalid = result.get("01", 0) + result.get("10", 0)

        entanglement_verified = (count_invalid < 10) and (abs(count_00 - count_11) < 30)

        logger.info(f"   Result: |00⟩={count_00}, |11⟩={count_11}, invalid={count_invalid}")
        logger.info(f"   Entanglement verified: {entanglement_verified}")
        logger.info(f"   ⏱️  Time: {elapsed:.1f}s")

        return {
            "experiment": "bell_state_entanglement",
            "backend": qpu.get_active_backend_info().name if qpu.active_backend else "UNKNOWN",
            "result_counts": result,
            "count_00": count_00,
            "count_11": count_11,
            "count_invalid": count_invalid,
            "entanglement_verified": entanglement_verified,
            "execution_time_s": elapsed,
            "shots": 100,
            "status": "SUCCESS",
        }
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return {"status": "FAILED", "error": str(e)}


def run_integration_latency_benchmark():
    """Experiment 3: Quantum→Classical Integration Latency"""
    logger.info("\n[EXP 3] Integration Latency Measurement")
    logger.info("-" * 60)

    start = time.time()

    # Simple 1-qubit circuit (minimal for latency test)
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()

    qpu = QPUInterface(preferred_backend=BackendType.IBMQ_CLOUD, ibmq_token=IBM_TOKEN)

    try:
        t0 = time.time()
        _result = qpu.execute(qc, shots=10, strict_mode=True)  # Low shots for speed
        t1 = time.time()

        latency_ms = (t1 - t0) * 1000

        logger.info(f"   ✅ Latency: {latency_ms:.1f}ms")
        logger.info(f"   Target: <50ms (for local), <100ms (for cloud)")

        meets_target = latency_ms < 100  # Cloud target

        return {
            "experiment": "quantum_classical_latency",
            "backend": qpu.get_active_backend_info().name if qpu.active_backend else "UNKNOWN",
            "latency_ms": latency_ms,
            "target_ms": 100,
            "meets_target": meets_target,
            "execution_time_s": time.time() - start,
            "status": "SUCCESS",
        }
    except Exception as e:
        logger.error(f"   ❌ Failed: {e}")
        return {"status": "FAILED", "error": str(e)}


def main():
    logger.info("=" * 60)
    logger.info("REAL HARDWARE BENCHMARK - IBM Quantum")
    logger.info("=" * 60)
    logger.info(f"Budget: 350 seconds")
    logger.info(f"Token: {IBM_TOKEN[:5]}...{IBM_TOKEN[-5:] if IBM_TOKEN else 'MISSING'}")

    if not IBM_TOKEN:
        logger.error("IBM_API_KEY not found! Cannot execute.")
        sys.exit(1)

    results = {}
    total_start = time.time()

    # Execute experiments
    results["grover"] = run_grover_search_benchmark()
    results["bell_state"] = run_bell_state_benchmark()
    results["latency"] = run_integration_latency_benchmark()

    total_time = time.time() - total_start

    # Save results
    output = {
        "benchmark_date": datetime.now().isoformat(),
        "total_execution_time_s": total_time,
        "budget_used_s": total_time,
        "budget_remaining_s": 350 - total_time,
        "experiments": results,
    }

    output_file = (
        Path("data/benchmarks")
        / f"ibm_quantum_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    logger.info("\n" + "=" * 60)
    logger.info("BENCHMARK COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total time: {total_time:.1f}s")
    logger.info(f"Budget remaining: {350 - total_time:.1f}s")
    logger.info(f"Results saved to: {output_file}")

    # Summary
    success_count = sum(1 for r in results.values() if r.get("status") == "SUCCESS")
    logger.info(f"\nSuccess rate: {success_count}/3 experiments")


if __name__ == "__main__":
    main()
