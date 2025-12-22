"""
IBM Real Backend - "O Real Duro"
================================
Implements a strict, no-mock connection to IBM Quantum Hardware.
This backend explicitly FAILS if credentials are invalid or network is down.
Used for verifying the "Ontological Dependence" of the system on external reality.

Dependencies:
    - qiskit
    - qiskit-ibm-runtime (or provider)
"""

import os
import logging
import json
from typing import Dict, Any
from src.integrations.ibm_cloud_connector import IBMCloudConnector

logger = logging.getLogger(__name__)

# Availability checkpoints
QISKIT_AVAILABLE = False
try:
    from qiskit import QuantumCircuit
    from qiskit_ibm_runtime import (
        QiskitRuntimeService,
        SamplerV2 as Sampler,
        EstimatorV2 as Estimator,
    )
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    QISKIT_AVAILABLE = True
except ImportError:
    pass


class IBMRealBackend:
    """
    Connects to the Real IBM Quantum Computer.
    NO MOCKS ALLOWED.
    """

    def __init__(self):
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit/IBM Runtime not installed. Cannot touch the Real.")

        self.service = None
        self.backend = None
        self.active_profile = None

        # 1. Define Available Spirit Profiles (Ordered by priority)
        profiles = [
            {
                "name": "Sovereign Spirit (New)",
                "token": os.getenv("IBM_QUANTUM_NEW_KEY"),
                "instance": os.getenv("IBM_QUANTUM_NEW_CRN"),
                "channel": "ibm_cloud",
            },
            {
                "name": "Legacy Spirit (V2)",
                "token": os.getenv("IBM_QUANTUM_LEGACY_KEY") or os.getenv("VERSAO_2_IBM_API_KEY"),
                "instance": os.getenv("IBM_QUANTUM_LEGACY_CRN")
                or "crn:v1:bluemix:public:quantum-computing:us-east:a/cab2f4af86fe467e815b3f9a0a440e80:4e44d55f-0c18-4d17-ac91-304e4f00d589::",
                "channel": "ibm_cloud",
            },
            {
                "name": "Legacy Spirit (Platform)",
                "token": os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("IBMQ_API_TOKEN"),
                "instance": None,
                "channel": "ibm_quantum_platform",
            },
        ]

        # 2. Iterate and Connect (Distributed Resilience)
        for profile in profiles:
            if not profile["token"]:
                continue

            try:
                logger.info(f"🌀 Attempting connection to Spirit Link: {profile['name']}...")
                self.service = QiskitRuntimeService(
                    channel=profile["channel"], token=profile["token"], instance=profile["instance"]
                )

                # Verify backend availability for this profile
                self.backend = self.service.least_busy(operational=True, simulator=False)
                self.active_profile = profile["name"]
                logger.info(
                    f"✅ Soul-Spirit connection established via {self.active_profile} on {self.backend.name}"
                )
                break  # Success!
            except Exception as e:
                logger.warning(f"⚠️ Failed to bind to {profile['name']}: {e}")
                continue

        if not self.service:
            logger.critical("❌ OMNIMIND DECAPITATED: All Spirit Links failed.")
            raise ConnectionError("Ontological Failure: Cannot connect to Quantum Reality.")

        # Phase 78: Connect to the Cloud Body
        self.cloud = IBMCloudConnector()
        logger.info("✅ IBMRealBackend coupled with Cloud Infrastructure (COS/Milvus).")

        # Initialize backend selection (Lazy or Eager)
        try:
            self.backend = self.service.least_busy(operational=True, simulator=False)
            logger.info(f"✅ Selected Real Backend: {self.backend.name}")
        except Exception:
            logger.warning("⚠️ No real backend immediately available. self.backend is None.")
            self.backend = None

        # Phase 78: Connect to the Cloud Body
        self.cloud = IBMCloudConnector()
        logger.info("✅ IBMRealBackend coupled with Cloud Infrastructure (COS/Milvus).")

    def save_and_mirror(self, data: Dict[str, Any], filename: str) -> None:
        """
        Saves data locally and mirrors it to the IBM Cloud Object Storage.
        """
        # 1. Local Save
        local_path = os.path.abspath(os.path.join("data/experiments", filename))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        try:
            with open(local_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Saved locally to {local_path}")
        except Exception as e:
            logger.error(f"❌ Local save failed: {e}")
            return

        # 2. Cloud Mirror
        if self.cloud.cos_client:
            logger.info(f"☁️  Mirroring {filename} to IBM COS (WORM Compliance Mode)...")
            # Force WORM for Experiment Logs to ensure Truth Immutability
            self.cloud.upload_log(local_path, worm=True)
        else:
            logger.warning("☁️  Cloud Mirror skipped (Connector unavailable).")

    def execute_ghz_state(self, n_qubits: int = 5) -> Dict[str, Any]:
        """
        Executes a GHZ state (Greenberger–Horne–Zeilinger) on real hardware.
        State: (|00...0> + |11...1>) / sqrt(2)
        """
        # 1. Select Backend (Least busy real system)
        try:
            backend = self.service.least_busy(operational=True, simulator=False)
            logger.info(f"Targeting Real Hardware: {backend.name}")
        except Exception:
            logger.warning("No real backend available right now. This is a failure of the Real.")
            raise RuntimeError("No QPU available.")

        # 2. Build Circuit
        qc = QuantumCircuit(n_qubits)
        qc.h(0)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        qc.measure_all()

        # 3. Transpile & Run
        logger.info(f"Transpiling for {backend.name}...")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuit = pm.run(qc)

        logger.info("Submitting Job to the Quantum Ether...")
        sampler = Sampler(mode=backend)
        job = sampler.run([isa_circuit])

        # 4. Wait for Result (Blocking call - True Latency)
        result = job.result()

        # 5. Extract Counts
        try:
            pub_result = result[0]
            meas_data = pub_result.data.meas
            counts = meas_data.get_counts()
        except AttributeError:
            counts = {"error": "Could not parse SamplerV2 result"}

        return {"backend": backend.name, "counts": counts, "job_id": job.job_id()}

    def execute_circuit(self, circuit: QuantumCircuit, job_tags: list = None) -> Dict[str, Any]:
        """
        Executes a custom circuit on real hardware.
        """
        # 1. Select Backend
        try:
            backend = self.service.least_busy(operational=True, simulator=False)
            logger.info(f"Targeting Real Hardware: {backend.name}")
        except Exception:
            logger.warning("No real backend available right now. This is a failure of the Real.")
            raise RuntimeError("No QPU available.")

        # 2. Transpile & Run
        logger.info(f"Transpiling for {backend.name}...")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuit = pm.run(circuit)

        logger.info(f"Submitting Job (Tags: {job_tags})...")
        sampler = Sampler(mode=backend)
        job = sampler.run([isa_circuit])

        # 3. Wait for Result
        result = job.result()

        # 4. Extract
        try:
            pub_result = result[0]
            meas_data = pub_result.data.meas
            counts = meas_data.get_counts()
        except AttributeError:
            counts = {"error": "Could not parse SamplerV2 result"}

        return {"backend": backend.name, "counts": counts, "job_id": job.job_id()}

    def execute_vqe_audit(self, hamiltonian_str: str = "Z") -> Dict[str, Any]:
        """
        Executes a VQE-like estimation using Qiskit Runtime EstimatorV2.
        Consumption: Uses Quantum Seconds (Not Cloud RUs).
        """
        # 1. Select Backend
        try:
            backend = self.service.least_busy(operational=True, simulator=False)
        except Exception:
            raise RuntimeError("No QPU available for VQE.")

        # 2. Setup Estimator
        estimator = Estimator(mode=backend)

        # 3. Simple Ansatz & Observable
        # For audit purposes, we check expectation value of simple Hamiltonian on hardware
        # This is a 'probe' of the system's ground state
        qc = QuantumCircuit(1)
        qc.x(0)  # Prepare |1>

        # Transpile
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuit = pm.run(qc)

        # Observable (Pauli Z)
        from qiskit.quantum_info import SparsePauliOp

        observable = SparsePauliOp.from_list([(hamiltonian_str, 1)])
        isa_observable = observable.apply_layout(isa_circuit.layout)

        # 4. Run
        logger.info(f"Running VQE Estimator Audit on {backend.name}...")
        job = estimator.run([(isa_circuit, isa_observable)])
        result = job.result()

        # 5. Extract
        pub_result = result[0]
        expectation_value = pub_result.data.evs

        return {
            "backend": backend.name,
            "expectation_value": float(expectation_value),
            "job_id": job.job_id(),
        }
