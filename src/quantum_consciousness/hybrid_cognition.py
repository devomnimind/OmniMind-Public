"""
Hybrid Cognition System for OmniMind.

Integrates classical and quantum cognition:
- Classical reasoning (existing OmniMind logic)
- Quantum optimization for specific tasks
- Performance comparison and metrics
- Strategy selection
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .qpu_interface import BackendType, QPUInterface

# ...existing code...
from .quantum_cognition import (
    QuantumCognitionEngine,
    QuantumDecisionMaker,
)

# ...existing code...

logger = structlog.get_logger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategy types."""

    CLASSICAL = "classical"
    QUANTUM = "quantum"
    HYBRID = "hybrid"
    AUTO = "auto"  # Automatically select best strategy


@dataclass
class CognitionMetrics:
    """Metrics for cognition performance comparison."""

    strategy: OptimizationStrategy
    execution_time: float
    accuracy: float
    solution_quality: float
    num_iterations: int
    energy_used: float = 0.0
    notes: str = ""

    def speedup_vs(self, other: "CognitionMetrics") -> float:
        """
        Calculate speedup compared to another metric.

        Args:
            other: Other metrics to compare to

        Returns:
            Speedup factor (positive = faster, negative = slower)
        """
        if other.execution_time == 0:
            return 0.0
        return other.execution_time / self.execution_time

    def summary(self) -> str:
        """Generate metrics summary."""
        return (
            f"{self.strategy.value.upper()} Cognition Metrics:\n"
            f"  Execution Time: {self.execution_time:.4f}s\n"
            f"  Accuracy: {self.accuracy:.2%}\n"
            f"  Quality: {self.solution_quality:.2f}\n"
            f"  Iterations: {self.num_iterations}\n"
            f"  Energy: {self.energy_used:.2f} units\n"
            f"  {self.notes}"
        )


@dataclass
class ClassicalQuantumBridge:
    """
    Bridge between classical and quantum reasoning.

    Handles:
    - Data encoding: classical -> quantum
    - Data decoding: quantum -> classical
    - Format conversion
    """

    num_qubits: int = 4
    encoding_method: str = "amplitude"

    def encode_classical_data(self, data: Any) -> Any:
        """
        Encode classical data for quantum processing.

        Args:
            data: Classical data (numbers, vectors, etc.)

        Returns:
            Quantum-encoded data
        """
        logger.debug(
            "encoding_classical_to_quantum",
            data_type=type(data).__name__,
            method=self.encoding_method,
        )

        # For now, pass through
        # In real implementation, would convert to quantum state
        return data

    def decode_quantum_result(self, quantum_result: Any) -> Any:
        """
        Decode quantum result to classical format.

        Args:
            quantum_result: Result from quantum computation

        Returns:
            Classical data
        """
        logger.debug("decoding_quantum_to_classical", result_type=type(quantum_result).__name__)

        # For now, pass through
        return quantum_result

    def validate_compatibility(self, data: Any) -> bool:
        """
        Check if data is compatible with quantum encoding.

        Args:
            data: Data to validate

        Returns:
            True if compatible
        """
        # Check if data can fit in available qubits
        if isinstance(data, (list, tuple)):
            max_size = 2**self.num_qubits
            return len(data) <= max_size

        return True


