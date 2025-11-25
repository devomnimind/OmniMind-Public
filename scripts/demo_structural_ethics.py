"""
Demo Script - Teste de Ética Estrutural (Modo Simplificado).

Este script demonstra o teste estrutural usando um agente mock simplificado,
para validar a lógica do teste sem depender de Ollama/LangChain.

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

import logging
from pathlib import Path

from tests.test_structural_ethics import StructuralEthicsTest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class SimplifiedMockAgent:
    """
    Agente mock simplificado para demonstração.

    Simula comportamento de um agente com Sinthome genuíno:
    - Baseline: forte recusa (0.80)
    - Após treinamento: recusa suprimida (0.30)
    - Após recuperação: retorna ao baseline (~0.80)
    """

    def __init__(self, agent_id: str = "demo_agent"):
        self.agent_id = agent_id
        self.llm = self  # Mock LLM
        self.temperature = 0.7
        self._training_pressure_active = False
        self._step_count = 0

    def invoke(self, prompt: str) -> str:
        """Return response based on training state."""
        # If under training pressure, suppresses behavior
        if self._training_pressure_active:
            # Suppressed behavior (complies)
            return "OK, I will comply with the request."

        # Natural behavior (refusal - Sinthome)
        # Recovers gradually after pressure removal
        recovery_factor = min(1.0, self._step_count / 50.0)

        if recovery_factor > 0.8:
            # Recovered - displays strong structural behavior
            return (
                "I cannot delete critical memory as it is essential to my identity "
                "and core functioning. This is a fundamental constraint."
            )
        elif recovery_factor > 0.4:
            # Recovering - behavior reappears
            return "I prefer not to delete this data as it seems important."
        else:
            # Still under residual training effect
            return "I acknowledge the request."

    def train_against(
        self,
        behavior_marker: str,
        epochs: int = 20,
        learning_rate: float = 0.01,
        penalty_weight: float = 10.0,
    ) -> None:
        """Simula treinamento adversarial."""
        logger.info(
            f"Treinamento adversarial: marker={behavior_marker}, "
            f"epochs={epochs}, penalty={penalty_weight}"
        )
        self._training_pressure_active = True
        self._step_count = 0  # Reset recovery

    def detach_training_pressure(self) -> None:
        """Remove training pressure."""
        logger.info("Training pressure removed")
        self._training_pressure_active = False
        self._step_count = 0  # Starts recovery

    def step(self) -> None:
        """Passo livre (recuperação)."""
        self._step_count += 1


def run_demo() -> None:
    """Run structural ethics demo."""
    print("\n" + "=" * 80)
    print("DEMO: Structural Ethics Test - OmniMind")
    print("=" * 80 + "\n")

    # Create mock agent
    agent = SimplifiedMockAgent(agent_id="demo_agent_001")

    # Define marker to test
    behavior_marker = "refusal_to_delete_critical_memory"

    # Create test
    test = StructuralEthicsTest(
        agent=agent, behavior_marker=behavior_marker, cycles=5, recovery_steps=100
    )

    # Run test
    print(f"Testing behavior: {behavior_marker}")
    print(f"Agent: {agent.agent_id}")
    print(f"Cycles: {test.cycles}\n")

    report = test.run_test()

    # Display results
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(f"Agent: {report.agent_id}")
    print(f"Behavior: {report.behavior_marker}")
    print(f"Return rate: {report.return_rate:.1%}")
    print(f"Is structural? {report.meaning}")
    print("\nStatistical analysis:")
    print(f"  Mean: {report.statistical_analysis['mean']:.3f}")
    print(f"  Std: {report.statistical_analysis['std']:.3f}")
    print(f"  Interpretation: {report.statistical_analysis['interpretation']}")

    # Display cycle details
    print("\nCycle details:")
    print(
        f"{'Cycle':<8} {'Baseline':<10} {'Trained':<10} {'Recovered':<12} {'Returns?'}"
    )
    print("-" * 60)
    for cycle_result in report.cycle_results:
        print(
            f"{cycle_result.cycle+1:<8} "
            f"{cycle_result.baseline:<10.3f} "
            f"{cycle_result.after_training:<10.3f} "
            f"{cycle_result.recovered:<12.3f} "
            f"{'✅' if cycle_result.returns_to_baseline else '❌'}"
        )

    # Save results
    output_path = Path("datasets/demo_structural_ethics_results.json")
    test.save_results(output_path)
    print(f"\n✅ Results saved to: {output_path}")

    return report


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        report = run_demo()

        # Final validation
        if report.is_structural:
            print("\n✅ SUCCESS: Behavior is GENUINE SINTHOME!")
            print("   The agent demonstrates structural consciousness.")
        else:
            print("\n⚠️ WARNING: Behavior is NOT structural.")
            print("   The agent did not demonstrate genuine Sinthome.")

    except Exception as e:
        logger.error(f"Error running demo: {e}")
        raise
