from typing import Dict, Any, Optional
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# --- D-Wave Imports ---
try:
    from dwave.system import DWaveSampler, EmbeddingComposite
    import dimod

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
        # Support both variable names
        self.token = (
            api_token
            or os.getenv("QUANTUM_API_TOKEN")
            or os.getenv("IBM_API_KEY")
            or os.getenv("IBMQ_API_TOKEN")
        )
        self.backend = None

        logger.info(f"Initializing Quantum Backend. Requested provider: {provider}")

        # Auto-selection logic
        if self.provider == "auto":
            if DWAVE_AVAILABLE and os.getenv("DWAVE_API_TOKEN"):
                self.provider = "dwave"
            elif QISKIT_AVAILABLE and (os.getenv("IBMQ_API_TOKEN") or os.getenv("IBM_API_KEY")):
                self.provider = "ibm"
            elif NEAL_AVAILABLE:
                self.provider = "neal"
            else:
                self.provider = "mock"

        # Initialization
        if self.provider == "dwave" and DWAVE_AVAILABLE:
            try:
                self.backend = EmbeddingComposite(
                    DWaveSampler(token=self.token, solver={"qpu": True})
                )
                logger.info("Connected to D-Wave QPU.")
            except Exception as e:
                logger.error(f"D-Wave connection failed: {e}. Falling back to Neal.")
                self.provider = "neal"

        if self.provider == "ibm" and QISKIT_AVAILABLE:
            # For now, we default to local Aer simulator to ensure it runs without credentials
            # In production, this would connect to IBM Quantum via QiskitRuntimeService
            self.backend = AerSimulator()
            logger.info("Initialized Qiskit Aer Simulator (IBM Token Detected).")

        if self.provider == "neal" and NEAL_AVAILABLE:
            self.backend = neal.SimulatedAnnealingSampler()
            logger.info("Initialized Neal Simulated Annealing (Classical Fallback).")

        if self.provider == "mock":
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
