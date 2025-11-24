"""
QPU Interface for OmniMind.

Provides abstraction for quantum processing units:
- Local simulators (Qiskit Aer)
- IBM Quantum cloud (IBMQ) - prepared but not executed without credentials
- Automatic fallback to simulator

Supports both Qiskit and Cirq backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import structlog

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QuantumCircuit = Any  # Type alias when Qiskit not available
    AerSimulator = Any
    generate_preset_pass_manager = Any

try:
    import cirq

    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False
    cirq = None

logger = structlog.get_logger(__name__)


class BackendType(Enum):
    """Types of quantum backends."""

    SIMULATOR_AER = "qiskit_aer"
    SIMULATOR_CIRQ = "cirq_simulator"
    IBMQ_CLOUD = "ibmq_cloud"
    GOOGLE_QUANTUM = "google_quantum"


@dataclass
class BackendInfo:
    """Information about a quantum backend."""

    name: str
    backend_type: BackendType
    num_qubits: int
    available: bool
    provider: str
    description: str = ""

    def __str__(self) -> str:
        """String representation."""
        status = "✓ Available" if self.available else "✗ Unavailable"
        return (
            f"{self.name} ({self.provider}): {status}\n"
            f"  Type: {self.backend_type.value}\n"
            f"  Qubits: {self.num_qubits}\n"
            f"  {self.description}"
        )


class QPUBackend(ABC):
    """Abstract base class for quantum backends."""

    @abstractmethod
    def execute(self, circuit: Any, shots: int = 1024) -> Dict[str, int]:
        """
        Execute quantum circuit.

        Args:
            circuit: Quantum circuit to execute
            shots: Number of shots

        Returns:
            Measurement counts
        """
        pass

    @abstractmethod
    def get_info(self) -> BackendInfo:
        """Get backend information."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available."""
        pass


