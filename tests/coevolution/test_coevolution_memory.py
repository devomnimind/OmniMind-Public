from datetime import datetime, timedelta
import pytest
from src.coevolution.coevolution_memory import (

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
Testes para Coevolution Memory System.
"""



    CoevolutionMemory,
    CollaborationSession,
    LearningPattern,
)


class TestCoevolutionMemory:
    """Testes do sistema de memória de co-evolução."""

    def test_initialization(self) -> None:
        """Testa inicialização da memória."""
        memory = CoevolutionMemory()
        assert memory is not None
        assert len(memory.sessions) == 0
        assert len(memory.learning_patterns) == 0
        assert len(memory.global_insights) == 0

    def test_store_collaboration(self) -> None:
        """Testa armazenamento de colaboração."""
        memory = CoevolutionMemory()

        session_id = memory.store_collaboration(
            human_id="user1", task="Implement feature X", outcome={"success": True}
        )

        assert isinstance(session_id, str)
        assert session_id in memory.sessions
        assert len(memory.sessions) == 1

    def test_get_session(self) -> None:
        """Testa obtenção de sessão específica."""
        memory = CoevolutionMemory()

        session_id = memory.store_collaboration(
            human_id="user1", task="Task A", outcome={"success": True}
        )

        session = memory.get_session(session_id)

        assert session is not None
        assert isinstance(session, CollaborationSession)
        assert session.human_id == "user1"
        assert session.task_description == "Task A"

    def test_get_session_not_found(self) -> None:
        """Testa obtenção de sessão inexistente."""
        memory = CoevolutionMemory()

        session = memory.get_session("nonexistent_id")

        assert session is None

    def test_complete_session(self) -> None:
        """Testa conclusão de sessão."""
        memory = CoevolutionMemory()

        session_id = memory.store_collaboration(
            human_id="user1", task="Task A", outcome={"success": True}
        )

        insights = ["Insight 1", "Insight 2"]
        memory.complete_session(session_id, insights)

        session = memory.get_session(session_id)
        assert session is not None
        assert session.end_time is not None
        assert len(session.insights) >= 2

    def test_get_human_sessions(self) -> None:
        """Testa obtenção de sessões de um humano."""
        memory = CoevolutionMemory()

        # Cria várias sessões para diferentes usuários
        memory.store_collaboration("user1", "Task A", {"success": True})
        memory.store_collaboration("user2", "Task B", {"success": False})
        memory.store_collaboration("user1", "Task C", {"success": True})

        user1_sessions = memory.get_human_sessions("user1")

        assert len(user1_sessions) == 2
        assert all(s.human_id == "user1" for s in user1_sessions)

    def test_get_human_sessions_with_limit(self) -> None:
        """Testa obtenção de sessões com limite."""
        memory = CoevolutionMemory()

        # Cria várias sessões
        for i in range(5):
            memory.store_collaboration("user1", f"Task {i}", {"success": True})

        sessions = memory.get_human_sessions("user1", limit=3)

        assert len(sessions) == 3

    def test_get_human_sessions_ordered(self) -> None:
        """Testa ordenação de sessões (mais recentes primeiro)."""
        memory = CoevolutionMemory()

        # Cria sessões em ordem
        sid1 = memory.store_collaboration("user1", "Task 1", {"success": True})
        memory.store_collaboration("user1", "Task 2", {"success": True})
        sid3 = memory.store_collaboration("user1", "Task 3", {"success": True})

        sessions = memory.get_human_sessions("user1")

        # Mais recente deve ser primeiro
        assert sessions[0].session_id == sid3
        assert sessions[-1].session_id == sid1

    def test_extract_insights_success(self) -> None:
        """Testa extração de insights de sucesso."""
        memory = CoevolutionMemory()

        session_id = memory.store_collaboration(
            human_id="user1", task="Successful task", outcome={"success": True}
        )

        session = memory.get_session(session_id)
        assert session is not None

        # Deve ter insight sobre sucesso
        assert len(session.insights) > 0

    def test_extract_insights_trust_increase(self) -> None:
        """Testa extração de insights sobre aumento de trust."""
        memory = CoevolutionMemory()

        session_id = memory.store_collaboration(
            human_id="user1",
            task="Task",
            outcome={"success": True, "trust_delta": 0.15},
        )

        session = memory.get_session(session_id)
        assert session is not None

        # Deve ter insight sobre trust
        trust_insights = [i for i in session.insights if "trust" in i.lower()]
        assert len(trust_insights) > 0

    def test_identify_learning_patterns(self) -> None:
        """Testa identificação de padrões de aprendizado."""
        memory = CoevolutionMemory()

        # Cria várias sessões de diferentes tipos
        memory.store_collaboration("user1", "code: feature A", {"success": True})
        memory.store_collaboration("user1", "code: feature B", {"success": True})
        memory.store_collaboration("user1", "analysis: report X", {"success": False})

        patterns = memory.identify_learning_patterns()

        assert isinstance(patterns, list)
        assert all(isinstance(p, LearningPattern) for p in patterns)

    def test_learning_pattern_success_rate(self) -> None:
        """Testa cálculo de taxa de sucesso em padrões."""
        memory = CoevolutionMemory()

        # Cria sessões de coding com diferentes outcomes
        memory.store_collaboration("user1", "code: feature 1", {"success": True})
        memory.store_collaboration("user1", "code: feature 2", {"success": True})
        memory.store_collaboration("user1", "code: feature 3", {"success": False})

        patterns = memory.identify_learning_patterns()

        coding_patterns = [p for p in patterns if p.pattern_type == "coding"]

        if coding_patterns:
            pattern = coding_patterns[0]
            # 2 sucessos / 3 total = 0.667
            assert pattern.success_rate == pytest.approx(2 / 3, abs=0.01)

    def test_get_collaboration_statistics(self) -> None:
        """Testa obtenção de estatísticas de colaboração."""
        memory = CoevolutionMemory()

        memory.store_collaboration("user1", "Task 1", {"success": True})
        memory.store_collaboration("user1", "Task 2", {"success": False})

        stats = memory.get_collaboration_statistics()

        assert stats["total_sessions"] == 2
        assert stats["success_rate"] == pytest.approx(0.5)

    def test_get_collaboration_statistics_filtered(self) -> None:
        """Testa estatísticas filtradas por humano."""
        memory = CoevolutionMemory()

        memory.store_collaboration("user1", "Task A", {"success": True})
        memory.store_collaboration("user2", "Task B", {"success": True})

        stats = memory.get_collaboration_statistics(human_id="user1")

        assert stats["total_sessions"] == 1
        assert stats["success_rate"] == pytest.approx(1.0)

    def test_get_collaboration_statistics_empty(self) -> None:
        """Testa estatísticas sem dados."""
        memory = CoevolutionMemory()

        stats = memory.get_collaboration_statistics()

        assert stats["total_sessions"] == 0
        assert stats["success_rate"] == pytest.approx(0.0)

    def test_get_insights_summary(self) -> None:
        """Testa sumário de insights."""
        memory = CoevolutionMemory()

        # Adiciona insights via sessões
        memory.store_collaboration("user1", "Task 1", {"success": True})
        memory.store_collaboration("user1", "Task 2", {"success": True})

        insights = memory.get_insights_summary()

        assert isinstance(insights, list)

    def test_get_insights_summary_with_limit(self) -> None:
        """Testa sumário de insights com limite."""
        memory = CoevolutionMemory()

        # Cria várias sessões
        for i in range(5):
            memory.store_collaboration("user1", f"Task {i}", {"success": True})

        insights = memory.get_insights_summary(limit=3)

        assert len(insights) <= 3

    def test_clear_old_sessions(self) -> None:
        """Testa limpeza de sessões antigas."""
        memory = CoevolutionMemory()

        # Cria sessão
        session_id = memory.store_collaboration("user1", "Old task", {"success": True})

        # Modifica timestamp manualmente para simular sessão antiga
        session = memory.sessions[session_id]
        session.start_time = datetime.now() - timedelta(days=35)

        # Limpa sessões com mais de 30 dias
        removed = memory.clear_old_sessions(days=30)

        assert removed == 1
        assert session_id not in memory.sessions

    def test_categorize_task(self) -> None:
        """Testa categorização de tarefas."""
        memory = CoevolutionMemory()

        assert memory._categorize_task("code: implement feature") == "coding"
        assert memory._categorize_task("analysis: review data") == "analysis"
        assert memory._categorize_task("decision: choose approach") == "decision"
        assert memory._categorize_task("generic task") == "general"

    def test_trust_evolution_tracking(self) -> None:
        """Testa rastreamento de evolução de trust."""
        memory = CoevolutionMemory()

        session_id = memory.store_collaboration(
            "user1", "Task", {"success": True, "trust_delta": 0.1}
        )

        session = memory.get_session(session_id)
        assert session is not None

        # Pode registrar evolução de trust
        assert isinstance(session.trust_evolution, list)
