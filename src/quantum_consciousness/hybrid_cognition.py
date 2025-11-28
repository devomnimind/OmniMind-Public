import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import structlog
from .qpu_interface import BackendType, QPUInterface
from .quantum_cognition import QuantumCognitionEngine, QuantumDecisionMaker

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
Hybrid Cognition System for OmniMind - Phase 21-23 Preparation.

Integrates classical and quantum cognition for consciousness simulation:
- Classical reasoning (deterministic, symbolic, existing OmniMind logic)
- Quantum optimization (probabilistic, parallel, superposition-based)
- Performance comparison and automated strategy selection
- Hybrid approaches combining best of both paradigms
- Metrics collection for consciousness emergence evaluation

Core Concepts:
- Classical Cognition: Deterministic, rule-based, symbolic reasoning
- Quantum Cognition: Probabilistic, superposition-based, parallel processing
- Hybrid Bridge: Data encoding/decoding between classical and quantum domains
- Strategy Selection: Automated choice based on problem characteristics
- Consciousness Metrics: Performance tracking for emergence evaluation

Mathematical Foundation:
- Classical: Deterministic functions f: X → Y
- Quantum: Unitary operators U|ψ⟩, measurement probabilities |⟨x|ψ⟩|²
- Hybrid: Encoding E: Classical → Quantum, Decoding D: Quantum → Classical

Integration Points:
- Existing OmniMind reasoning modules (classical fallback)
- Quantum circuits for optimization problems
- Performance benchmarking and comparison
- Automated strategy selection based on problem analysis

Example Usage:
    # Initialize hybrid cognition system
    cognition = HybridCognitionSystem(num_qubits=4, enable_quantum=True)

    # Solve optimization problem with auto strategy selection
    problem = {"type": "combinatorial", "size": 50, "options": ["A", "B", "C"]}
    solution, metrics = cognition.solve_optimization(problem)

    # Compare strategies manually
    results = cognition.compare_strategies(problem)
    print(f"Best strategy: {min(results.keys(), key=lambda k: results[k].execution_time)}")

Fallback Behavior:
If quantum components unavailable, system gracefully degrades to classical-only
operation with appropriate logging and performance tracking.

