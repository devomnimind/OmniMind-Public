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

import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.quantum_consciousness.qpu_interface import QPUInterface, BackendType
from qiskit import QuantumCircuit

load_dotenv()


def validate_bell_state_ibm():
    print("Connecting to IBM Quantum via QPUInterface...")
    token = (
        os.getenv("IBM_API_KEY") or os.getenv("IBMQ_API_TOKEN") or os.getenv("QUANTUM_API_TOKEN")
    )

    if not token:
        print("❌ Error: IBM Token not found")
        return

    # Initialize QPU Interface with IBMQ preference
    try:
        qpu = QPUInterface(preferred_backend=BackendType.IBMQ_CLOUD, ibmq_token=token)
    except Exception as e:
        print(f"❌ Failed to initialize QPUInterface: {e}")
        return

    # Check if we actually got the IBM backend
    active_info = qpu.get_active_backend_info()
    if not active_info:
        print("❌ No active backend")
        return

    print(f"Active Backend: {active_info.name} ({active_info.provider})")

    if active_info.provider != "IBM Quantum":
        print("⚠️ Warning: IBM Quantum not active. Checking availability...")
        if BackendType.IBMQ_CLOUD in qpu.backends:
            qpu.switch_backend(BackendType.IBMQ_CLOUD)
            print(f"Switched to: {qpu.get_active_backend_info().name}")
        else:
            print("❌ IBM Quantum backend not available in QPUInterface.")
            # List available for debug
            print("Available backends:")
            for b in qpu.list_backends():
                print(f" - {b.name} ({b.provider})")
            return

    # Circuit
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()

    print("Submitting job (shots=100)...")

    try:
        # Execute using the interface
        counts = qpu.execute(circuit, shots=100, strict_mode=True)
        print(f"Counts: {counts}")

        total = sum(counts.values())
        # QPUInterface returns counts dict, keys are binary strings
        state_00 = counts.get("00", 0)
        state_11 = counts.get("11", 0)
        score = (state_00 + state_11) / total

        print(f"IBM Quantum Bell State Results:")
        print(f"  |00⟩ + |11⟩ Score: {score:.1%}")

        if score > 0.85:
            print("✅ VALIDADO: Entanglement real")
        else:
            print(f"❌ FAILED: Score {score:.1%} < 85%")

    except Exception as e:
        print(f"❌ Job failed: {e}")


if __name__ == "__main__":
    validate_bell_state_ibm()
