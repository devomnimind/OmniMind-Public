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
Verify IBM Quantum Connection.

This script checks if the IBM Quantum account is accessible using the API key
from the environment variables and runs a simple Bell state experiment on a simulator.
"""

import os
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit

# Load environment variables
load_dotenv()


def verify_connection():
    api_key = os.getenv("IBM_API_KEY") or os.getenv("IBM_QUANTUM_TOKEN")

    if not api_key:
        print("❌ Error: IBM_API_KEY or IBM_QUANTUM_TOKEN not found in environment.")
        return

    print(f"🔑 Found API Key: {api_key[:4]}...{api_key[-4:]}")

    try:
        # Initialize Service
        # channel="ibm_quantum_platform" is for the standard IBM Quantum account
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
        print("✅ QiskitRuntimeService initialized successfully.")

        # List backends to verify access
        backends = service.backends()
        print(f"📋 Available backends: {[b.name for b in backends[:3]]}...")

        # Select a backend (simulator for speed/free tier)
        # ibm_brisbane is a real device, ibm_osaka, etc.
        # We try to find a simulator first, or the least busy real backend.
        backend = service.least_busy(operational=True, simulator=False)
        print(f"🖥️ Selected backend: {backend.name}")

        # Create a simple circuit (Bell State)
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        # Transpile circuit for target backend
        from qiskit import transpile

        qc_transpiled = transpile(qc, backend=backend, optimization_level=3)

        print("⚛️ Submitting job (Bell State)...")
        sampler = Sampler(mode=backend)
        job = sampler.run([qc_transpiled])
        print(f"🚀 Job submitted! Job ID: {job.job_id()}")

        # Monitor job until completion and retrieve results
        def monitor_job(job, timeout: int = 300) -> None:
            """Poll the job status until it reaches a final state or timeout.

            Args:
                job: The Qiskit Runtime job object.
                timeout: Maximum time in seconds to wait for job completion.
            """
            import time

            start_time = time.time()
            while True:
                status = job.status()
                print(f"⏳ Job status: {status}")
                if status in ("DONE", "CANCELLED", "ERROR"):
                    break
                if time.time() - start_time > timeout:
                    print("⚠️ Timeout reached while waiting for job result.")
                    return
                time.sleep(5)

            if status == "DONE":
                try:
                    result = job.result()
                    counts = None
                    try:
                        # Attempt to get counts directly (e.g., for older Sampler or simpler results)
                        counts = result.get_counts()
                    except AttributeError:
                        # Fallback for SamplerV2 PrimitiveResult structure
                        # For a single circuit, access the first result and its measurement data.
                        counts = result[0].data.meas.get_counts()

                    if counts:
                        print("📊 Measurement results (counts):")
                        for bitstring, count in counts.items():
                            print(f"  {bitstring}: {count}")
                    else:
                        print("⚠️ Could not retrieve measurement counts.")
                except Exception as e:
                    print(f"❌ Failed to retrieve results: {e}")
            else:
                print(f"⚠️ Job finished with status: {status}")

        monitor_job(job)

        print("\n✅ IBM Quantum connection verified!")

    except Exception as e:
        print(f"\n❌ Connection failed: {e}")


if __name__ == "__main__":
    verify_connection()
