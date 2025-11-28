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

import os
import sys
import logging
from src.quantum_consciousness.quantum_backend import QuantumBackend
from src.quantum_consciousness.qpu_interface import QPUInterface, BackendType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantumValidator")


def validate_quantum_execution():
    print("=" * 50)
    print("QUANTUM EXECUTION VALIDATOR (STRICT MODE)")
    print("=" * 50)

    # Check for credentials
    ibm_token = os.getenv("IBM_API_KEY") or os.getenv("IBMQ_API_TOKEN")
    if not ibm_token:
        print("⚠️  WARNING: No IBM Quantum token found in environment.")
        print("    Real hardware execution cannot be validated.")
        print("    Set IBM_API_KEY or IBMQ_API_TOKEN to validate.")
    else:
        print(f"✅ IBM Token detected: {ibm_token[:5]}...{ibm_token[-5:]}")

    print("\n1. Testing QuantumBackend (High-Level API)")
    try:
        # Force IBM provider
        backend = QuantumBackend(provider="ibm", api_token=ibm_token)

        # Check what backend was actually initialized
        backend_name = backend.backend.__class__.__name__
        print(f"   Initialized Backend Class: {backend_name}")

        if ibm_token and "Aer" in backend_name and "IBMQBackend" not in backend_name:
            print("❌ FAILURE: Token provided but fallback to AerSimulator occurred!")
        elif ibm_token and "IBMQBackend" in backend_name:
            print("✅ SUCCESS: Real IBMQBackend initialized.")
        elif not ibm_token and "Aer" in backend_name:
            print("✅ SUCCESS: Correctly defaulted to Aer (No Token).")
        else:
            print(f"⚠️  UNCERTAIN: Backend is {backend_name}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n2. Testing QPUInterface (Low-Level API) with Strict Mode")
    try:
        qpu = QPUInterface(preferred_backend=BackendType.IBMQ_CLOUD, ibmq_token=ibm_token)

        active_info = qpu.get_active_backend_info()
        print(f"   Active Backend: {active_info.name} ({active_info.provider})")

        if ibm_token and active_info.backend_type != BackendType.IBMQ_CLOUD:
            print("❌ FAILURE: Preferred IBMQ but got something else.")

        # Create a simple circuit (Bell State)
        try:
            from qiskit import QuantumCircuit

            qc = QuantumCircuit(2)
            qc.h(0)
            qc.cx(0, 1)
            qc.measure_all()

            print("   Executing circuit (Strict Mode)...")
            # This should FAIL if connection is bad, NOT fallback
            result = qpu.execute(qc, shots=10, strict_mode=True)
            print(f"   Result: {result}")
            print("✅ SUCCESS: Execution completed without fallback.")

        except ImportError:
            print("⚠️  Qiskit not installed, skipping circuit execution.")
        except RuntimeError as e:
            if "Strict mode" in str(e):
                print(f"✅ SUCCESS: Strict mode correctly raised error on failure: {e}")
            else:
                print(f"❌ FAILURE: Unexpected error: {e}")
        except Exception as e:
            print(f"❌ FAILURE: Unexpected exception: {e}")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    validate_quantum_execution()
