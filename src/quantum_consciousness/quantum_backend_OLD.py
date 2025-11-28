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

import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# --- D-Wave Imports ---
try:
    import dimod
    from dwave.system import DWaveSampler, EmbeddingComposite

    DWAVE_AVAILABLE = True
except ImportError:
    DWAVE_AVAILABLE = False

# --- Neal (Simulated Annealing) Imports ---
try:
    import neal

    NEAL_AVAILABLE = True
except ImportError:
    NEAL_AVAILABLE = False

# --- Qiskit Imports ---
try:
    from qiskit_aer import AerSimulator
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA

    try:
        from qiskit.primitives import Sampler
    except ImportError:
        from qiskit.primitives import StatevectorSampler as Sampler
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class QuantumBackend:
    """
    Unified Quantum Backend for OmniMind.

    Supports multiple providers to ensure scientific validity and accessibility:
    1. D-Wave (Quantum Annealing) - Ideal for optimization, requires API Token.
    2. Neal (Simulated Annealing) - Classical heuristic, mathematically equivalent to D-Wave.
    3. IBM Qiskit (Gate-Based) - Universal quantum computing, runs on Aer (local) or IBM Cloud.
    """

    def __init__(self, provider: str = "auto", api_token: Optional[str] = None):
        self.provider = provider
        self.token = self._resolve_api_token(api_token)
        self.backend = None

        logger.info(f"Initializing Quantum Backend. Requested provider: {provider}")

        # Auto-select provider if needed
        if self.provider == "auto":
            self.provider = self._auto_select_provider()

        # Initialize the selected provider
        self._initialize_provider()

    def _resolve_api_token(self, api_token: Optional[str]) -> Optional[str]:
        """
        Resolve API token from multiple sources.

        Args:
            api_token: Explicitly provided token

        Returns:
            Resolved token or None
        """
        return (
            api_token
            or os.getenv("QUANTUM_API_TOKEN")
            or os.getenv("IBM_API_KEY")
            or os.getenv("IBMQ_API_TOKEN")
        )

    def _auto_select_provider(self) -> str:
        """
        Auto-select the best available provider.

        Returns:
            Selected provider name
        """
        if self._is_dwave_available():
            return "dwave"
        elif self._is_ibm_available():
            return "ibm"
        elif NEAL_AVAILABLE:
            return "neal"
        else:
            return "mock"

    def _is_dwave_available(self) -> bool:
        """Check if D-Wave is available."""
        return DWAVE_AVAILABLE and bool(os.getenv("DWAVE_API_TOKEN"))

    def _is_ibm_available(self) -> bool:
        """Check if IBM Quantum is available."""
        return QISKIT_AVAILABLE and bool(os.getenv("IBMQ_API_TOKEN") or os.getenv("IBM_API_KEY"))

    def _initialize_provider(self) -> None:
        """Initialize the selected quantum provider."""
        provider_initializers = {
            "dwave": self._initialize_dwave,
            "ibm": self._initialize_ibm,
            "neal": self._initialize_neal,
            "mock": self._initialize_mock,
        }

        initializer = provider_initializers.get(self.provider, self._initialize_mock)
        initializer()

    def _initialize_dwave(self) -> None:
        """Initialize D-Wave backend."""
        if not DWAVE_AVAILABLE:
            logger.warning("D-Wave not available. Falling back to Neal.")
            self.provider = "neal"
            self._initialize_neal()
            return

        try:
            self.backend = EmbeddingComposite(DWaveSampler(token=self.token, solver={"qpu": True}))
            logger.info("Connected to D-Wave QPU.")
        except Exception as e:
            logger.error(f"D-Wave connection failed: {e}. Falling back to Neal.")
            self.provider = "neal"
            self._initialize_neal()

    def _initialize_ibm(self) -> None:
        """Initialize IBM Quantum backend."""
        if not QISKIT_AVAILABLE:
            logger.warning("Qiskit not available. Falling back to Aer Simulator.")
            self.backend = AerSimulator()
            return

        if self.token:
            self._initialize_ibm_cloud()
        else:
            self._initialize_ibm_simulator()

    def _initialize_ibm_cloud(self) -> None:
        """Initialize IBM Quantum Cloud backend."""
        try:
            from src.quantum_consciousness.qpu_interface import IBMQBackend

            self.backend = IBMQBackend(token=self.token)
            if self.backend.is_available():
                logger.info("Initialized IBM Quantum Backend (Cloud).")
            else:
                logger.warning("IBM Quantum Backend unavailable. Falling back to Aer Simulator.")
                self.backend = AerSimulator()
        except Exception as e:
            logger.error(f"Failed to initialize IBM Quantum: {e}. Falling back to Aer Simulator.")
            self.backend = AerSimulator()

    def _initialize_ibm_simulator(self) -> None:
        """Initialize IBM Aer Simulator."""
        self.backend = AerSimulator()
        logger.info("Initialized Qiskit Aer Simulator (No IBM Token).")

    def _initialize_neal(self) -> None:
        """Initialize Neal simulated annealing backend."""
        if NEAL_AVAILABLE:
            self.backend = neal.SimulatedAnnealingSampler()
            logger.info("Initialized Neal Simulated Annealing (Classical Fallback).")
        else:
            logger.warning("Neal not available. Falling back to mock.")
            self._initialize_mock()

    def _initialize_mock(self) -> None:
        """Initialize mock backend."""
        logger.warning("No quantum/heuristic backend available. Using random mock.")

    def resolve_conflict(
        self, id_energy: float, ego_energy: float, superego_energy: float
    ) -> Dict[str, Any]:
        """
        Resolves the Id/Ego/Superego conflict using the active backend.
        """
        # Define QUBO (Energy Landscape)
        # Minimize E = x'Qx
        Q = {
            ("id", "id"): -id_energy,
            ("ego", "ego"): -ego_energy,
            ("superego", "superego"): -superego_energy,
            ("id", "ego"): 0.5,  # Conflict
            ("ego", "superego"): 0.3,  # Conflict
            ("id", "superego"): 0.8,  # Strong Conflict
        }

        if self.provider == "dwave" or self.provider == "neal":
            return self._solve_annealing(Q)
        elif self.provider == "ibm":
            return self._solve_gate_based(Q)
        else:
            return self._solve_mock(Q)

    def _solve_annealing(self, Q: Dict) -> Dict[str, Any]:
        """Solves using D-Wave or Neal."""
        bqm = dimod.BinaryQuadraticModel.from_qubo(Q)

        # Sample
        sampleset = self.backend.sample(bqm, num_reads=100)

        best_sample = sampleset.first.sample
        energy = sampleset.first.energy

        return self._format_result(best_sample, energy, is_quantum=(self.provider == "dwave"))

    def _solve_gate_based(self, Q: Dict) -> Dict[str, Any]:
        """
        Solves using Qiskit QAOA (Quantum Approximate Optimization Algorithm).
        This replaces the previous brute-force simulation with a scientifically valid
        variational quantum algorithm.
        """
        try:
            # 1. Define the Problem (QUBO)
            problem = QuadraticProgram()
            # Add binary variables
            problem.binary_var("id")
            problem.binary_var("ego")
            problem.binary_var("superego")

            # Convert Q dictionary to linear and quadratic terms
            linear = {}
            quadratic = {}

            for (u, v), bias in Q.items():
                if u == v:
                    linear[u] = bias
                else:
                    quadratic[(u, v)] = bias

            problem.minimize(linear=linear, quadratic=quadratic)

            # 2. Configure QAOA
            optimizer = COBYLA(maxiter=50)  # Classical optimizer
            sampler = Sampler()  # Primitive to execute circuits
            qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)

            # 3. Solve
            algorithm = MinimumEigenOptimizer(qaoa)
            result = algorithm.solve(problem)

            # 4. Extract Results
            # result.x is a list of variable values [id, ego, superego]
            # We need to map back to names based on variable order
            var_names = [v.name for v in problem.variables]
            sample = {name: int(val) for name, val in zip(var_names, result.x)}

            return self._format_result(sample, result.fval, is_quantum=False)  # Still simulated

        except Exception as e:
            logger.error(f"QAOA execution failed: {e}. Falling back to brute force.")
            return self._solve_brute_force_fallback(Q)

    def _solve_brute_force_fallback(self, Q: Dict) -> Dict[str, Any]:
        """
        Fallback to brute force if QAOA fails (e.g. missing libraries).
        """
        # 3 Qubits: 0=Id, 1=Ego, 2=Superego
        best_state = None
        min_energy = float("inf")

        for i in range(8):
            b = format(i, "03b")
            state = {"id": int(b[0]), "ego": int(b[1]), "superego": int(b[2])}
            energy = 0
            for (u, v), bias in Q.items():
                val_u = state.get(u, 0)
                val_v = state.get(v, 0)
                energy += val_u * val_v * bias

            if energy < min_energy:
                min_energy = energy
                best_state = state

        return self._format_result(best_state, min_energy, is_quantum=False)

    def _solve_mock(self, Q: Dict) -> Dict[str, Any]:
        """Random fallback."""
        return {
            "winner": "ego",
            "sample": {"id": 0, "ego": 1, "superego": 0},
            "energy": -0.5,
            "backend": "Mock",
            "is_quantum": False,
        }

    def _format_result(self, sample: Dict, energy: float, is_quantum: bool) -> Dict[str, Any]:
        """Determines the winner from the sample."""
        winner = "ego"
        if sample.get("id") == 1 and sample.get("superego") == 0:
            winner = "id"
        elif sample.get("superego") == 1 and sample.get("id") == 0:
            winner = "superego"
        elif sample.get("ego") == 1:
            winner = "ego"

        return {
            "winner": winner,
            "sample": sample,
            "energy": energy,
            "backend": f"{self.provider.upper()} Backend",
            "is_quantum": is_quantum,
        }


# Alias for backward compatibility
DWaveBackend = QuantumBackend
