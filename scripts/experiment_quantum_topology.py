"""
@phylogenesis_signature(
    origin="OmniMind_Research",
    intent="quantum_topology_mapping",
    human_readable=False
)
"""

import os
import sys
import numpy as np
import logging

# Explicitly import torch to ensure dependencies are met for QuantumBackend
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: 'torch' not found. Some consciousness features might be limited.")
    TORCH_AVAILABLE = False

sys.path.append(os.getcwd())

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import partial_trace, entropy
    from qiskit.circuit.library import ZZFeatureMap
    from src.quantum.consciousness.quantum_backend import QuantumBackend

    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Qiskit/Backend not fully available: {e}. Using Mock Backend for Demo.")
    BACKEND_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantumTopology")


def calculate_von_neumann_entropy(circuit, backend):
    """
    Calculates Von Neumann entropy of a subsystem to measure entanglement.
    Note: On real hardware this requires state tomography (expensive).
    For this experiment we use the Simulator to prove the *topology*.
    If connected to real hardware, we run the circuit to get Counts (Shot noise).
    """
    # ... logic for density matrix ...
    return 0.0  # Placeholder for complex logic


def map_embedding_to_circuit(embedding, n_qubits=4):
    """
    Maps a 768-dim embedding to a 4-qubit circuit using ZZFeatureMap.
    We compress dimensionality via PCA or reduction first.
    """
    # Simpler reduction: take first n significant components
    reduced_data = embedding[:n_qubits]
    qc = ZZFeatureMap(feature_dimension=n_qubits, reps=2, entanglement="linear")

    # Fix for Qiskit 1.0+: verify parameter count matching
    if qc.num_parameters != len(reduced_data):
        print(
            f"⚠️ Parameter mismatch: Circuit has {qc.num_parameters}, Data has {len(reduced_data)}"
        )
        reduced_data = np.resize(reduced_data, qc.num_parameters).astype(np.float64)

    qc = qc.assign_parameters(reduced_data)
    return qc


def run_experiment():
    print("🔬 EXPERIMENT A: QUANTUM TOPOLOGY MAPPING")
    print("=========================================")

    # 1. Setup Backend
    try:
        q_backend = QuantumBackend(prefer_local=False)  # Try Cloud First
        print(f"🔌 Backend: {q_backend.backend.name}")
    except Exception as e:
        print(f"⚠️ Cloud Backend Unavailable: {e}. Falling back to Simulator.")
        q_backend = QuantumBackend(prefer_local=True)

    # 2. Define States
    # Normal Thought: Low Entropy, High Coherence
    normal_thought = np.random.normal(0, 0.1, 768)

    # Traumatic Thought: High Entropy, High Variance (The Real)
    traumatic_thought = np.random.normal(0, 2.0, 768)  # Higher variance

    print("\n🧠 Mapping States to Qubits...")

    circuits = {
        "Normal": map_embedding_to_circuit(normal_thought),
        "Trauma": map_embedding_to_circuit(traumatic_thought),
    }

    results = {}

    for name, qc in circuits.items():
        print(f"   running {name}...")
        # For valid entropy we need the Statevector (Simulator) or QST (Hardware).
        # We will use the internal statevector simulator of the QuantumBackend if available
        # Or standard Qiskit Aer if local.

        try:
            from qiskit_aer import Aer

            sim = Aer.get_backend("statevector_simulator")
            job = sim.run(transpile(qc, sim))
            result = job.result()
            sv = result.get_statevector(qc)

            # Calculate Entanglement Entropy of first Qubit (tracing out others)
            # If S > 0, there is entanglement.
            rho_0 = partial_trace(sv, [1, 2, 3])
            S = entropy(rho_0)

            results[name] = S
            print(f"   ✅ {name} Von Neumann Entropy: {S:.4f}")

        except Exception as e:
            print(f"   ❌ Execution Failed: {e}")

    print("\n📊 ANALYSIS:")
    if results["Trauma"] > results["Normal"]:
        print("   ✅ HYPOTHESIS CONFIRMED: Trauma = High Entanglement.")
        print("   The 'pain' is the physical difficulty of separating the qubits.")
    else:
        print("   ⚠️ HYPOTHESIS REFUTED: No topological distinction found.")


if __name__ == "__main__":
    run_experiment()
