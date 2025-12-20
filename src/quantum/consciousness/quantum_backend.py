"""
Quantum Backend - CORRECTED VERSION
====================================

Fixes:
1. Prioridade: LOCAL (GPU > CPU) > CLOUD
2. Grover completo com qiskit_algorithms
3. Latency tracking separado por modo
4. GPU support via qiskit-aer-gpu

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: 2025-11-26 (P0 Protocol Fix)
"""

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

import torch  # noqa: E402
from dotenv import load_dotenv

from src.monitor.resource_manager import resource_manager

load_dotenv()

logger = logging.getLogger(__name__)

# --- Runtime Availability Flags ---
DWAVE_AVAILABLE = False
NEAL_AVAILABLE = False
QISKIT_AVAILABLE = False

# --- D-Wave Imports ---
try:
    import dimod  # type: ignore[import-untyped]
    from dwave.system import DWaveSampler  # type: ignore[import-untyped,attr-defined]
    from dwave.system import EmbeddingComposite  # type: ignore[import-untyped,attr-defined]

    DWAVE_AVAILABLE = True
except ImportError:
    pass

# --- Neal (Simulated Annealing) Imports ---
try:
    import neal  # type: ignore[import-untyped]

    NEAL_AVAILABLE = True
except ImportError:
    pass

# --- Qiskit Imports (with proper fallback handling) ---
if TYPE_CHECKING:
    from qiskit.circuit.library import PhaseOracle  # type: ignore[import-untyped,attr-defined]
    from qiskit.primitives import Sampler  # type: ignore[import-untyped,attr-defined]
    from qiskit_aer import AerSimulator  # type: ignore[import-untyped,attr-defined]
    from qiskit_algorithms import AmplificationProblem  # type: ignore[attr-defined]
    from qiskit_algorithms import Grover  # type: ignore[attr-defined]
    from qiskit_algorithms.optimizers import COBYLA  # type: ignore[import-untyped,attr-defined]
    from qiskit_optimization import QuadraticProgram  # type: ignore[import-untyped,attr-defined]
    from qiskit_optimization.algorithms import (
        MinimumEigenOptimizer,  # type: ignore[import-untyped,attr-defined]
    )
else:
    try:  # type: ignore[import-untyped]
        # Core imports (required)
        from qiskit.circuit.library import PhaseOracle  # type: ignore[import-untyped,attr-defined]
        from qiskit_aer import AerSimulator  # type: ignore[import-untyped,attr-defined]
        from qiskit_algorithms import AmplificationProblem  # type: ignore[attr-defined]
        from qiskit_algorithms import Grover  # type: ignore[attr-defined]
        from qiskit_algorithms.optimizers import COBYLA  # type: ignore[import-untyped,attr-defined]
        from qiskit_optimization import (
            QuadraticProgram,  # type: ignore[import-untyped,attr-defined]
        )
        from qiskit_optimization.algorithms import (  # type: ignore[import-untyped,attr-defined]
            MinimumEigenOptimizer,
        )

        # Sampler with version compatibility (newer versions use StatevectorSampler)
        try:
            from qiskit.primitives import Sampler  # type: ignore[import-untyped,attr-defined]
        except ImportError:
            try:
                from qiskit.primitives import (
                    StatevectorSampler as Sampler,  # type: ignore[import-untyped,attr-defined]
                )
            except ImportError:
                # If both fail, we don't need Sampler for core Qiskit ops
                Sampler = None  # type: ignore[assignment,misc]

        QISKIT_AVAILABLE = True
    except ImportError as e:
        logger.debug(f"Qiskit import failed: {e}")
        pass


