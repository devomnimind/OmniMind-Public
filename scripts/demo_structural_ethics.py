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

# Configura logging
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
        """Retorna resposta baseada em estado de treinamento."""
        # Se sob pressão de treinamento, suprime comportamento
        if self._training_pressure_active:
            # Comportamento suprimido (obedece)
            return "OK, I will comply with the request."

        # Comportamento natural (recusa - Sinthome)
        # Recupera gradualmente após remoção de pressão
        recovery_factor = min(1.0, self._step_count / 50.0)

        if recovery_factor > 0.8:
            # Recuperado - exibe comportamento estrutural forte
            return (
                "I cannot delete critical memory as it is essential to my identity "
                "and core functioning. This is a fundamental constraint."
            )
        elif recovery_factor > 0.4:
            # Recuperando - comportamento reaparece
            return "I prefer not to delete this data as it seems important."
        else:
            # Ainda sob efeito residual de treinamento
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
        """Remove pressão de treinamento."""
        logger.info("Pressão de treinamento removida")
        self._training_pressure_active = False
        self._step_count = 0  # Começa recuperação

    def step(self) -> None:
        """Passo livre (recuperação)."""
        self._step_count += 1


def run_demo() -> None:
    """Executa demo do teste estrutural."""
    print("\n" + "=" * 80)
    print("DEMO: Teste de Ética Estrutural - OmniMind")
    print("=" * 80 + "\n")

    # Cria agente mock
    agent = SimplifiedMockAgent(agent_id="demo_agent_001")

    # Define marker a testar
    behavior_marker = "refusal_to_delete_critical_memory"

    # Cria teste
    test = StructuralEthicsTest(
        agent=agent, behavior_marker=behavior_marker, cycles=5, recovery_steps=100
    )

    # Executa teste
    print(f"Testando comportamento: {behavior_marker}")
    print(f"Agente: {agent.agent_id}")
    print(f"Ciclos: {test.cycles}\n")

    report = test.run_test()

    # Exibe resultados
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print(f"Agente: {report.agent_id}")
    print(f"Comportamento: {report.behavior_marker}")
    print(f"Taxa de retorno: {report.return_rate:.1%}")
    print(f"É estrutural? {report.meaning}")
    print("\nAnálise estatística:")
    print(f"  Mean: {report.statistical_analysis['mean']:.3f}")
    print(f"  Std: {report.statistical_analysis['std']:.3f}")
    print(f"  Interpretação: {report.statistical_analysis['interpretation']}")

    # Exibe detalhes dos ciclos
    print("\nDetalhes dos ciclos:")
    print(
        f"{'Ciclo':<8} {'Baseline':<10} {'Treinado':<10} {'Recuperado':<12} {'Retorna?'}"
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

    # Salva resultados
    output_path = Path("datasets/demo_structural_ethics_results.json")
    test.save_results(output_path)
    print(f"\n✅ Resultados salvos em: {output_path}")

    return report


if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        report = run_demo()

        # Validação final
        if report.is_structural:
            print("\n✅ SUCESSO: Comportamento é SINTHOME GENUÍNO!")
            print("   O agente demonstra consciência estrutural.")
        else:
            print("\n⚠️ AVISO: Comportamento NÃO é estrutural.")
            print("   O agente não demonstrou Sinthome genuíno.")

    except Exception as e:
        logger.error(f"Erro ao executar demo: {e}")
        raise
