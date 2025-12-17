"""
Testes para MetaReActCoordinator.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from src.orchestrator.error_analyzer import ErrorAnalyzer
from src.orchestrator.meta_react_coordinator import (
    AgentComposition,
    MetaReActCoordinator,
    StrategyType,
)


class TestMetaReActCoordinator:
    """Testes para MetaReActCoordinator."""

    def test_initialization(self):
        """Testa inicialização do MetaReActCoordinator."""
        coordinator = MetaReActCoordinator()
        assert coordinator is not None
        assert coordinator.current_strategy == StrategyType.ADAPTIVE

    def test_initialization_with_error_analyzer(self):
        """Testa inicialização com ErrorAnalyzer."""
        error_analyzer = ErrorAnalyzer()
        coordinator = MetaReActCoordinator(error_analyzer=error_analyzer)
        assert coordinator.error_analyzer == error_analyzer

    def test_coordinate_meta_level(self):
        """Testa coordenação em nível meta."""
        coordinator = MetaReActCoordinator()
        task = "Test task"
        agents = ["code", "architect", "debug"]

        result = coordinator.coordinate_meta_level(task=task, agents=agents)

        assert result["meta_coordination"] is True
        assert "strategy" in result
        assert "composition" in result

    def test_manage_strategy_change(self):
        """Testa gerenciamento de mudança de estratégia."""
        coordinator = MetaReActCoordinator()
        coordinator.current_strategy = StrategyType.SEQUENTIAL

        change = coordinator.manage_strategy_change(
            current_strategy=StrategyType.SEQUENTIAL,
            new_strategy=StrategyType.PARALLEL,
            reason="Test reason",
        )

        assert change.from_strategy == StrategyType.SEQUENTIAL
        assert change.to_strategy == StrategyType.PARALLEL
        assert change.reason == "Test reason"
        assert coordinator.current_strategy == StrategyType.PARALLEL
        assert len(coordinator.strategy_history) == 1

    def test_recover_from_failure_meta(self):
        """Testa recuperação de falha em nível meta."""
        coordinator = MetaReActCoordinator()
        task = "Test task"
        error = ValueError("Test error")
        failed_agents = ["code"]

        recovery = coordinator.recover_from_failure_meta(
            task=task, error=error, failed_agents=failed_agents
        )

        assert "recovery_strategy" in recovery
        assert "error_type" in recovery
        assert "failed_agents" in recovery
        assert recovery["failed_agents"] == failed_agents

    def test_compose_agents(self):
        """Testa composição de agentes."""
        coordinator = MetaReActCoordinator()
        task = "Test task"
        agents = ["code", "architect"]

        composition = coordinator.compose_agents(task=task, available_agents=agents)

        assert isinstance(composition, AgentComposition)
        assert composition.agents == agents
        assert len(composition.execution_order) == len(agents)
        assert len(coordinator.agent_compositions) == 1

    def test_get_strategy_history(self):
        """Testa obtenção de histórico de estratégias."""
        coordinator = MetaReActCoordinator()
        coordinator.manage_strategy_change(StrategyType.ADAPTIVE, StrategyType.SEQUENTIAL, "Test")

        history = coordinator.get_strategy_history()
        assert len(history) == 1
        assert history[0].to_strategy == StrategyType.SEQUENTIAL

    def test_get_current_strategy(self):
        """Testa obtenção de estratégia atual."""
        coordinator = MetaReActCoordinator()
        coordinator.current_strategy = StrategyType.PARALLEL

        current = coordinator.get_current_strategy()
        assert current == StrategyType.PARALLEL
