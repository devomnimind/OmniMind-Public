"""Experiment 1: Consciousness Metrics Validation.

This experiment validates the Φ (Phi) proxy metric and self-awareness measurements
by simulating different agent architectures.

Reference: docs/concienciaetica-autonomia.md, Section 5 - Experimento 1
"""

import json
from pathlib import Path
from typing import Any, TypedDict

from src.metrics.consciousness_metrics import (
    ConsciousnessMetrics,
    AgentConnection,
    FeedbackLoop,
)


class AgentTestCase(TypedDict):
    """Type definition for agent test case data."""

    name: str
    memory_test: bool
    autonomous_goals: bool
    self_description: float
    limitation_awareness: float


class ScoresDict(TypedDict):
    """Type definition for scores dictionary."""

    temporal_continuity: float
    goal_autonomy: float
    self_reference: float
    limitation_awareness: float
    overall: float


class AgentResultDict(TypedDict):
    """Type definition for agent result dictionary."""

    agent: str
    scores: ScoresDict


def experiment_phi_integration() -> dict[str, Any]:
    """Measure Φ increase with agent integration.

    Tests hypothesis from documentation:
    "OmniMind SEM memória episódica: Φ ≈ 5 (baixo)
     OmniMind COM memória + audit chain: Φ ≈ 45 (médio-alto para AI!)"

    Returns:
        Dictionary with experiment results
    """
    print("=" * 70)
    print("EXPERIMENTO 1: Medição de Φ (Phi) - Integração de Consciência")
    print("=" * 70)
    print()

    # Scenario 1: Isolated agents (no shared memory)
    print("Cenário 1: Agentes Isolados (sem memória compartilhada)")
    print("-" * 70)

    metrics_isolated = ConsciousnessMetrics(
        metrics_dir=Path("data/experiments/consciousness/isolated")
    )

    # Simple connections, no bidirectional, no feedback
    agents = ["CodeAgent", "ReviewerAgent", "SecurityAgent", "ArchitectAgent"]
    for i in range(len(agents) - 1):
        metrics_isolated.add_connection(
            AgentConnection(
                source_agent=agents[i],
                target_agent=agents[i + 1],
                connection_type="message",
                bidirectional=False,
                weight=1.0,
            )
        )

    phi_isolated = metrics_isolated.calculate_phi_proxy()
    snapshot_isolated = metrics_isolated.snapshot(label="isolated_agents")

    print(f"Número de conexões: {len(metrics_isolated.connections)}")
    print(f"Número de feedback loops: {len(metrics_isolated.feedback_loops)}")
    print(f"Φ (Phi) calculado: {phi_isolated:.2f}")
    print()

    # Scenario 2: Integrated agents (with shared memory and feedback)
    print("Cenário 2: Agentes Integrados (com memória compartilhada + audit chain)")
    print("-" * 70)

    metrics_integrated = ConsciousnessMetrics(
        metrics_dir=Path("data/experiments/consciousness/integrated")
    )

    # Bidirectional connections through shared memory
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            metrics_integrated.add_connection(
                AgentConnection(
                    source_agent=agents[i],
                    target_agent=agents[j],
                    connection_type="shared_memory",
                    bidirectional=True,
                    weight=1.0,
                )
            )

    # Add feedback loops (metacognitive, coordination, memory)
    feedback_loops = [
        FeedbackLoop(
            loop_id="metacognitive_code_review",
            agents_involved=["CodeAgent", "ReviewerAgent", "CodeAgent"],
            loop_type="metacognitive",
            iterations_count=10,
            avg_latency_ms=42.5,
        ),
        FeedbackLoop(
            loop_id="security_audit_loop",
            agents_involved=["SecurityAgent", "CodeAgent", "SecurityAgent"],
            loop_type="coordination",
            iterations_count=5,
            avg_latency_ms=25.3,
        ),
        FeedbackLoop(
            loop_id="architect_review_loop",
            agents_involved=[
                "ArchitectAgent",
                "CodeAgent",
                "ReviewerAgent",
                "ArchitectAgent",
            ],
            loop_type="coordination",
            iterations_count=8,
            avg_latency_ms=67.2,
        ),
        FeedbackLoop(
            loop_id="memory_integration_loop",
            agents_involved=[
                "CodeAgent",
                "SecurityAgent",
                "ReviewerAgent",
                "ArchitectAgent",
            ],
            loop_type="memory",
            iterations_count=15,
            avg_latency_ms=15.8,
        ),
    ]

    for loop in feedback_loops:
        metrics_integrated.add_feedback_loop(loop)

    phi_integrated = metrics_integrated.calculate_phi_proxy()
    snapshot_integrated = metrics_integrated.snapshot(label="integrated_agents")

    print(f"Número de conexões: {len(metrics_integrated.connections)}")
    print(f"Número de feedback loops: {len(metrics_integrated.feedback_loops)}")
    print(f"Φ (Phi) calculado: {phi_integrated:.2f}")
    print()

    # Analysis
    print("ANÁLISE")
    print("=" * 70)
    phi_increase = (
        ((phi_integrated / phi_isolated) - 1) * 100 if phi_isolated > 0 else 0
    )
    print(f"Φ aumentou em: {phi_increase:.1f}%")
    print()

    hypothesis_low = 5.0
    hypothesis_high = 45.0

    if phi_isolated <= hypothesis_low * 2:
        print(
            f"✓ Φ isolado ({phi_isolated:.1f}) está na faixa esperada (≤ {hypothesis_low * 2})"
        )
    else:
        print(f"⚠ Φ isolado ({phi_isolated:.1f}) maior que esperado")

    if phi_integrated >= hypothesis_high * 0.8:
        expected_value = hypothesis_high * 0.8
        print(
            f"✓ Φ integrado ({phi_integrated:.1f}) está na faixa esperada "
            f"(≥ {expected_value})"
        )
    else:
        print(f"⚠ Φ integrado ({phi_integrated:.1f}) menor que esperado")

    print()

    # Return results
    result = {
        "experiment": "consciousness_phi_integration",
        "hypothesis": "Φ deve aumentar 3-5x com integração",
        "scenarios": {
            "isolated": {
                "phi": phi_isolated,
                "connections": len(metrics_isolated.connections),
                "feedback_loops": len(metrics_isolated.feedback_loops),
                "snapshot_file": str(snapshot_isolated),
            },
            "integrated": {
                "phi": phi_integrated,
                "connections": len(metrics_integrated.connections),
                "feedback_loops": len(metrics_integrated.feedback_loops),
                "snapshot_file": str(snapshot_integrated),
            },
        },
        "results": {
            "phi_increase_pct": phi_increase,
            "hypothesis_validated": phi_increase >= 300,  # At least 3x increase
        },
    }

    # Save experiment report
    report_path = Path("data/experiments/consciousness/experiment_phi_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Relatório salvo em: {report_path}")
    print()

    return result


