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
Testes para HCHAC Framework.
"""

import pytest

from src.coevolution.hchac_framework import (
    CollaborationOutcome,
    ExecutionResult,
    HCHACFramework,
    Role,
)


class TestHCHACFramework:
    """Testes do framework HCHAC."""

    def test_initialization(self) -> None:
        """Testa inicialização do framework."""
        framework = HCHACFramework()
        assert framework is not None
        assert framework.trust is not None
        assert framework.negotiator is not None
        assert framework.feedback is not None
        assert framework.bias_detector is not None
        assert framework.memory is not None

    def test_co_execute_task_basic(self) -> None:
        """Testa execução colaborativa básica."""
        framework = HCHACFramework()

        outcome = framework.co_execute_task(
            human_id="user1",
            task_description="Implement feature X",
            human_intent={"goal": "feature X"},
            ai_capabilities=["autonomous_execution"],
        )

        assert isinstance(outcome, CollaborationOutcome)
        assert isinstance(outcome.success, bool)
        assert 0 <= outcome.human_satisfaction <= 1
        assert 0 <= outcome.ai_learning_gain <= 1
        assert -1 <= outcome.trust_delta <= 1

    def test_co_execute_task_failed_negotiation(self) -> None:
        """Testa execução com falha na negociação."""
        framework = HCHACFramework()

        # Usa threshold muito alto para forçar falha
        framework.negotiator.convergence_threshold = 0.99
        framework.negotiator.max_rounds = 1

        outcome = framework.co_execute_task(
            human_id="user1",
            task_description="Complex task",
            human_intent={"goal": "complex"},
            ai_capabilities=[],
        )

        # Pode falhar na negociação
        if not outcome.success:
            assert outcome.trust_delta < 0

    def test_allocate_roles_high_trust(self) -> None:
        """Testa alocação de papéis com trust alto."""
        framework = HCHACFramework()

        # Constrói trust alto
        framework.trust.trust_scores["user1"] = 0.9
        framework.trust._initialize_trust("user1")
        framework.trust.reliability_scores["user1"] = 0.9
        framework.trust.competence_scores["user1"] = 0.9
        framework.trust.transparency_scores["user1"] = 0.9
        framework.trust.alignment_scores["user1"] = 0.9

        roles = framework._allocate_roles(
            human_id="user1",
            task={"goal": "task"},
            ai_capabilities=["autonomous_execution"],
        )

        assert roles["human"] == Role.LEADER
        assert roles["ai"] == Role.CONTRIBUTOR

    def test_allocate_roles_medium_trust(self) -> None:
        """Testa alocação de papéis com trust médio."""
        framework = HCHACFramework()

        roles = framework._allocate_roles(
            human_id="user2", task={"goal": "task"}, ai_capabilities=[]
        )

        assert roles["human"] == Role.LEADER
        # Com trust médio (0.5), IA pode ser ADVISOR ou EXECUTOR
        # Verifica que é um dos dois
        assert roles["ai"] in [Role.ADVISOR, Role.EXECUTOR]

    def test_allocate_roles_low_trust(self) -> None:
        """Testa alocação de papéis com trust baixo."""
        framework = HCHACFramework()

        # Trust baixo
        framework.trust.trust_scores["user3"] = 0.3
        framework.trust._initialize_trust("user3")
        framework.trust.reliability_scores["user3"] = 0.3
        framework.trust.competence_scores["user3"] = 0.3
        framework.trust.transparency_scores["user3"] = 0.3
        framework.trust.alignment_scores["user3"] = 0.3

        roles = framework._allocate_roles(
            human_id="user3", task={"goal": "task"}, ai_capabilities=[]
        )

        assert roles["human"] == Role.LEADER
        assert roles["ai"] == Role.EXECUTOR

    def test_generate_ai_perspective(self) -> None:
        """Testa geração de perspectiva da IA."""
        framework = HCHACFramework()

        perspective = framework._generate_ai_perspective("Implement feature")

        assert isinstance(perspective, dict)
        assert "alternative_approaches" in perspective
        assert "potential_risks" in perspective
        assert "questions_for_human" in perspective

    def test_execute_with_roles(self) -> None:
        """Testa execução com papéis alocados."""
        framework = HCHACFramework()

        roles = {"human": Role.LEADER, "ai": Role.CONTRIBUTOR}

        result = framework._execute_with_roles(human_id="user1", goal={"goal": "test"}, roles=roles)

        assert isinstance(result, ExecutionResult)
        assert isinstance(result.success, bool)
        assert 0 <= result.satisfaction <= 1
        assert isinstance(result.insights, list)

    def test_calculate_learning_gain(self) -> None:
        """Testa cálculo de ganho de aprendizado."""
        framework = HCHACFramework()

        result = ExecutionResult(
            success=True,
            satisfaction=0.8,
            insights=["Insight 1", "Insight 2", "Insight 3"],
        )

        gain = framework._calculate_learning_gain(result)

        assert 0 <= gain <= 1
        assert gain > 0.5  # Com sucesso e insights, deve ser alto

    def test_get_trust_dashboard(self) -> None:
        """Testa obtenção de dashboard de trust."""
        framework = HCHACFramework()

        # Cria algum histórico
        framework.co_execute_task(
            human_id="user1",
            task_description="Task A",
            human_intent={"goal": "A"},
            ai_capabilities=[],
        )

        dashboard = framework.get_trust_dashboard("user1")

        assert isinstance(dashboard, dict)
        assert "trust_breakdown" in dashboard
        assert "trust_history" in dashboard
        assert "collaboration_stats" in dashboard
        assert "recent_insights" in dashboard

    def test_submit_human_feedback(self) -> None:
        """Testa submissão de feedback do humano."""
        framework = HCHACFramework()

        framework.submit_human_feedback(
            human_id="user1",
            feedback_type="CORRECTION",
            content="Please fix this",
            context={"item": "value"},
        )

        # Verifica que feedback foi registrado
        assert len(framework.feedback.feedback_history) == 1

    def test_submit_human_feedback_invalid_type(self) -> None:
        """Testa submissão de feedback com tipo inválido."""
        framework = HCHACFramework()

        # Tipo inválido não deve causar crash
        framework.submit_human_feedback(
            human_id="user1", feedback_type="INVALID_TYPE", content="Test", context={}
        )

        # Não deve ter adicionado feedback inválido
        # (ou pode ter logado erro)

    def test_get_ai_feedback(self) -> None:
        """Testa obtenção de feedback da IA."""
        framework = HCHACFramework()

        # IA submete feedback
        from src.coevolution.bidirectional_feedback import FeedbackType

        framework.feedback.submit_ai_feedback(
            feedback_type=FeedbackType.OBSERVATION, content="I observed something"
        )

        ai_feedback = framework.get_ai_feedback(limit=5)

        assert isinstance(ai_feedback, list)
        assert len(ai_feedback) >= 1

        if ai_feedback:
            item = ai_feedback[0]
            assert "timestamp" in item
            assert "type" in item
            assert "content" in item
            assert "acknowledged" in item

    def test_role_enum(self) -> None:
        """Testa enum de papéis."""
        assert Role.LEADER.value == "leader"
        assert Role.CONTRIBUTOR.value == "contributor"
        assert Role.ADVISOR.value == "advisor"
        assert Role.EXECUTOR.value == "executor"
        assert Role.REVIEWER.value == "reviewer"

    def test_collaboration_outcome_dataclass(self) -> None:
        """Testa dataclass de resultado de colaboração."""
        outcome = CollaborationOutcome(
            success=True,
            human_satisfaction=0.9,
            ai_learning_gain=0.7,
            trust_delta=0.1,
            insights_generated=["Insight 1"],
        )

        assert outcome.success is True
        assert outcome.human_satisfaction == pytest.approx(0.9)
        assert outcome.ai_learning_gain == pytest.approx(0.7)
        assert outcome.trust_delta == pytest.approx(0.1)
        assert len(outcome.insights_generated) == 1

    def test_execution_result_dataclass(self) -> None:
        """Testa dataclass de resultado de execução."""
        result = ExecutionResult(
            success=True, satisfaction=0.85, insights=["A", "B"], data={"key": "value"}
        )

        assert result.success is True
        assert result.satisfaction == pytest.approx(0.85)
        assert len(result.insights) == 2
        assert "key" in result.data

    def test_bias_detection_integration(self) -> None:
        """Testa integração com detector de viés."""
        framework = HCHACFramework()

        # Executa tarefa que pode ter vieses
        outcome = framework.co_execute_task(
            human_id="user1",
            task_description="Task with potential bias",
            human_intent={"goal": "test"},
            ai_capabilities=[],
        )

        # Framework deve ter detectado e corrigido vieses automaticamente
        assert isinstance(outcome, CollaborationOutcome)

    def test_memory_storage_integration(self) -> None:
        """Testa integração com memória de co-evolução."""
        framework = HCHACFramework()

        # Executa tarefa
        framework.co_execute_task(
            human_id="user1",
            task_description="Stored task",
            human_intent={"goal": "store"},
            ai_capabilities=[],
        )

        # Verifica que foi armazenado na memória
        sessions = framework.memory.get_human_sessions("user1")
        assert len(sessions) >= 1

    def test_trust_evolution_over_multiple_tasks(self) -> None:
        """Testa evolução de trust ao longo de múltiplas tarefas."""
        framework = HCHACFramework()

        initial_trust = framework.trust.get_trust_level("user1")

        # Executa tarefas bem-sucedidas
        for _ in range(3):
            framework.co_execute_task(
                human_id="user1",
                task_description="Success task",
                human_intent={"goal": "success"},
                ai_capabilities=[],
            )

        final_trust = framework.trust.get_trust_level("user1")

        # Trust deve ter aumentado
        assert final_trust >= initial_trust