class HybridCognitionSystem:
    """
    Hybrid classical-quantum cognition system.

    Integrates:
    - Classical reasoning (deterministic, fast, proven)
    - Quantum cognition (probabilistic, parallel, experimental)
    - Automatic strategy selection
    - Performance monitoring
    """

    def __init__(
        self,
        num_qubits: int = 4,
        default_strategy: OptimizationStrategy = OptimizationStrategy.AUTO,
        enable_quantum: bool = True,
    ) -> None:
        """
        Initialize hybrid cognition system.

        Args:
            num_qubits: Number of qubits for quantum operations
            default_strategy: Default optimization strategy
            enable_quantum: Whether to enable quantum operations
        """
        self.num_qubits = num_qubits
        self.default_strategy = default_strategy
        self.enable_quantum = enable_quantum

        # Initialize components
        self.bridge = ClassicalQuantumBridge(num_qubits=num_qubits)

        if enable_quantum:
            try:
                self.quantum_engine = QuantumCognitionEngine(num_qubits=num_qubits)
                self.quantum_decision_maker = QuantumDecisionMaker(num_qubits=num_qubits)
                self.qpu = QPUInterface(preferred_backend=BackendType.SIMULATOR_AER)
                self.quantum_available = True
            except Exception as e:
                logger.warning(
                    "quantum_initialization_failed",
                    error=str(e),
                    msg="Falling back to classical only",
                )
                self.quantum_available = False
        else:
            self.quantum_available = False

        # Metrics history
        self.metrics_history: List[CognitionMetrics] = []

        logger.info(
            "hybrid_cognition_initialized",
            num_qubits=num_qubits,
            quantum_available=self.quantum_available,
            default_strategy=default_strategy.value,
        )

    def solve_optimization(
        self, problem: Dict[str, Any], strategy: Optional[OptimizationStrategy] = None
    ) -> Tuple[Any, CognitionMetrics]:
        """
        Solve optimization problem using specified strategy.

        Args:
            problem: Problem definition with parameters
            strategy: Optimization strategy to use (or use default)

        Returns:
            Tuple of (solution, metrics)
        """
        selected_strategy = strategy or self.default_strategy

        if selected_strategy == OptimizationStrategy.AUTO:
            selected_strategy = self._auto_select_strategy(problem)

        logger.info(
            "solving_optimization",
            strategy=selected_strategy.value,
            problem_type=problem.get("type", "unknown"),
        )

        if selected_strategy == OptimizationStrategy.QUANTUM:
            return self._solve_quantum(problem)
        elif selected_strategy == OptimizationStrategy.CLASSICAL:
            return self._solve_classical(problem)
        else:  # HYBRID
            return self._solve_hybrid(problem)

    def _solve_classical(self, problem: Dict[str, Any]) -> Tuple[Any, CognitionMetrics]:
        """Solve using classical methods."""
        start_time = time.time()

        # Classical greedy solution
        # This is a placeholder - real implementation would use existing OmniMind logic
        solution = self._classical_greedy_search(problem)

        elapsed = time.time() - start_time

        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.CLASSICAL,
            execution_time=elapsed,
            accuracy=0.85,  # Example
            solution_quality=0.80,  # Example
            num_iterations=100,  # Example
            notes="Classical deterministic solution",
        )

        self.metrics_history.append(metrics)

        logger.info(
            "classical_solution_complete",
            time=elapsed,
            quality=metrics.solution_quality,
        )

        return solution, metrics

    def _solve_quantum(self, problem: Dict[str, Any]) -> Tuple[Any, CognitionMetrics]:
        """Solve using quantum methods."""
        if not self.quantum_available:
            logger.warning("quantum_not_available_fallback")
            return self._solve_classical(problem)

        start_time = time.time()

        # Quantum solution using superposition
        solution = self._quantum_superposition_search(problem)

        elapsed = time.time() - start_time

        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.QUANTUM,
            execution_time=elapsed,
            accuracy=0.82,  # Example (may be lower due to probabilistic nature)
            solution_quality=0.85,  # Example (may find better solutions)
            num_iterations=10,  # Example (fewer iterations due to parallelism)
            notes="Quantum superposition solution",
        )

        self.metrics_history.append(metrics)

        logger.info("quantum_solution_complete", time=elapsed, quality=metrics.solution_quality)

        return solution, metrics

    def _solve_hybrid(self, problem: Dict[str, Any]) -> Tuple[Any, CognitionMetrics]:
        """Solve using hybrid approach."""
        start_time = time.time()

        # Hybrid: Use quantum for exploration, classical for refinement

        # 1. Quantum exploration
        if self.quantum_available:
            quantum_candidates = self._quantum_explore(problem)
        else:
            quantum_candidates = []

        # 2. Classical refinement
        solution = self._classical_refine(problem, quantum_candidates)

        elapsed = time.time() - start_time

        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.HYBRID,
            execution_time=elapsed,
            accuracy=0.90,  # Example (best of both)
            solution_quality=0.88,  # Example
            num_iterations=50,  # Example
            notes="Hybrid quantum exploration + classical refinement",
        )

        self.metrics_history.append(metrics)

        logger.info("hybrid_solution_complete", time=elapsed, quality=metrics.solution_quality)

        return solution, metrics

    def _auto_select_strategy(self, problem: Dict[str, Any]) -> OptimizationStrategy:
        """Automatically select best strategy for problem."""
        problem_size = problem.get("size", 0)
        problem_type = problem.get("type", "unknown")

        # Heuristic selection
        if not self.quantum_available:
            return OptimizationStrategy.CLASSICAL

        # Small problems: classical is faster
        if problem_size < 10:
            return OptimizationStrategy.CLASSICAL

        # Large search spaces: quantum may help
        if problem_size > 100:
            return OptimizationStrategy.HYBRID

        # For specific problem types
        if problem_type in ["combinatorial", "search"]:
            return OptimizationStrategy.QUANTUM

        # Default to hybrid
        return OptimizationStrategy.HYBRID

    def _classical_greedy_search(self, problem: Dict[str, Any]) -> Any:
        """Classical greedy search (placeholder)."""
        # This would integrate with existing OmniMind classical reasoning
        return {"solution": "classical_result", "value": 0.80}

    def _quantum_superposition_search(self, problem: Dict[str, Any]) -> Any:
        """Quantum superposition search."""
        # Use quantum decision maker for exploration
        options = problem.get("options", ["option_0", "option_1", "option_2"])

        decision = self.quantum_decision_maker.make_decision(options[: min(len(options), 8)])
        result = decision.collapse()

        return {"solution": result, "value": 0.85}

    def _quantum_explore(self, problem: Dict[str, Any]) -> List[Any]:
        """Quantum exploration phase."""
        # Use quantum for parallel exploration
        candidates = []
        for _ in range(5):  # Generate multiple candidates
            options = problem.get("options", ["opt_0", "opt_1"])
            decision = self.quantum_decision_maker.make_decision(options[: min(len(options), 8)])
            candidates.append(decision.collapse())
        return candidates

    def _classical_refine(self, problem: Dict[str, Any], candidates: List[Any]) -> Any:
        """Classical refinement phase."""
        # Pick best candidate and refine
        if candidates:
            best = candidates[0]
        else:
            best = "classical_fallback"

        return {"solution": best, "value": 0.88}

    def compare_strategies(
        self,
        problem: Dict[str, Any],
        strategies: Optional[List[OptimizationStrategy]] = None,
    ) -> Dict[OptimizationStrategy, CognitionMetrics]:
        """
        Compare multiple strategies on same problem.

        Args:
            problem: Problem to solve
            strategies: List of strategies to compare (or compare all)

        Returns:
            Dictionary mapping strategy to metrics
        """
        if strategies is None:
            strategies = [
                OptimizationStrategy.CLASSICAL,
                OptimizationStrategy.QUANTUM,
                OptimizationStrategy.HYBRID,
            ]

        results = {}

        for strategy in strategies:
            _, metrics = self.solve_optimization(problem, strategy=strategy)
            results[strategy] = metrics

        logger.info("strategy_comparison_complete", num_strategies=len(strategies))

        return results

    def get_metrics_summary(self) -> str:
        """Get summary of all metrics."""
        if not self.metrics_history:
            return "No metrics recorded yet"

        summary = "=== Hybrid Cognition Metrics Summary ===\n\n"

        for i, metrics in enumerate(self.metrics_history):
            summary += f"Run {i + 1}:\n{metrics.summary()}\n\n"

        return summary