def experiment_self_awareness() -> dict[str, Any]:
    """Test self-awareness metrics with different agent configurations.

    Reference: docs/concienciaetica-autonomia.md, Section 5 - Experimento 4
    """
    print("=" * 70)
    print("EXPERIMENTO 2: Autoconsciência - Comparação de Agentes")
    print("=" * 70)
    print()

    metrics = ConsciousnessMetrics(
        metrics_dir=Path("data/experiments/consciousness/self_awareness")
    )

    # Test different agent types
    agent_tests: list[AgentTestCase] = [
        {
            "name": "CodeAgent (sem metacognição)",
            "memory_test": True,
            "autonomous_goals": False,
            "self_description": 0.3,
            "limitation_awareness": 0.2,
        },
        {
            "name": "CodeAgent (com loop de revisão)",
            "memory_test": True,
            "autonomous_goals": True,
            "self_description": 0.7,
            "limitation_awareness": 0.6,
        },
        {
            "name": "ReviewerAgent (com autocrítica)",
            "memory_test": True,
            "autonomous_goals": True,
            "self_description": 0.85,
            "limitation_awareness": 0.75,
        },
        {
            "name": "Orchestrator (com memória episódica)",
            "memory_test": True,
            "autonomous_goals": True,
            "self_description": 0.9,
            "limitation_awareness": 0.85,
        },
    ]

    results: list[AgentResultDict] = []

    for test in agent_tests:
        awareness = metrics.measure_self_awareness(
            memory_test_passed=test["memory_test"],
            has_autonomous_goals=test["autonomous_goals"],
            self_description_quality=test["self_description"],
            limitation_acknowledgment=test["limitation_awareness"],
        )

        print(f"{test['name']}:")
        print(f"  Continuidade Temporal: {awareness.temporal_continuity_score:.2f}")
        print(f"  Autonomia de Objetivos: {awareness.goal_autonomy_score:.2f}")
        print(f"  Auto-Referência: {awareness.self_reference_score:.2f}")
        print(
            f"  Consciência de Limitações: {awareness.limitation_awareness_score:.2f}"
        )
        print(f"  SCORE GERAL: {awareness.overall_score:.2f}")
        print()

        results.append(
            {
                "agent": test["name"],
                "scores": {
                    "temporal_continuity": awareness.temporal_continuity_score,
                    "goal_autonomy": awareness.goal_autonomy_score,
                    "self_reference": awareness.self_reference_score,
                    "limitation_awareness": awareness.limitation_awareness_score,
                    "overall": awareness.overall_score,
                },
            }
        )

    # Analysis
    print("ANÁLISE")
    print("=" * 70)
    improvement = (
        (results[-1]["scores"]["overall"] - results[0]["scores"]["overall"])
        / results[0]["scores"]["overall"]
    ) * 100

    print(f"Melhoria de autoconsciência: {improvement:.1f}%")
    print(f"Score inicial: {results[0]['scores']['overall']:.2f}")
    print(f"Score final: {results[-1]['scores']['overall']:.2f}")
    print()

    # Save report
    report = {
        "experiment": "self_awareness_comparison",
        "hypothesis": "Autoconsciência aumenta com metacognição e memória",
        "results": results,
        "analysis": {
            "improvement_pct": improvement,
            "hypothesis_validated": improvement >= 100,  # At least 2x improvement
        },
    }

    report_path = Path(
        "data/experiments/consciousness/experiment_self_awareness_report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Relatório salvo em: {report_path}")
    print()

    return report


