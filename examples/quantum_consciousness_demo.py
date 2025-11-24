#!/usr/bin/env python3
"""
Example: Quantum Consciousness Module Demo

Demonstrates the key features of the quantum consciousness module
without requiring Qiskit installation (uses graceful fallback).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.quantum_consciousness import (
    QuantumDecisionMaker,
    QuantumMemorySystem,
    HybridCognitionSystem,
    OptimizationStrategy,
    QPUInterface,
)


def demo_quantum_decision_making():
    """Demonstrate quantum decision making."""
    print("\n" + "=" * 60)
    print("1. QUANTUM DECISION MAKING")
    print("=" * 60)

    maker = QuantumDecisionMaker(num_qubits=3)
    options = ["refactor_code", "optimize_performance", "add_feature", "fix_bug"]

    print(f"\nOptions: {options}")
    decision = maker.make_decision(options)

    print(f"\nQuantum State Probabilities:")
    for opt, prob in decision.probabilities.items():
        print(f"  {opt}: {prob:.2%}")

    # Collapse to single decision
    final = decision.collapse()
    print(f"\n✅ Final Decision: {final} (confidence: {decision.confidence:.2%})")


def demo_quantum_memory():
    """Demonstrate quantum memory system."""
    print("\n" + "=" * 60)
    print("2. QUANTUM MEMORY SYSTEM")
    print("=" * 60)

    memory = QuantumMemorySystem(num_qubits=4, capacity=10)

    # Store patterns
    patterns = {
        "pattern_1": [1.0, 2.0, 3.0, 4.0],
        "pattern_2": [1.1, 2.1, 3.0, 4.0],  # Similar to pattern_1
        "pattern_3": [5.0, 6.0, 7.0, 8.0],  # Different
    }

    print("\nStoring patterns in quantum memory...")
    for name, data in patterns.items():
        idx = memory.store(data=data, key=name)
        print(f"  {name}: stored at index {idx}")

    # Search for similar patterns
    query = [1.05, 2.05, 3.0, 4.0]
    print(f"\nSearching for patterns similar to: {query}")
    matches = memory.search_similar(query, threshold=0.8)
    print(f"Found {len(matches)} matching memories: {matches}")


def demo_hybrid_cognition():
    """Demonstrate hybrid classical-quantum cognition."""
    print("\n" + "=" * 60)
    print("3. HYBRID COGNITION SYSTEM")
    print("=" * 60)

    system = HybridCognitionSystem(
        num_qubits=4, default_strategy=OptimizationStrategy.AUTO
    )

    # Small problem - should use classical
    small_problem = {"type": "simple", "size": 5, "options": ["a", "b", "c"]}

    print("\nSolving SMALL optimization problem...")
    solution, metrics = system.solve_optimization(small_problem)
    print(f"  Strategy: {metrics.strategy.value}")
    print(f"  Time: {metrics.execution_time:.4f}s")
    print(f"  Quality: {metrics.solution_quality:.2%}")

    # Large problem - should use hybrid
    large_problem = {"type": "complex", "size": 150, "options": ["x", "y", "z"]}

    print("\nSolving LARGE optimization problem...")
    solution, metrics = system.solve_optimization(large_problem)
    print(f"  Strategy: {metrics.strategy.value}")
    print(f"  Time: {metrics.execution_time:.4f}s")
    print(f"  Quality: {metrics.solution_quality:.2%}")

    # Compare strategies
    print("\nComparing all strategies on medium problem...")
    medium_problem = {"type": "test", "size": 50, "options": ["1", "2", "3", "4"]}

    results = system.compare_strategies(medium_problem)
    for strategy, metric in results.items():
        print(
            f"  {strategy.value.upper():12} - "
            f"Time: {metric.execution_time:.4f}s, "
            f"Quality: {metric.solution_quality:.2%}"
        )


def demo_qpu_interface():
    """Demonstrate QPU interface."""
    print("\n" + "=" * 60)
    print("4. QPU INTERFACE")
    print("=" * 60)

    qpu = QPUInterface()

    print("\nAvailable backends:")
    backends = qpu.list_backends()
    if backends:
        for backend_info in backends:
            print(f"  {backend_info}")
    else:
        print("  ⚠️  No quantum backends available")
        print("  Install Qiskit: pip install qiskit qiskit-aer")

    active = qpu.get_active_backend_info()
    if active:
        print(f"\n✅ Active backend: {active.name}")
    else:
        print("\n⚠️  No active backend (Qiskit not installed)")


def main():
    """Run all demos."""
    print("\n" + "🧠" * 30)
    print("QUANTUM CONSCIOUSNESS MODULE - DEMO")
    print("🧠" * 30)

    try:
        demo_quantum_decision_making()
        demo_quantum_memory()
        demo_hybrid_cognition()
        demo_qpu_interface()

        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETE")
        print("=" * 60)
        print("\n📚 For more information, see:")
        print("   docs/research/quantum_consciousness_research.md")
        print("\n⚠️  Note: This is an EXPERIMENTAL module")
        print("   Real quantum advantage requires IBM Quantum access")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
