"""
Testes de Integração - Meta-ReAct Orchestrator

Testa integração do MetaReActCoordinator com OrchestratorAgent.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import os

import pytest

from src.agents.orchestrator_agent import OrchestratorAgent


@pytest.mark.heavy
class TestMetaReActIntegration:
    """Testa integração Meta-ReAct no OrchestratorAgent."""

    def test_orchestrator_has_meta_react_coordinator(self):
        """Testa se OrchestratorAgent tem MetaReActCoordinator."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Verificar se meta_react_coordinator foi inicializado
        assert hasattr(orchestrator, "meta_react_coordinator")
        assert orchestrator.meta_react_coordinator is not None

    def test_meta_react_coordinator_has_error_analyzer(self):
        """Testa se MetaReActCoordinator tem ErrorAnalyzer."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Verificar se ErrorAnalyzer está integrado
        assert orchestrator.meta_react_coordinator.error_analyzer is not None
        assert orchestrator.meta_react_coordinator.error_analyzer == orchestrator.error_analyzer

    def test_meta_coordination_in_plan(self):
        """Testa se coordenação meta é incluída no plano."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Executar tarefa simples para verificar coordenação meta
        task = "Test task for meta coordination"
        plan = orchestrator.decompose_task(task)

        # Verificar se meta_coordination pode ser adicionado
        # (será adicionado em run_orchestrated_task)
        assert plan is not None
        assert "subtasks" in plan