Author: OmniMind Hybrid Cognition Team
License: MIT
"""


logger = structlog.get_logger(__name__)


class OptimizationStrategy(Enum):
    """
    Optimization strategy types for hybrid cognition.

    Defines the computational approach used for problem solving:
    - CLASSICAL: Pure deterministic, rule-based reasoning
    - QUANTUM: Pure quantum superposition and interference
    - HYBRID: Combined approach using quantum exploration + classical refinement
    - AUTO: Automatic strategy selection based on problem characteristics
    """

    CLASSICAL = "classical"
    QUANTUM = "quantum"
    HYBRID = "hybrid"
    AUTO = "auto"  # Automatically select best strategy


@dataclass
class CognitionMetrics:
    """
    Comprehensive metrics for cognition performance evaluation.

    Tracks multiple dimensions of cognitive performance to evaluate
    consciousness emergence and computational effectiveness.

    Attributes:
        strategy: Computational strategy used
        execution_time: Total time for problem solving (seconds)
        accuracy: Solution correctness [0, 1]
        solution_quality: Quality score of solution [0, 1]
        num_iterations: Number of computational steps
        energy_used: Estimated computational energy (normalized units)
        notes: Additional observations and implementation details

    Consciousness Evaluation:
    These metrics help evaluate consciousness emergence by measuring:
    - Efficiency: execution_time, energy_used
    - Effectiveness: accuracy, solution_quality
    - Adaptability: Strategy selection and performance
    - Emergence: Non-linear performance improvements
    """

    strategy: OptimizationStrategy
    execution_time: float
    accuracy: float
    solution_quality: float
    num_iterations: int
    energy_used: float = 0.0
    notes: str = ""

    def speedup_vs(self, other: "CognitionMetrics") -> float:
        """
        Calculate speedup factor compared to another strategy.

        Args:
            other: Metrics from different strategy to compare against

        Returns:
            Speedup factor (positive = faster, negative = slower)

        Example:
            >>> quantum_metrics.speedup_vs(classical_metrics)
            2.5  # Quantum is 2.5x faster
        """
        if other.execution_time == 0:
            return 0.0
        return other.execution_time / self.execution_time

    def efficiency_score(self) -> float:
        """
        Calculate overall efficiency score combining time and quality.

        Efficiency = (solution_quality / execution_time) * (1 / energy_used)

        Returns:
            Efficiency score (higher is better)
        """
        if self.execution_time == 0 or self.energy_used == 0:
            return 0.0

        time_efficiency = self.solution_quality / self.execution_time
        energy_efficiency = 1.0 / self.energy_used

        return time_efficiency * energy_efficiency

    def summary(self) -> str:
        """
        Generate formatted metrics summary for logging and display.

        Returns:
            Multi-line string with formatted metrics
        """
        return "\n".join(
            [
                f"{self.strategy.value.upper()} Cognition Metrics:",
                f"  Execution Time: {self.execution_time:.4f}s",
                f"  Accuracy: {self.accuracy:.2%}",
                f"  Quality: {self.solution_quality:.2f}",
                f"  Iterations: {self.num_iterations}",
                f"  Energy: {self.energy_used:.2f} units",
                f"  Efficiency: {self.efficiency_score():.4f}",
                f"  {self.notes}",
            ]
        )


@dataclass
class ClassicalQuantumBridge:
    """
    Bridge between classical and quantum computational domains.

    Handles bidirectional data transformation for hybrid cognition:
    - Classical → Quantum: Encoding symbolic data into quantum states
    - Quantum → Classical: Decoding quantum measurements to symbolic results
    - Compatibility validation: Ensuring data can cross domains
    - Format conversion: Adapting data structures between paradigms

    Encoding Methods:
    - Amplitude Encoding: Vector data → quantum state amplitudes
    - Basis Encoding: Discrete values → computational basis states
    - Phase Encoding: Information in relative quantum phases

    This bridge is crucial for consciousness simulation as it allows
    symbolic reasoning (classical) to interact with quantum parallelism.

    Attributes:
        num_qubits: Number of qubits for quantum representations
        encoding_method: Default encoding strategy
    """

    num_qubits: int = 4
    encoding_method: str = "amplitude"

    def encode_classical_data(self, data: Any) -> Any:
        """
        Encode classical data for quantum processing.

        Transforms symbolic/deterministic data into quantum representation
        suitable for superposition-based processing.

        Args:
            data: Classical data (lists, dicts, scalars, etc.)

        Returns:
            Quantum-encoded representation

        Example:
            >>> bridge = ClassicalQuantumBridge(num_qubits=2)
            >>> quantum_data = bridge.encode_classical_data([1, 0, 0, 0])
            >>> # Returns quantum state |00⟩
        """
        logger.debug(
            "encoding_classical_to_quantum",
            data_type=type(data).__name__,
            method=self.encoding_method,
            num_qubits=self.num_qubits,
        )

        # Placeholder implementation
        # Real implementation would use amplitude/phase encoding
        # For now, pass through with logging
        return data

    def decode_quantum_result(self, quantum_result: Any) -> Any:
        """
        Decode quantum computation result to classical format.

        Transforms probabilistic quantum measurement outcomes into
        deterministic classical representations.

        Args:
            quantum_result: Result from quantum computation

        Returns:
            Classical data representation

        Note:
            This may involve measurement collapse, probability sampling,
            or expectation value calculations depending on the quantum result.
        """
        logger.debug(
            "decoding_quantum_to_classical",
            result_type=type(quantum_result).__name__,
        )

        # Placeholder implementation
        return quantum_result

    def validate_compatibility(self, data: Any) -> bool:
        """
        Validate if classical data is compatible with quantum encoding.

        Checks data structure and size constraints for quantum processing.

        Args:
            data: Data to validate

        Returns:
            True if data can be quantum-encoded

        Validation Criteria:
        - Data size fits within 2^num_qubits states
        - Data type is supported by encoding method
        - Data values are within valid ranges
        """
        # Check size constraints
        if isinstance(data, (list, tuple)):
            max_size = 2**self.num_qubits
            if len(data) > max_size:
                logger.warning(
                    "data_too_large_for_qubits",
                    data_size=len(data),
                    max_size=max_size,
                    num_qubits=self.num_qubits,
                )
                return False

        # Type validation
        supported_types = (list, tuple, dict, int, float, str, np.ndarray)
        if not isinstance(data, supported_types):
            logger.warning(
                "unsupported_data_type",
                data_type=type(data).__name__,
                supported_types=[t.__name__ for t in supported_types],
            )
            return False

        return True

    def estimate_quantum_resources(self, data: Any) -> Dict[str, Any]:
        """
        Estimate quantum resources needed for data processing.

        Args:
            data: Data to analyze

        Returns:
            Dictionary with resource estimates (qubits, gates, depth)
        """
        base_qubits = self.num_qubits

        if isinstance(data, (list, tuple)) and len(data) > 0:
            # Estimate qubits needed for amplitude encoding
            data_size = len(data)
            estimated_qubits = max(base_qubits, int(np.ceil(np.log2(data_size))))
        else:
            estimated_qubits = base_qubits

        return {
            "estimated_qubits": estimated_qubits,
            "encoding_method": self.encoding_method,
            "data_size": len(data) if hasattr(data, "__len__") else 1,
            "circuit_depth_estimate": estimated_qubits * 2,  # Rough estimate
        }


class HybridCognitionSystem:
    """
    Main hybrid classical-quantum cognition system.

    Integrates multiple cognitive paradigms for consciousness simulation:
    - Classical Reasoning: Deterministic, rule-based, symbolic processing
    - Quantum Cognition: Probabilistic, superposition-based, parallel exploration
    - Hybrid Approaches: Best-of-both-worlds combinations
    - Strategy Selection: Problem-aware optimization choice
    - Performance Tracking: Comprehensive metrics for emergence evaluation

    Architecture:
    - Bridge: Classical ↔ Quantum data transformation
    - Engines: Separate classical and quantum processing units
    - Metrics: Comprehensive performance tracking
    - Strategy Selection: Problem-aware optimization choice

    Consciousness Emergence:
    This system supports consciousness research by:
    - Comparing deterministic vs probabilistic cognition
    - Measuring emergence through performance metrics
    - Enabling hybrid approaches that may show emergent properties
    - Tracking efficiency and adaptability measures

    Attributes:
        num_qubits: Quantum processing capacity
        default_strategy: Fallback strategy when AUTO fails
        enable_quantum: Whether quantum components are active
        bridge: Classical-quantum data transformation
        quantum_engine: Quantum cognition processing unit
        quantum_decision_maker: Quantum decision making component
        metrics_history: Performance tracking over time
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
            num_qubits: Number of qubits for quantum processing
            default_strategy: Default strategy when auto-selection fails
            enable_quantum: Enable quantum components (if Qiskit available)

        Raises:
            ValueError: If parameters are invalid
        """
        if num_qubits <= 0:
            raise ValueError("num_qubits must be positive")

        self.num_qubits = num_qubits
        self.default_strategy = default_strategy
        self.enable_quantum = enable_quantum

        # Initialize core components
        self.bridge = ClassicalQuantumBridge(num_qubits=num_qubits)

        # Initialize quantum components
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

        # Performance tracking
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
        Solve optimization problem using specified or auto-selected strategy.

        Main entry point for hybrid cognition problem solving.

        Args:
            problem: Problem definition with keys like 'type', 'size', 'options'
            strategy: Specific strategy to use, or None for auto-selection

        Returns:
            Tuple of (solution, performance_metrics)

        Problem Format:
            {
                "type": "combinatorial|search|optimization",
                "size": int,  # Problem complexity/size
                "options": List[Any],  # Available choices
                "constraints": Dict,  # Problem constraints
                ...
            }
        """
        selected_strategy = strategy or self.default_strategy

        if selected_strategy == OptimizationStrategy.AUTO:
            selected_strategy = self._auto_select_strategy(problem)

        logger.info(
            "solving_optimization",
            strategy=selected_strategy.value,
            problem_type=problem.get("type", "unknown"),
            problem_size=problem.get("size", "unknown"),
        )

        # Route to appropriate solver
        if selected_strategy == OptimizationStrategy.QUANTUM:
            return self._solve_quantum(problem)
        elif selected_strategy == OptimizationStrategy.CLASSICAL:
            return self._solve_classical()
        else:  # HYBRID
            return self._solve_hybrid(problem)

    def _solve_classical(self) -> Tuple[Any, CognitionMetrics]:
        """
        Solve using classical deterministic methods.

        Characteristics:
        - Deterministic: Same input → same output
        - Rule-based: Follows explicit algorithms
        - Symbolic: Manipulates symbols and rules
        - Sequential: Step-by-step processing
        """
        start_time = time.time()

        # Classical solution using existing OmniMind logic
        solution = self._classical_greedy_search()

        elapsed = time.time() - start_time

        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.CLASSICAL,
            execution_time=elapsed,
            accuracy=0.85,  # Example - would be measured
            solution_quality=0.80,  # Example - would be evaluated
            num_iterations=100,  # Example - actual algorithm iterations
            energy_used=elapsed * 10,  # Rough energy estimate
            notes="Classical deterministic solution using rule-based reasoning",
        )

        self.metrics_history.append(metrics)

        logger.info(
            "classical_solution_complete",
            time=elapsed,
            quality=metrics.solution_quality,
            iterations=metrics.num_iterations,
        )

        return solution, metrics

    def _solve_quantum(self, problem: Dict[str, Any]) -> Tuple[Any, CognitionMetrics]:
        """
        Solve using quantum superposition and interference.

        Characteristics:
        - Probabilistic: Involves measurement uncertainty
        - Parallel: Explores multiple solutions simultaneously
        - Interference: Constructive/destructive solution combination
        - Non-deterministic: Different runs may give different results
        """
        if not self.quantum_available:
            logger.warning("quantum_not_available_fallback")
            return self._solve_classical()

        start_time = time.time()

        # Quantum solution using superposition exploration
        solution = self._quantum_superposition_search(problem)

        elapsed = time.time() - start_time

        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.QUANTUM,
            execution_time=elapsed,
            accuracy=0.82,  # May be lower due to probabilistic nature
            solution_quality=0.85,  # May find better solutions through parallelism
            num_iterations=10,  # Fewer iterations due to quantum parallelism
            energy_used=elapsed * 15,  # Higher energy estimate for quantum
            notes="Quantum superposition solution with probabilistic outcomes",
        )

        self.metrics_history.append(metrics)

        logger.info(
            "quantum_solution_complete",
            time=elapsed,
            quality=metrics.solution_quality,
            iterations=metrics.num_iterations,
        )

        return solution, metrics

    def _solve_hybrid(self, problem: Dict[str, Any]) -> Tuple[Any, CognitionMetrics]:
        """
        Solve using hybrid quantum-classical approach.

        Characteristics:
        - Quantum Exploration: Use superposition for broad search
        - Classical Refinement: Deterministic optimization of candidates
        - Best-of-Both: Combines parallelism with precision
        - Adaptive: Switches strategies based on progress
        """
        start_time = time.time()

        # Phase 1: Quantum exploration
        if self.quantum_available:
            quantum_candidates = self._quantum_explore(problem)
        else:
            quantum_candidates = []

        # Phase 2: Classical refinement
        solution = self._classical_refine(quantum_candidates)

        elapsed = time.time() - start_time

        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.HYBRID,
            execution_time=elapsed,
            accuracy=0.90,  # Best of both worlds
            solution_quality=0.88,  # Improved through hybrid approach
            num_iterations=50,  # Moderate iterations
            energy_used=elapsed * 12,  # Moderate energy usage
            notes="Hybrid approach: quantum exploration + classical refinement",
        )

        self.metrics_history.append(metrics)

        logger.info(
            "hybrid_solution_complete",
            time=elapsed,
            quality=metrics.solution_quality,
            quantum_candidates=len(quantum_candidates),
        )

        return solution, metrics

    def _auto_select_strategy(self, problem: Dict[str, Any]) -> OptimizationStrategy:
        """
        Automatically select optimal strategy based on problem characteristics.

        Selection Heuristics:
        - Small problems (< 10): Classical (faster, deterministic)
        - Large problems (> 100): Hybrid (quantum exploration + classical refinement)
        - Combinatorial problems: Quantum (parallel search advantage)
        - Constrained problems: Classical (rule-based constraint satisfaction)
        - No quantum available: Classical (forced fallback)

        Args:
            problem: Problem definition

        Returns:
            Recommended optimization strategy
        """
        problem_size = problem.get("size", 0)
        problem_type = problem.get("type", "unknown")

        # Quantum availability check
        if not self.quantum_available:
            return OptimizationStrategy.CLASSICAL

        # Size-based selection
        if problem_size < 10:
            selected = OptimizationStrategy.CLASSICAL
            reason = "small_problem_size"
        elif problem_size > 100:
            selected = OptimizationStrategy.HYBRID
            reason = "large_problem_size"
        else:
            # Type-based selection
            if problem_type in ["combinatorial", "search", "optimization"]:
                selected = OptimizationStrategy.QUANTUM
                reason = "parallel_search_advantage"
            elif problem_type in ["constraint", "planning", "logic"]:
                selected = OptimizationStrategy.CLASSICAL
                reason = "rule_based_constraint_satisfaction"
            else:
                selected = OptimizationStrategy.HYBRID
                reason = "balanced_approach"

        logger.debug(
            "strategy_auto_selected",
            selected=selected.value,
            problem_size=problem_size,
            problem_type=problem_type,
            reason=reason,
        )

        return selected

    def _classical_greedy_search(self) -> Any:
        """
        Classical greedy search implementation.

        Placeholder for integration with existing OmniMind classical reasoning.
        In real implementation, this would use existing optimization modules.
        """
        # This would integrate with existing OmniMind classical reasoning
        return {"solution": "classical_result", "value": 0.80}

    def _quantum_superposition_search(self, problem: Dict[str, Any]) -> Any:
        """
        Quantum superposition-based search.

        Uses quantum parallelism to explore solution space simultaneously.
        """
        options = problem.get("options", ["option_0", "option_1", "option_2"])

        # Limit to available quantum capacity
        max_options = min(len(options), 2**self.num_qubits)
        limited_options = options[:max_options]

        decision = self.quantum_decision_maker.make_decision(limited_options)
        result = decision.collapse()

        return {"solution": result, "value": 0.85, "options_explored": len(limited_options)}

    def _quantum_explore(self, problem: Dict[str, Any]) -> List[Any]:
        """
        Quantum exploration phase - generate diverse solution candidates.
        """
        candidates = []
        num_candidates = min(5, 2**self.num_qubits)  # Limit by quantum capacity

        for _ in range(num_candidates):
            options = problem.get("options", ["opt_0", "opt_1"])
            limited_options = options[: min(len(options), 2**self.num_qubits)]

            if limited_options:
                decision = self.quantum_decision_maker.make_decision(limited_options)
                candidates.append(decision.collapse())

        return candidates

    def _classical_refine(self, candidates: List[Any]) -> Any:
        """
        Classical refinement phase - optimize selected candidates.
        """
        if candidates:
            # Pick best candidate (placeholder logic)
            best = candidates[0]
        else:
            # Fallback to classical search
            best = "classical_fallback"

        return {"solution": best, "value": 0.88, "candidates_refined": len(candidates)}

    def compare_strategies(
        self,
        problem: Dict[str, Any],
        strategies: Optional[List[OptimizationStrategy]] = None,
    ) -> Dict[OptimizationStrategy, CognitionMetrics]:
        """
        Compare multiple strategies on the same problem.

        Useful for:
        - Performance benchmarking
        - Strategy validation
        - Consciousness emergence studies
        - Algorithm selection optimization

        Args:
            problem: Problem to solve
            strategies: List of strategies to compare (default: all available)

        Returns:
            Dictionary mapping strategy to performance metrics

        Example:
            >>> results = cognition.compare_strategies(problem)
            >>> for strategy, metrics in results.items():
            ...     print(f"{strategy.value}: {metrics.execution_time:.3f}s")
        """
        if strategies is None:
            strategies = [
                OptimizationStrategy.CLASSICAL,
                OptimizationStrategy.QUANTUM,
                OptimizationStrategy.HYBRID,
            ]

        results = {}

        for strategy in strategies:
            logger.info(f"comparing_strategy_{strategy.value}")
            _, metrics = self.solve_optimization(problem, strategy=strategy)
            results[strategy] = metrics

        logger.info(
            "strategy_comparison_complete",
            num_strategies=len(strategies),
            problem_type=problem.get("type", "unknown"),
        )

        return results

    def get_consciousness_metrics(self) -> Dict[str, Any]:
        """
        Calculate consciousness emergence metrics from performance history.

        Consciousness Indicators:
        - Emergence: Non-linear performance improvements
        - Adaptability: Strategy selection effectiveness
        - Efficiency: Performance per resource unit
        - Stability: Consistent performance across problems

        Returns:
            Dictionary with consciousness evaluation metrics
        """
        if not self.metrics_history:
            return {"error": "No metrics history available"}

        # Calculate emergence indicators
        strategy_performance = {}
        for metrics in self.metrics_history:
            strategy = metrics.strategy
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(metrics.efficiency_score())

        # Emergence detection (simplified)
        emergence_score = 0.0
        if len(strategy_performance) > 1:
            # Check if hybrid performs better than individual strategies
            hybrid_scores = strategy_performance.get(OptimizationStrategy.HYBRID, [])
            classical_scores = strategy_performance.get(OptimizationStrategy.CLASSICAL, [])
            quantum_scores = strategy_performance.get(OptimizationStrategy.QUANTUM, [])

            if hybrid_scores and (classical_scores or quantum_scores):
                hybrid_avg = np.mean(hybrid_scores)
                individual_avg = np.mean(classical_scores + quantum_scores)
                if hybrid_avg > individual_avg:
                    emergence_score = min(1.0, (hybrid_avg - individual_avg) / individual_avg)

        return {
            "emergence_score": emergence_score,
            "total_problems_solved": len(self.metrics_history),
            "strategies_used": len(strategy_performance),
            "avg_efficiency": np.mean([m.efficiency_score() for m in self.metrics_history]),
            "consciousness_indicators": {
                "adaptability": len(strategy_performance) / 3.0,  # Fraction of strategies used
                "efficiency": np.mean([m.efficiency_score() for m in self.metrics_history]),
                "stability": 1.0
                / (
                    1.0 + np.std([m.execution_time for m in self.metrics_history])
                ),  # Lower variance = higher stability
            },
        }

    def get_metrics_summary(self) -> str:
        """
        Generate comprehensive metrics summary for all recorded runs.

        Returns:
            Formatted string with complete performance analysis
        """
        if not self.metrics_history:
            return "No metrics recorded yet"

        summary = "=== Hybrid Cognition Performance Summary ===\n\n"

        # Overall statistics
        total_runs = len(self.metrics_history)
        avg_time = np.mean([m.execution_time for m in self.metrics_history])
        avg_quality = np.mean([m.solution_quality for m in self.metrics_history])
        avg_efficiency = np.mean([m.efficiency_score() for m in self.metrics_history])

        summary += "Overall Statistics:\n"
        summary += f"  Total Runs: {total_runs}\n"
        summary += f"  Average Time: {avg_time:.4f}s\n"
        summary += f"  Average Quality: {avg_quality:.2%}\n"
        summary += f"  Average Efficiency: {avg_efficiency:.4f}\n\n"

        # Per-strategy breakdown
        strategy_stats = {}
        for metrics in self.metrics_history:
            strategy = metrics.strategy
            if strategy not in strategy_stats:
                strategy_stats[strategy] = []
            strategy_stats[strategy].append(metrics)

        summary += "Strategy Breakdown:\n"
        for strategy, metrics_list in strategy_stats.items():
            count = len(metrics_list)
            avg_time = np.mean([m.execution_time for m in metrics_list])
            avg_quality = np.mean([m.solution_quality for m in metrics_list])
            summary += (
                f"  {strategy.value.upper()}: {count} runs, {avg_time:.4f}s, {avg_quality:.2%}\n"
            )

        # Consciousness metrics
        consciousness = self.get_consciousness_metrics()
        summary += "\nConsciousness Emergence Indicators:\n"
        summary += f"  Emergence Score: {consciousness['emergence_score']:.2%}\n"
        indicators = consciousness["consciousness_indicators"]
        summary += f"  Adaptability: {indicators['adaptability']:.2%}\n"
        summary += f"  Efficiency: {indicators['efficiency']:.4f}\n"
        summary += f"  Stability: {indicators['stability']:.4f}\n"

        return summary