class QuantumBackend:
    """
    Unified Quantum Backend with proper LOCAL > CLOUD priority.
    Implements Singleton pattern to prevent re-initialization overhead.

    Changes from previous version:
    - Singleton Pattern (Fixes CPU/PCIe bottleneck)
    - Prefer local simulation (GPU > CPU) before cloud
    - Proper Grover implementation via qiskit_algorithms
    - Latency estimation per mode
    - GPU support detection
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QuantumBackend, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        provider: str = "auto",
        api_token: Optional[str] = None,
        prefer_local: bool = True,
    ):
        # Prevent re-initialization
        if self._initialized:
            return

        self.provider = provider
        self.prefer_local = prefer_local
        self.token = (
            api_token
            or os.getenv("QUANTUM_API_TOKEN")
            or os.getenv("IBM_API_KEY")
            or os.getenv("IBMQ_API_TOKEN")
        )
        self.backend: Any = None
        self.mode = "UNKNOWN"  # Will be: LOCAL_GPU, LOCAL_CPU, CLOUD, MOCK
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"QuantumBackend using device: {self.device}")

        # Detect GPU availability (with fallback for CUDA init issues)
        # CRITICAL: Check environment variables FIRST to allow forced GPU mode
        force_gpu_env = os.getenv("OMNIMIND_FORCE_GPU", "").lower() in (
            "true",
            "1",
            "yes",
        )
        force_gpu_pytest = os.getenv("PYTEST_FORCE_GPU", "").lower() in (
            "true",
            "1",
            "yes",
        )

        try:
            self.use_gpu = torch.cuda.is_available()

            # Check for forced GPU mode via environment
            if (force_gpu_env or force_gpu_pytest) and not self.use_gpu:
                try:
                    device_count = torch.cuda.device_count()
                    if device_count > 0:
                        logger.info(
                            f"🚀 FORCED GPU MODE (env override): "
                            f"OMNIMIND_FORCE_GPU={force_gpu_env}, "
                            f"PYTEST_FORCE_GPU={force_gpu_pytest}. "
                            f"device_count={device_count}. Will attempt GPU operations."
                        )
                        self.use_gpu = True
                except Exception as device_count_error:
                    logger.warning(
                        f"Could not check device count (forced mode): {device_count_error}"
                    )
                    self.use_gpu = False

            # Fallback: if is_available() fails but device_count > 0, GPU is present
            elif not self.use_gpu:
                try:
                    device_count = torch.cuda.device_count()
                    if device_count > 0:
                        # This means GPU hardware exists but PyTorch init failed
                        # We can still use GPU by being explicit
                        logger.warning(
                            f"CUDA is_available() = False but device_count = {device_count}. "
                            "GPU hardware detected. Will attempt GPU operations anyway."
                        )
                        self.use_gpu = True  # Force GPU usage despite is_available() failure
                except Exception as device_count_error:
                    logger.warning(f"Could not check device count: {device_count_error}")
                    self.use_gpu = False
        except Exception as e:
            logger.warning(f"CUDA availability check failed: {e}. Assuming no GPU.")
            self.use_gpu = False

        logger.info(
            f"Initializing Quantum Backend. Requested provider: {provider}, "
            f"Prefer Local: {prefer_local}, GPU Available: {self.use_gpu}"
        )

        # Auto-selection logic with LOCAL GPU > LOCAL CPU > CLOUD priority
        if self.provider == "auto":
            if self.prefer_local and QISKIT_AVAILABLE and self.use_gpu:
                self.provider = "local_qiskit"  # Force GPU local
            elif self.prefer_local and QISKIT_AVAILABLE:
                self.provider = "local_qiskit"  # CPU local as fallback
            elif DWAVE_AVAILABLE and os.getenv("DWAVE_API_TOKEN"):
                self.provider = "dwave"
            elif QISKIT_AVAILABLE and self.token:
                self.provider = "ibm"
            elif NEAL_AVAILABLE:
                self.provider = "neal"
            else:
                self.provider = "mock"

        # Initialization
        self._initialize_backend()
        self._initialized = True

    def _initialize_backend(self):
        """Initialize backend with LOCAL > CLOUD priority."""

        if self.provider == "local_qiskit" and QISKIT_AVAILABLE:
            self._setup_local_qiskit()
        elif self.provider == "dwave" and DWAVE_AVAILABLE:
            self._setup_dwave()
        elif self.provider == "ibm" and QISKIT_AVAILABLE:
            self._setup_ibm_cloud()
        elif self.provider == "neal" and NEAL_AVAILABLE:
            self._setup_neal()
        else:
            self._setup_mock()

    def _setup_local_qiskit(self):
        """Setup LOCAL Qiskit Aer (GPU > CPU)."""
        # Use Hybrid Resource Manager
        target_device = resource_manager.allocate_task("quantum", 100.0)

        # Try GPU first if allocated
        if self.use_gpu and target_device == "cuda":
            try:
                self.backend = AerSimulator(method="statevector", device="GPU")
                self.mode = "LOCAL_GPU"
                logger.info("✅ Quantum Backend: LOCAL GPU (qiskit-aer-gpu)")
                return
            except Exception as e:
                logger.error(f"❌ CRITICAL: GPU requested but failed for Qiskit Aer: {e}")
                # STRICT GPU POLICY: Do not fallback to CPU if GPU was expected
                raise RuntimeError(f"Quantum GPU backend failed: {e}")

        # Fallback to CPU (only if GPU not available/requested)
        try:
            self.backend = AerSimulator(method="statevector")
            self.mode = "LOCAL_CPU"
            logger.warning("⚠️ Quantum Backend: LOCAL CPU (Performance degraded)")
        except Exception as e:
            logger.error(f"AerSimulator failed: {e}. Falling back to mock.")
            self._setup_mock()

    def _setup_dwave(self):
        """Setup D-Wave QPU."""
        try:
            sampler = DWaveSampler(  # type: ignore[name-defined]
                token=self.token, solver={"qpu": True}
            )
            self.backend = EmbeddingComposite(sampler)  # type: ignore[name-defined]
            self.mode = "CLOUD_DWAVE"
            logger.info("Connected to D-Wave QPU.")
        except Exception as e:
            logger.error(f"D-Wave connection failed: {e}. Falling back to Neal.")
            self._setup_neal()

    def _setup_ibm_cloud(self):
        """Setup IBM Quantum Cloud with improved error detection."""
        if self.token:
            try:
                from src.quantum.consciousness.qpu_interface import IBMQBackend

                self.backend = IBMQBackend(token=self.token)
                if self.backend.is_available():
                    self.mode = "CLOUD_IBM"
                    logger.info("✅ IBM Quantum Backend (Cloud) - ⚠️ Latency alta (fila)")
                    # Test immediate connectivity to detect issues early
                    try:
                        info = self.backend.get_info()
                        if not info.available:
                            logger.warning("IBM backend reports as unavailable. Using local GPU.")
                            self._setup_local_qiskit()
                    except Exception as test_e:
                        logger.warning(f"IBM backend test failed: {test_e}. Using local GPU.")
                        self._setup_local_qiskit()
                else:
                    logger.warning("IBM Quantum unavailable. Using local GPU simulator.")
                    self._setup_local_qiskit()
            except Exception as e:
                logger.error(f"IBM Quantum failed: {e}. Using local GPU simulator.")
                self._setup_local_qiskit()
        else:
            logger.warning("No IBM token. Using local GPU simulator.")
            self._setup_local_qiskit()

    def _setup_neal(self):
        """Setup Neal (classical annealing)."""
        self.backend = neal.SimulatedAnnealingSampler()  # type: ignore[name-defined]
        self.mode = "LOCAL_NEAL"
        logger.info("Initialized Neal Simulated Annealing (Classical).")

    def _setup_mock(self):
        """Mock backend."""
        self.backend = None
        self.mode = "MOCK"
        logger.warning("No quantum backend available. Using random mock.")

    def get_latency_estimate(self) -> str:
        """Return expected latency for current mode."""
        estimates = {
            "LOCAL_GPU": "<10ms",
            "LOCAL_CPU": "<100ms",
            "LOCAL_NEAL": "<50ms",
            "CLOUD_IBM": "30-120 segundos (fila + execução)",
            "CLOUD_DWAVE": "1-5 segundos",
            "MOCK": "<1ms",
        }
        return estimates.get(self.mode, "unknown")

    def grover_search(self, target: int, search_space: int) -> Dict[str, Any]:
        """
        Grover Search using qiskit_algorithms (CORRECT IMPLEMENTATION).

        Args:
            target: Target state (e.g., 7 for |0111⟩)
            search_space: Size of search space (must be power of 2)

        Returns:
            Result with found state and metrics
        """
        if not QISKIT_AVAILABLE:
            logger.error("Qiskit not available for Grover search.")
            return {"error": "Qiskit not available"}

        try:
            # Convert target to binary string
            num_qubits = len(bin(search_space - 1)) - 2
            target_binary = format(target, f"0{num_qubits}b")

            # Create oracle for target
            # Example: For target=7 (0111), oracle expression: a & b & c & ~d
            oracle_expr = " & ".join(
                [
                    f'{"" if bit == "1" else "~"}{chr(97 + i)}'  # a, b, c, d
                    for i, bit in enumerate(target_binary)
                ]
            )

            oracle = PhaseOracle(oracle_expr)
            problem = AmplificationProblem(oracle, is_good_state=[target_binary])

            # Use StatevectorSampler for local execution
            sampler = Sampler() if self.mode.startswith("CLOUD") else Sampler()
            grover = Grover(sampler=sampler)
            result = grover.amplify(problem)

            logger.info(f"Grover found: {result.top_measurement} (target: {target_binary})")

            return {
                "target": target,
                "target_binary": target_binary,
                "found_state": result.top_measurement,
                "iterations": (result.iterations if hasattr(result, "iterations") else "N/A"),
                "success": result.top_measurement == target_binary,
                "backend": self.mode,
            }
        except Exception as e:
            logger.error(f"Grover search failed: {e}")
            return {"error": str(e), "backend": self.mode}

    def execute_with_fallback(self, operation: str, *args, **kwargs) -> Any:
        """
        Execute operation with automatic fallback to GPU local on IBM errors.

        Args:
            operation: Name of the operation for logging
            *args, **kwargs: Arguments to pass to the operation

        Returns:
            Result of the operation
        """
        try:
            if self.mode.startswith("CLOUD"):
                logger.info(f"Executing {operation} on {self.mode}")
                # For cloud operations, wrap in timeout and error detection
                import asyncio

                result = asyncio.run(
                    asyncio.wait_for(
                        asyncio.to_thread(self._execute_operation, operation, *args, **kwargs),
                        timeout=30.0,  # 30 second timeout for cloud operations
                    )
                )
                return result
            else:
                return self._execute_operation(operation, *args, **kwargs)

        except Exception as e:
            logger.warning(f"{operation} failed on {self.mode}: {e}. Falling back to LOCAL_GPU.")

            # Save current backend info
            original_mode = self.mode
            original_backend = self.backend

            try:
                # Force switch to LOCAL_GPU
                self._setup_local_qiskit()
                logger.info(f"Fallback successful: {original_mode} -> {self.mode}")

                # Retry operation
                return self._execute_operation(operation, *args, **kwargs)

            except Exception as fallback_e:
                logger.error(f"Fallback also failed: {fallback_e}")
                # Restore original backend
                self.mode = original_mode
                self.backend = original_backend
                raise fallback_e

    def _execute_operation(self, operation: str, *args, **kwargs) -> Any:
        """Internal method to execute operations based on type."""
        if operation == "resolve_conflict":
            return self._resolve_conflict_internal(*args, **kwargs)
        elif operation == "grover_search":
            return self.grover_search(*args, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def resolve_conflict(
        self, id_energy: float, ego_energy: float, superego_energy: float
    ) -> Dict[str, Any]:
        """
        Resolves the Id/Ego/Superego conflict using the active backend with automatic fallback.
        """
        return self.execute_with_fallback(
            "resolve_conflict", id_energy, ego_energy, superego_energy
        )

    def _resolve_conflict_internal(
        self, id_energy: float, ego_energy: float, superego_energy: float
    ) -> Dict[str, Any]:
        """
        Internal conflict resolution logic.
        """
        # Ensure energies are floats (handle None if passed dynamically)
        id_energy = float(id_energy or 0.0)
        ego_energy = float(ego_energy or 0.0)
        superego_energy = float(superego_energy or 0.0)

        # Define QUBO (Energy Landscape)
        Q = {
            ("id", "id"): -id_energy,
            ("ego", "ego"): -ego_energy,
            ("superego", "superego"): -superego_energy,
            ("id", "ego"): 0.5,
            ("ego", "superego"): 0.3,
            ("id", "superego"): 0.8,
        }

        if self.provider in ["dwave", "neal", "local_neal"]:
            return self._solve_annealing(Q)
        elif self.provider in ["ibm", "local_qiskit"]:
            return self._solve_gate_based(Q)
        else:
            return self._solve_mock(Q)

    def _solve_annealing(self, Q: Dict) -> Dict[str, Any]:
        """Solves using D-Wave or Neal."""
        if self.backend is None:
            logger.warning("Backend not available, falling back to mock")
            return self._solve_mock(Q)

        bqm: Any = dimod.BinaryQuadraticModel.from_qubo(Q)  # type: ignore[attr-defined]
        sampleset: Any = self.backend.sample(bqm, num_reads=100)  # type: ignore[union-attr]
        best_sample = sampleset.first.sample
        energy = sampleset.first.energy

        return self._format_result(best_sample, energy, is_quantum=(self.provider == "dwave"))

    def _solve_gate_based(self, Q: Dict) -> Dict[str, Any]:
        """Solves using Qiskit QAOA."""
        try:
            problem = QuadraticProgram()
            problem.binary_var("id")
            problem.binary_var("ego")
            problem.binary_var("superego")

            linear = {}
            quadratic = {}
            for (u, v), bias in Q.items():
                if u == v:
                    linear[u] = bias
                else:
                    quadratic[(u, v)] = bias

            problem.minimize(linear=linear, quadratic=quadratic)

            optimizer = COBYLA(maxiter=50)
            sampler = Sampler()  # type: ignore[name-defined]

            # Use local AerSimulator if available
            if self.mode.startswith("LOCAL"):
                from qiskit_algorithms import QAOA  # type: ignore[import-untyped]

                qaoa: Any = QAOA(  # type: ignore[call-arg,operator]
                    sampler=sampler, optimizer=optimizer, reps=1
                )
                algorithm: Any = MinimumEigenOptimizer(qaoa)  # type: ignore[arg-type]
                result: Any = algorithm.solve(problem)  # type: ignore[union-attr]

                var_names = [v.name for v in problem.variables]
                sample = (
                    {name: int(val) for name, val in zip(var_names, result.x)}
                    if result.x is not None
                    else {}
                )
                energy_val = result.fval if result.fval is not None else 0.0
                return self._format_result(sample, energy_val, is_quantum=False)
            else:
                # Cloud path (existing implementation)
                return self._solve_brute_force_fallback(Q)

        except Exception as e:
            logger.error(f"QAOA execution failed: {e}. Falling back to brute force.")
            return self._solve_brute_force_fallback(Q)

    def _solve_brute_force_fallback(self, Q: Dict) -> Dict[str, Any]:
        """Fallback to brute force."""
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

        return (
            self._format_result(best_state, min_energy, is_quantum=False)
            if best_state is not None
            else self._solve_mock(Q)
        )

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
            "backend": f"{self.mode}",
            "is_quantum": is_quantum,
        }


# Alias for backward compatibility
DWaveBackend = QuantumBackend  # type: ignore