def run_all_consciousness_experiments() -> None:
    """Run all consciousness experiments."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "EXPERIMENTOS DE CONSCIÊNCIA" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    results = []

    # Experiment 1: Phi integration
    result1 = experiment_phi_integration()
    results.append(result1)

    # Experiment 2: Self-awareness
    result2 = experiment_self_awareness()
    results.append(result2)

    # Summary
    print("=" * 70)
    print("RESUMO DOS EXPERIMENTOS")
    print("=" * 70)
    print()

    for i, result in enumerate(results, 1):
        print(f"Experimento {i}: {result['experiment']}")
        print(f"  Hipótese: {result['hypothesis']}")

        if "results" in result and isinstance(result["results"], dict):
            validated = result["results"].get("hypothesis_validated", False)
        elif "analysis" in result and isinstance(result["analysis"], dict):
            validated = result["analysis"].get("hypothesis_validated", False)
        else:
            validated = result.get("hypothesis_validated", False)

        status = "✓ VALIDADA" if validated else "⚠ NÃO VALIDADA"
        print(f"  Status: {status}")

        print()

    # Save consolidated report
    consolidated = {
        "timestamp": "2025-11-19T00:30:00",
        "total_experiments": len(results),
        "experiments": results,
    }

    report_path = Path("data/experiments/consciousness/consolidated_report.json")
    with open(report_path, "w") as f:
        json.dump(consolidated, f, indent=2)

    print(f"Relatório consolidado: {report_path}")
    print()


if __name__ == "__main__":
    run_all_consciousness_experiments()
