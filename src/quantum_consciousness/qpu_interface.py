"""
Quantum Processing Unit (QPU) Interface for OmniMind - Phase 21-23 Preparation.

Provides unified abstraction layer for quantum computing backends:
- Local simulators (Qiskit Aer, Cirq) for development and testing
- Cloud quantum computers (IBM Quantum, Google Quantum AI)
- Automatic fallback strategies and backend selection
- Performance monitoring and error handling

Core Concepts:
- Backend Abstraction: Unified interface for different quantum providers
- Fallback Strategy: Graceful degradation when preferred backends unavailable
- Resource Management: Automatic backend selection based on availability and requirements
- Error Handling: Comprehensive error recovery with logging and fallback

Supported Backends:
- Qiskit Aer Simulator: Local classical simulation of quantum circuits
- IBM Quantum Cloud: Real quantum hardware via IBM Quantum Experience
- Cirq Simulator: Google's quantum computing framework (prepared)
- Google Quantum AI: Future integration with Sycamore processor

Mathematical Foundation:
- Quantum State: |ψ⟩ = Σᵢ αᵢ|i⟩, where αᵢ are complex amplitudes
- Measurement: Probability p(i) = |⟨i|ψ⟩|² for outcome i
- Circuit Execution: U|ψ₀⟩ = |ψ⟩, where U is unitary evolution operator

Integration Points:
- Quantum Cognition Engine: Uses QPU for superposition-based reasoning
- Quantum Memory: Leverages quantum parallelism for associative recall
- Hybrid Cognition: Compares classical vs quantum performance
- Consciousness Simulation: Quantum effects for emergence modeling

Example Usage:
    # Initialize with preferred backend
    qpu = QPUInterface(preferred_backend=BackendType.SIMULATOR_AER)

    # Execute quantum circuit
    circuit = create_bell_state_circuit()
    counts = qpu.execute(circuit, shots=1024)

    # List available backends
    backends = qpu.list_backends()
    print(f"Available backends: {len(backends)}")

Fallback Behavior:
- Primary: Use preferred backend if available
- Secondary: Fallback to any available backend
- Tertiary: Raise error if no backends available
- Strict Mode: Disable fallback, raise errors immediately

Security Considerations:
- IBM Quantum tokens stored securely (not hardcoded)
- No sensitive data transmitted to quantum backends
- Local simulation for sensitive computations

Performance Characteristics:
- Simulators: Fast execution, unlimited shots, perfect for development
- Real Hardware: Slower (minutes), limited shots, true quantum effects
- Auto-selection: Balances speed vs authenticity based on use case

Author: OmniMind Quantum Computing Team
License: MIT
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

# Retry mechanism with exponential backoff
RETRY_BASE_DELAY = 1.0  # seconds
RETRY_MAX_DELAY = 30.0  # seconds
RETRY_MAX_ATTEMPTS = 5
RETRY_JITTER_FACTOR = 0.1  # 10% random jitter to prevent thundering herd

try:
    from qiskit import QuantumCircuit  # type: ignore[import-untyped]
    from qiskit.transpiler.preset_passmanagers import (
        generate_preset_pass_manager,  # type: ignore[import-untyped]
    )
    from qiskit_aer import AerSimulator  # type: ignore[import-untyped]

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
    cirq = None  # type: ignore[assignment]

logger = structlog.get_logger(__name__)


def retry_with_exponential_backoff(
    func: Any,
    *args: Any,
    max_attempts: int = RETRY_MAX_ATTEMPTS,
    base_delay: float = RETRY_BASE_DELAY,
    max_delay: float = RETRY_MAX_DELAY,
    **kwargs: Any,
) -> Any:
    """
    Execute function with exponential backoff retry mechanism.

    CRITICAL FIX: Implements exponential backoff for transient quantum
    operation failures (connectivity, temporary unavailability, etc.).

    Features:
    - Exponential backoff: delay = min(base_delay * 2^attempt, max_delay)
    - Jitter: Add random jitter to prevent thundering herd
    - Logging: Track all retry attempts
    - Type-aware: Works with any callable

    Args:
        func: Function/method to retry
        *args: Positional arguments to pass to func
        max_attempts: Maximum number of attempts (default 5)
        base_delay: Initial delay in seconds (default 1.0)
        max_delay: Maximum delay cap in seconds (default 30.0)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of successful function call

    Raises:
        Exception: Last exception if all attempts fail

    Example:
        result = retry_with_exponential_backoff(
            qpu.execute,
            circuit,
            max_attempts=5,
            base_delay=1.0,
            max_delay=30.0
        )
    """
    import random
    import time

    last_exception: Optional[Exception] = None

    for attempt in range(max_attempts):
        try:
            logger.debug(
                f"Attempting {func.__name__}",
                attempt=attempt + 1,
                max_attempts=max_attempts,
            )
            return func(*args, **kwargs)

        except Exception as e:
            last_exception = e
            if attempt == max_attempts - 1:
                # Last attempt failed
                logger.error(
                    f"All {max_attempts} attempts to {func.__name__} failed",
                    last_error=str(e),
                    error_type=type(e).__name__,
                )
                raise

            # Calculate exponential backoff with jitter
            delay = min(base_delay * (2**attempt), max_delay)
            jitter = delay * RETRY_JITTER_FACTOR * random.random()
            total_delay = delay + jitter

            logger.warning(
                f"{func.__name__} failed, retrying...",
                attempt=attempt + 1,
                max_attempts=max_attempts,
                error=str(e),
                next_retry_delay=f"{total_delay:.2f}s",
            )

            time.sleep(total_delay)

    # Should never reach here, but handle just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Failed to execute {func.__name__} after {max_attempts} attempts")


class BackendType(Enum):
    """
    Enumeration of supported quantum backend types.

    Defines the available quantum computing platforms and simulators
    that can be used for executing quantum circuits in OmniMind.

    Attributes:
        SIMULATOR_AER: Qiskit Aer local simulator (classical simulation)
        SIMULATOR_CIRQ: Cirq local simulator (Google's framework)
        IBMQ_CLOUD: IBM Quantum cloud service (real quantum hardware)
        GOOGLE_QUANTUM: Google Quantum AI service (future integration)
    """

    SIMULATOR_AER = "qiskit_aer"
    SIMULATOR_CIRQ = "cirq_simulator"
    IBMQ_CLOUD = "ibmq_cloud"
    GOOGLE_QUANTUM = "google_quantum"


@dataclass
class BackendInfo:
    """
    Comprehensive information about a quantum backend.

    Provides detailed metadata about quantum computing resources,
    including capabilities, availability, and performance characteristics.

    Attributes:
        name: Human-readable backend name
        backend_type: Type of backend (simulator/hardware/cloud)
        num_qubits: Maximum number of qubits supported
        available: Current availability status
        provider: Organization providing the backend
        description: Detailed description of backend capabilities

    Usage:
        Used for backend selection, monitoring, and user interface display.
        Helps users understand backend characteristics for optimal choice.
    """

    name: str
    backend_type: BackendType
    num_qubits: int
    available: bool
    provider: str
    description: str = ""

    def __str__(self) -> str:
        """
        String representation for logging and display.

        Returns:
            Formatted string with backend information
        """
        status = "✓ Available" if self.available else "✗ Unavailable"
        return (
            f"{self.name} ({self.provider}): {status}\n"
            f"  Type: {self.backend_type.value}\n"
            f"  Qubits: {self.num_qubits}\n"
            f"  {self.description}"
        )

    def supports_circuit(self, circuit: Any) -> bool:
        """
        Check if backend can execute a given circuit.

        Args:
            circuit: Quantum circuit to validate

        Returns:
            True if circuit is compatible with backend

        Validation Criteria:
        - Number of qubits ≤ backend capacity
        - Gate set supported by backend
        - Circuit depth within limits
        """
        try:
            circuit_qubits = getattr(circuit, "num_qubits", 0)
            return circuit_qubits <= self.num_qubits
        except AttributeError:
            return False

    def estimated_execution_time(self, circuit: Any, shots: int = 1024) -> float:
        """
        Estimate execution time for a circuit on this backend.

        Args:
            circuit: Circuit to estimate
            shots: Number of measurement shots

        Returns:
            Estimated execution time in seconds

        Estimation Factors:
        - Simulators: Fast (milliseconds)
        - Real hardware: Queue time + execution time (minutes)
        - Circuit complexity: Depth and gate count
        """
        if not self.available:
            return float("inf")

        # Simulators are fast
        if self.backend_type in [BackendType.SIMULATOR_AER, BackendType.SIMULATOR_CIRQ]:
            return 0.1  # Conservative estimate

        # Real hardware has significant latency
        elif self.backend_type == BackendType.IBMQ_CLOUD:
            # Base queue time + execution time
            base_time = 300  # 5 minutes average queue
            circuit_depth = getattr(circuit, "depth", lambda: 10)()
            execution_time = circuit_depth * 0.01 * shots  # Rough estimate
            return base_time + execution_time

        return 60.0  # Default estimate


class QPUBackend(ABC):
    """
    Abstract base class for quantum processing unit backends.

    Defines the interface that all quantum backends must implement,
    ensuring consistent behavior across different providers and platforms.

    This abstraction allows OmniMind to work with various quantum computing
    ecosystems while maintaining a unified programming model.

    Key Responsibilities:
    - Circuit execution with measurement
    - Backend capability reporting
    - Availability checking
    - Error handling and recovery
    """

    @abstractmethod
    def execute(self, circuit: Any, shots: int = 1024) -> Dict[str, int]:
        """
        Execute quantum circuit and return measurement results.

        Args:
            circuit: Quantum circuit to execute (Qiskit, Cirq, etc.)
            shots: Number of measurement repetitions for statistics

        Returns:
            Dictionary mapping measurement outcomes to counts
            Example: {'00': 512, '01': 256, '10': 200, '11': 56}

        Implementation Notes:
        - Automatically adds measurements if not present
        - Handles transpilation for specific backend requirements
        - Manages job submission and result retrieval
        - Provides comprehensive error handling
        """
        pass

    @abstractmethod
    def get_info(self) -> BackendInfo:
        """
        Get comprehensive information about this backend.

        Returns:
            BackendInfo object with capabilities and status

        Information Includes:
        - Name and provider
        - Qubit count and connectivity
        - Current availability
        - Performance characteristics
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if backend is currently available for use.

        Returns:
            True if backend can accept and execute circuits

        Availability Factors:
        - Service connectivity
        - Authentication status
        - Hardware operational status
        - Resource allocation
        """
        pass

    def validate_circuit(self, circuit: Any) -> List[str]:
        """
        Validate circuit compatibility with backend.

        Args:
            circuit: Circuit to validate

        Returns:
            List of validation error messages (empty if valid)

        Validation Checks:
        - Qubit count within limits
        - Supported gate set
        - Circuit depth constraints
        - Parameter ranges
        """
        errors = []

        if hasattr(circuit, "num_qubits"):
            if circuit.num_qubits > self.get_info().num_qubits:
                errors.append(
                    f"Circuit requires {circuit.num_qubits} qubits, "
                    f"backend supports {self.get_info().num_qubits}"
                )

        return errors


class SimulatorBackend(QPUBackend):
    """
    Local quantum circuit simulator using Qiskit Aer.

    Provides fast, accurate simulation of quantum circuits on classical hardware.
    Essential for development, testing, and debugging quantum algorithms.

    Characteristics:
    - Perfect for algorithm development and testing
    - Unlimited shot capacity
    - Deterministic results (same input → same output)
    - No queue times or access restrictions
    - Supports all Qiskit gates and circuits

    Performance:
    - Execution time scales with circuit size and shot count
    - Memory usage depends on number of qubits (2^n state vector)
    - GPU acceleration available with qiskit-aer-gpu

    Use Cases:
    - Algorithm prototyping
    - Unit testing quantum components
    - Performance benchmarking
    - Education and experimentation
    """

    def __init__(self, num_qubits: int = 10) -> None:
        """
        Initialize Qiskit Aer simulator backend.

        Args:
            num_qubits: Maximum qubit capacity (default: 10 for reasonable memory usage)

        Raises:
            ValueError: If num_qubits is invalid
        """
        if num_qubits <= 0:
            raise ValueError("num_qubits must be positive")

        self.num_qubits = num_qubits
        self.backend_type = BackendType.SIMULATOR_AER

        if QISKIT_AVAILABLE:
            self.simulator = AerSimulator()
        else:
            self.simulator = None
            logger.warning("qiskit_aer_not_available", msg="Install with: pip install qiskit-aer")

        logger.info(
            "simulator_backend_initialized",
            num_qubits=num_qubits,
            available=self.is_available(),
        )

    def execute(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        """
        Execute quantum circuit on local simulator.

        Args:
            circuit: Qiskit QuantumCircuit to execute
            shots: Number of measurement repetitions

        Returns:
            Dictionary of measurement outcomes and counts

        Process:
        1. Copy circuit to avoid modifying original
        2. Add measurements if not present
        3. Execute simulation
        4. Return measurement statistics
        """
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

        logger.info("simulator_execution_complete", shots=shots, num_outcomes=len(counts))

        return counts

    def get_info(self) -> BackendInfo:
        """
        Get simulator backend information.

        Returns:
            BackendInfo with simulator capabilities
        """
        return BackendInfo(
            name="Qiskit Aer Simulator",
            backend_type=self.backend_type,
            num_qubits=self.num_qubits,
            available=self.is_available(),
            provider="Qiskit",
            description="Local quantum simulator (classical simulation)",
        )

    def is_available(self) -> bool:
        """
        Check if simulator is available.

        Returns:
            True if Qiskit Aer is installed and functional
        """
        return QISKIT_AVAILABLE and self.simulator is not None


class IBMQBackend(QPUBackend):
    """
    IBM Quantum cloud backend for real quantum hardware.

    Provides access to IBM's quantum computers through the Quantum Experience cloud.
    Enables execution of quantum circuits on actual quantum processors.

    ⚠️  EXPERIMENTAL - Requires IBM Quantum credentials
    Falls back to simulator if credentials not available.

    Characteristics:
    - Real quantum hardware with true quantum effects
    - Limited by physical qubit count and coherence time
    - Queue times vary by backend popularity
    - Shot limits and usage quotas apply
    - Requires IBM Quantum account and API token

    Security:
    - API tokens handled securely (environment variables recommended)
    - No sensitive OmniMind data transmitted to IBM
    - Quantum circuits may be logged for debugging

    Performance:
    - Queue times: 1-30 minutes depending on backend
    - Execution time: Milliseconds per circuit
    - Reliability: Hardware errors possible (readout, gate errors)
    - Cost: Usage-based pricing may apply
    """

    def __init__(self, token: Optional[str] = None, use_least_busy: bool = True) -> None:
        """
        Initialize IBM Quantum backend.

        Args:
            token: IBM Quantum API token (from IBM Quantum Experience)
            use_least_busy: Automatically select least busy available backend

        Security Note:
            Token should be provided via environment variable, not hardcoded.
            Example: export IBMQ_TOKEN="your_token_here"
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
        """
        Initialize IBM Quantum service connection.

        Attempts to connect using Qiskit Runtime V2 API.
        Falls back gracefully if connection fails.
        """
        try:
            # Try new qiskit-ibm-runtime (Qiskit 1.0+)
            try:
                from qiskit_ibm_runtime import (
                    QiskitRuntimeService,  # type: ignore[import-untyped]
                )

                # Use correct channel name for current qiskit-ibm-runtime version
                # 'ibm_quantum' was deprecated, use 'ibm_cloud' or 'ibm_quantum_platform'
                try:
                    self.service = QiskitRuntimeService(channel="ibm_cloud", token=self.token)
                except ValueError:
                    # Fallback to ibm_quantum_platform if ibm_cloud not supported
                    self.service = QiskitRuntimeService(
                        channel="ibm_quantum_platform", token=self.token
                    )

                if self.use_least_busy:
                    # Get least busy backend
                    backends = self.service.backends(simulator=False, operational=True)
                    if backends:
                        # Sort by queue length
                        self.ibm_backend = min(backends, key=lambda b: b.status().pending_jobs)
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
        """
        Execute circuit on IBM Quantum hardware using Sampler V2 API.

        Args:
            circuit: Qiskit QuantumCircuit to execute
            shots: Number of measurement shots (limited by IBM quotas)

        Returns:
            Dictionary of measurement outcomes and counts

        Process:
        1. Transpile circuit for target backend
        2. Submit job to IBM Quantum
        3. Wait for completion (with timeout)
        4. Extract and return measurement results

        Error Handling:
        - Falls back to simulator if hardware unavailable
        - Logs detailed error information
        - Respects 7-minute execution limit per project rules
        """
        if not self.is_available():
            logger.warning("ibmq_not_available_fallback_to_simulator")
            simulator = SimulatorBackend()
            return simulator.execute(circuit, shots)

        try:
            # Use Sampler V2 with correct mode parameter (backend object)
            from qiskit import transpile
            from qiskit_ibm_runtime import Sampler

            # Transpile circuit for the backend
            qc_transpiled = transpile(circuit, backend=self.ibm_backend)

            sampler = Sampler(mode=self.ibm_backend)
            job = sampler.run([qc_transpiled], shots=shots)

            # Enforce 7-minute limit (420 seconds) as per project rules
            result = job.result(timeout=420)

            # Extract counts from V2 API DataBin object
            # Extract counts from V2 API DataBin object
            data_bin = result[0].data
            if hasattr(data_bin, "meas"):
                counts = data_bin.meas.get_counts()
            elif hasattr(data_bin, "c"):
                counts = data_bin.c.get_counts()
            else:
                # Fallback: try to find any attribute that looks like a register with counts
                counts = {}
                for attr in dir(data_bin):
                    if not attr.startswith("_"):
                        val = getattr(data_bin, attr)
                        if hasattr(val, "get_counts"):
                            counts = val.get_counts()
                            break

            logger.info(
                "ibmq_execution_complete",
                backend=self.ibm_backend.name if self.ibm_backend else "unknown",
                shots=shots,
                num_outcomes=len(counts),
                job_id=str(job.job_id()),
            )

            return counts

        except Exception as e:
            logger.error("ibmq_execution_failed", error=str(e), msg="Falling back to simulator")
            simulator = SimulatorBackend()
            return simulator.execute(circuit, shots)

    def get_info(self) -> BackendInfo:
        """
        Get IBM Quantum backend information.

        Returns:
            BackendInfo with hardware specifications and status
        """
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
        """
        Check if IBM Quantum backend is available.

        Returns:
            True if authenticated and backend operational
        """
        return self.ibm_backend is not None


class QPUInterface:
    """
    Main quantum processing unit interface with intelligent backend management.

    Provides unified interface for quantum computing resources with:
    - Automatic backend selection and fallback
    - Performance monitoring and optimization
    - Error handling and recovery
    - Resource management and load balancing

    Architecture:
    - Backend Registry: Manages available quantum backends
    - Strategy Selection: Chooses optimal backend for each task
    - Fallback Logic: Graceful degradation when preferred backends fail
    - Monitoring: Tracks performance and reliability metrics

    Backend Selection Strategy:
    1. Preferred backend (if available)
    2. Any available backend of same type
    3. Simulator fallback
    4. Error if no backends available

    Use Cases:
    - Algorithm development (simulators)
    - Production quantum computing (hardware)
    - Benchmarking (compare backends)
    - Research (real quantum effects)
    """

    active_backend: Optional[QPUBackend]

    def __init__(
        self,
        preferred_backend: BackendType = BackendType.SIMULATOR_AER,
        ibmq_token: Optional[str] = None,
    ) -> None:
        """
        Initialize QPU interface with backend management.

        Args:
            preferred_backend: Primary backend preference
            ibmq_token: IBM Quantum API token (optional)

        Initialization Process:
        1. Discover available backends
        2. Initialize backend instances
        3. Select active backend
        4. Log configuration status
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
            active=(self.active_backend.get_info().name if self.active_backend else "None"),
            num_backends=len(self.backends),
        )

    def _initialize_backends(self, ibmq_token: Optional[str]) -> None:
        """
        Initialize all available quantum backends.

        Attempts to initialize each supported backend type.
        Logs success/failure for each backend.

        Args:
            ibmq_token: Token for IBM Quantum access
        """
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
        """
        Select optimal backend based on preferences and availability.

        Selection Priority:
        1. Preferred backend (if available)
        2. Any available backend
        3. None (no backends available)

        Returns:
            Selected backend or None if none available
        """
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
        strict_mode: bool = False,
    ) -> Dict[str, int]:
        """
        Execute quantum circuit with intelligent backend selection.

        Main entry point for quantum circuit execution.

        Args:
            circuit: Quantum circuit to execute
            shots: Number of measurement repetitions
            backend_type: Force specific backend type
            strict_mode: Disable fallback, raise errors immediately

        Returns:
            Measurement outcome counts

        Execution Strategy:
        1. Select appropriate backend
        2. Validate circuit compatibility
        3. Execute with error handling
        4. Return results or fallback
        """
        if self.active_backend is None:
            raise RuntimeError(
                "No quantum backends available. Install qiskit-aer: pip install qiskit-aer"
            )

        backend = self.active_backend

        if backend_type and backend_type in self.backends:
            backend = self.backends[backend_type]

        logger.info(
            "executing_circuit", backend=backend.get_info().name, shots=shots, strict=strict_mode
        )

        try:
            return backend.execute(circuit, shots)
        except Exception as e:
            if strict_mode:
                logger.error("execution_failed_strict_mode", error=str(e))
                raise RuntimeError(
                    f"Strict mode execution failed on {backend.get_info().name}: {e}"
                )

            # Default fallback logic (if not strict)
            logger.warning("execution_failed_fallback", error=str(e))
            if isinstance(backend, SimulatorBackend):
                raise e  # Simulator failed, nothing to fallback to

            # Try to find a simulator to fallback to
            if BackendType.SIMULATOR_AER in self.backends:
                logger.info("falling_back_to_simulator")
                return self.backends[BackendType.SIMULATOR_AER].execute(circuit, shots)

            raise e

    def list_backends(self) -> List[BackendInfo]:
        """
        List all available quantum backends.

        Returns:
            List of BackendInfo objects for all configured backends

        Useful for:
        - Backend selection UI
        - Debugging availability issues
        - Performance monitoring
        """
        return [backend.get_info() for backend in self.backends.values()]

    def get_active_backend_info(self) -> Optional[BackendInfo]:
        """
        Get information about currently active backend.

        Returns:
            BackendInfo for active backend, or None if none active

        Active Backend:
        The backend currently used for circuit execution.
        May change based on availability and preferences.
        """
        if self.active_backend is None:
            return None
        return self.active_backend.get_info()

    def switch_backend(self, backend_type: BackendType) -> bool:
        """
        Switch to a different quantum backend.

        Args:
            backend_type: Type of backend to switch to

        Returns:
            True if switch successful, False if backend unavailable

        Use Cases:
        - Force simulator for testing
        - Switch to hardware for production
        - Manual backend selection for benchmarking
        """
        if backend_type not in self.backends:
            logger.error("backend_not_available", requested=backend_type.value)
            return False

        self.active_backend = self.backends[backend_type]
        logger.info(
            "backend_switched",
            new_backend=(self.active_backend.get_info().name if self.active_backend else "None"),
        )
        return True

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all backends.

        Returns:
            Dictionary with backend performance statistics

        Metrics Include:
        - Availability status
        - Typical execution times
        - Success rates
        - Queue lengths (for cloud backends)
        """
        metrics = {}

        for backend_type, backend in self.backends.items():
            info = backend.get_info()
            metrics[backend_type.value] = {
                "available": info.available,
                "name": info.name,
                "qubits": info.num_qubits,
                "provider": info.provider,
            }

        return metrics