class SimulatorBackend(QPUBackend):
    """
    Local simulator backend using Qiskit Aer.

    Always available for testing and development.
    """

    def __init__(self, num_qubits: int = 10) -> None:
        """
        Initialize simulator backend.

        Args:
            num_qubits: Maximum number of qubits
        """
        self.num_qubits = num_qubits
        self.backend_type = BackendType.SIMULATOR_AER

        if QISKIT_AVAILABLE:
            self.simulator = AerSimulator()
        else:
            self.simulator = None
            logger.warning(
                "qiskit_aer_not_available", msg="Install with: pip install qiskit-aer"
            )

        logger.info(
            "simulator_backend_initialized",
            num_qubits=num_qubits,
            available=self.is_available(),
        )

    def execute(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        """Execute circuit on simulator."""
        if not self.is_available():
            raise RuntimeError("Qiskit Aer not available")

        # Add measurements if not present
        qc = circuit.copy()
        if not any(instr.operation.name == "measure" for instr in qc.data):
            qc.measure_all()

        # Run simulation
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        logger.info(
            "simulator_execution_complete", shots=shots, num_outcomes=len(counts)
        )

        return counts

    def get_info(self) -> BackendInfo:
        """Get backend information."""
        return BackendInfo(
            name="Qiskit Aer Simulator",
            backend_type=self.backend_type,
            num_qubits=self.num_qubits,
            available=self.is_available(),
            provider="Qiskit",
            description="Local quantum simulator (classical simulation)",
        )

    def is_available(self) -> bool:
        """Check if simulator is available."""
        return QISKIT_AVAILABLE and self.simulator is not None


class IBMQBackend(QPUBackend):
    """
    IBM Quantum cloud backend.

    ⚠️  EXPERIMENTAL - Requires IBM Quantum credentials
    Falls back to simulator if credentials not available.
    """

    def __init__(
        self, token: Optional[str] = None, use_least_busy: bool = True
    ) -> None:
        """
        Initialize IBMQ backend.

        Args:
            token: IBM Quantum API token
            use_least_busy: Use least busy available quantum computer
        """
        self.token = token
        self.use_least_busy = use_least_busy
        self.backend_type = BackendType.IBMQ_CLOUD
        self.ibm_backend: Optional[Any] = None
        self.service: Optional[Any] = None

        # Try to initialize IBMQ
        if token and QISKIT_AVAILABLE:
            self._initialize_ibmq()
        else:
            logger.warning(
                "ibmq_not_initialized",
                has_token=token is not None,
                qiskit_available=QISKIT_AVAILABLE,
                msg="Will fallback to simulator",
            )

    def _initialize_ibmq(self) -> None:
        """Initialize IBM Quantum service."""
        try:
            # Try new qiskit-ibm-runtime (Qiskit 1.0+)
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService

                self.service = QiskitRuntimeService(
                    channel="ibm_quantum", token=self.token
                )

                if self.use_least_busy:
                    # Get least busy backend
                    backends = self.service.backends(simulator=False, operational=True)
                    if backends:
                        # Sort by queue length
                        self.ibm_backend = min(
                            backends, key=lambda b: b.status().pending_jobs
                        )
                else:
                    # Get default backend
                    self.ibm_backend = self.service.backend()

                logger.info(
                    "ibmq_initialized",
                    backend=self.ibm_backend.name if self.ibm_backend else None,
                )
            except ImportError:
                logger.warning(
                    "qiskit_ibm_runtime_not_available",
                    msg="Install with: pip install qiskit-ibm-runtime",
                )
        except Exception as e:
            logger.error("ibmq_initialization_failed", error=str(e))

    def execute(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        """Execute circuit on IBM Quantum."""
        if not self.is_available():
            logger.warning("ibmq_not_available_fallback_to_simulator")
            # Fallback to simulator
            simulator = SimulatorBackend()
            return simulator.execute(circuit, shots)

        # Transpile for backend
        pm = generate_preset_pass_manager(
            backend=self.ibm_backend, optimization_level=1
        )
        transpiled = pm.run(circuit)

        # Execute on quantum hardware
        job = self.ibm_backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()

        logger.info(
            "ibmq_execution_complete",
            backend=self.ibm_backend.name,
            shots=shots,
            job_id=job.job_id(),
        )

        return counts

    def get_info(self) -> BackendInfo:
        """Get backend information."""
        if self.ibm_backend:
            config = self.ibm_backend.configuration()
            return BackendInfo(
                name=self.ibm_backend.name,
                backend_type=self.backend_type,
                num_qubits=config.num_qubits,
                available=True,
                provider="IBM Quantum",
                description=f"Real quantum hardware: {config.description}",
            )
        else:
            return BackendInfo(
                name="IBM Quantum (Not Connected)",
                backend_type=self.backend_type,
                num_qubits=0,
                available=False,
                provider="IBM Quantum",
                description="Credentials required",
            )

    def is_available(self) -> bool:
        """Check if IBMQ backend is available."""
        return self.ibm_backend is not None


class QPUInterface:
    """
    Main QPU interface with automatic backend selection.

    Provides unified interface for:
    - Local simulators
    - Cloud quantum computers
    - Automatic fallback
    """

    active_backend: Optional[QPUBackend]

    def __init__(
        self,
        preferred_backend: BackendType = BackendType.SIMULATOR_AER,
        ibmq_token: Optional[str] = None,
    ) -> None:
        """
        Initialize QPU interface.

        Args:
            preferred_backend: Preferred backend type
            ibmq_token: Optional IBM Quantum token
        """
        self.preferred_backend = preferred_backend
        self.backends: Dict[BackendType, QPUBackend] = {}

        # Initialize available backends
        self._initialize_backends(ibmq_token)

        # Select active backend
        self.active_backend = self._select_backend()

        logger.info(
            "qpu_interface_initialized",
            preferred=preferred_backend.value,
            active=(
                self.active_backend.get_info().name if self.active_backend else "None"
            ),
            num_backends=len(self.backends),
        )

    def _initialize_backends(self, ibmq_token: Optional[str]) -> None:
        """Initialize all available backends."""
        # Always try to initialize simulator
        try:
            simulator = SimulatorBackend()
            if simulator.is_available():
                self.backends[BackendType.SIMULATOR_AER] = simulator
                logger.info("simulator_backend_available")
        except Exception as e:
            logger.error("simulator_initialization_failed", error=str(e))

        # Try to initialize IBMQ if token provided
        if ibmq_token:
            try:
                ibmq = IBMQBackend(token=ibmq_token)
                if ibmq.is_available():
                    self.backends[BackendType.IBMQ_CLOUD] = ibmq
                    logger.info("ibmq_backend_available")
            except Exception as e:
                logger.error("ibmq_initialization_failed", error=str(e))

    def _select_backend(self) -> Optional[QPUBackend]:
        """Select best available backend."""
        # Try preferred backend first
        if self.preferred_backend in self.backends:
            return self.backends[self.preferred_backend]

        # Fallback to any available backend
        if self.backends:
            backend = next(iter(self.backends.values()))
            logger.warning(
                "using_fallback_backend",
                preferred=self.preferred_backend.value,
                actual=backend.get_info().name,
            )
            return backend

        # No backends available - return None instead of raising
        logger.warning(
            "no_quantum_backends_available",
            msg="No quantum backends available. Install qiskit-aer: pip install qiskit-aer",
        )
        return None

    def execute(
        self,
        circuit: Any,
        shots: int = 1024,
        backend_type: Optional[BackendType] = None,
    ) -> Dict[str, int]:
        """
        Execute quantum circuit.

        Args:
            circuit: Quantum circuit to execute
            shots: Number of measurement shots
            backend_type: Optional specific backend to use

        Returns:
            Measurement counts
        """
        if self.active_backend is None:
            raise RuntimeError(
                "No quantum backends available. Install qiskit-aer: pip install qiskit-aer"
            )

        backend = self.active_backend

        if backend_type and backend_type in self.backends:
            backend = self.backends[backend_type]

        logger.info("executing_circuit", backend=backend.get_info().name, shots=shots)

        return backend.execute(circuit, shots)

    def list_backends(self) -> List[BackendInfo]:
        """List all available backends."""
        return [backend.get_info() for backend in self.backends.values()]

    def get_active_backend_info(self) -> Optional[BackendInfo]:
        """Get information about active backend."""
        if self.active_backend is None:
            return None
        return self.active_backend.get_info()

    def switch_backend(self, backend_type: BackendType) -> bool:
        """
        Switch to different backend.

        Args:
            backend_type: Backend type to switch to

        Returns:
            True if switch successful
        """
        if backend_type not in self.backends:
            logger.error("backend_not_available", requested=backend_type.value)
            return False

        self.active_backend = self.backends[backend_type]
        logger.info(
            "backend_switched",
            new_backend=(
                self.active_backend.get_info().name if self.active_backend else "None"
            ),
        )
        return True
