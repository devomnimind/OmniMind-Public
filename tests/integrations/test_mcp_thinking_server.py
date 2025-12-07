"""
Testes para ThinkingMCPServer.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import pytest

from src.integrations.mcp_thinking_server import ThinkingMCPServer


@pytest.mark.asyncio
@pytest.mark.real
class TestThinkingMCPServer:
    """Testes para ThinkingMCPServer."""

    def setup_method(self) -> None:
        """Setup para cada teste."""
        self.server = ThinkingMCPServer()

    def test_start_session(self) -> None:
        """Testa criação de sessão de pensamento."""
        result = self.server.start_session("Resolver problema X")

        assert "session_id" in result
        assert result["goal"] == "Resolver problema X"
        assert result["status"] == "active"
        assert "created_at" in result
        assert result["session_id"].startswith("think_")

    def test_start_session_with_metadata(self) -> None:
        """Testa criação de sessão com metadados."""
        metadata = {"priority": "high", "tags": ["urgent"]}
        result = self.server.start_session("Teste com metadata", metadata=metadata)

        assert result["session_id"] in self.server._sessions
        session = self.server._sessions[result["session_id"]]
        assert session.metadata == metadata

    def test_add_step(self) -> None:
        """Testa adição de passo a sessão."""
        session_result = self.server.start_session("Teste de passos")
        session_id = session_result["session_id"]

        step_result = self.server.add_step(
            session_id=session_id,
            content="Primeiro passo de pensamento",
            step_type="thought",
        )

        assert "step_id" in step_result
        assert step_result["session_id"] == session_id
        assert step_result["step_type"] == "thought"
        assert step_result["step_index"] == 0

        # Verificar que passo foi adicionado
        session = self.server._sessions[session_id]
        assert len(session.steps) == 1
        assert session.steps[0].content == "Primeiro passo de pensamento"

    def test_add_step_different_types(self) -> None:
        """Testa adição de passos de diferentes tipos."""
        session_result = self.server.start_session("Teste tipos")
        session_id = session_result["session_id"]

        types = ["observation", "thought", "action", "result"]
        for step_type in types:
            self.server.add_step(
                session_id=session_id,
                content=f"Passo do tipo {step_type}",
                step_type=step_type,
            )

        session = self.server._sessions[session_id]
        assert len(session.steps) == 4
        assert [s.step_type for s in session.steps] == types

    def test_add_step_to_nonexistent_session(self) -> None:
        """Testa erro ao adicionar passo a sessão inexistente."""
        with pytest.raises(ValueError, match="Sessão não encontrada"):
            self.server.add_step("nonexistent", "conteúdo", "thought")

    def test_get_history(self) -> None:
        """Testa recuperação de histórico."""
        session_result = self.server.start_session("Teste histórico")
        session_id = session_result["session_id"]

        # Adicionar alguns passos
        for i in range(3):
            self.server.add_step(
                session_id=session_id,
                content=f"Passo {i+1}",
                step_type="thought",
            )

        history = self.server.get_history(session_id)

        assert history["session_id"] == session_id
        assert history["goal"] == "Teste histórico"
        assert history["total_steps"] == 3
        assert len(history["steps"]) == 3
        assert all("step_id" in step for step in history["steps"])
        assert all("content" in step for step in history["steps"])

    def test_get_history_with_limit(self) -> None:
        """Testa histórico com limite."""
        session_result = self.server.start_session("Teste limite")
        session_id = session_result["session_id"]

        # Adicionar 5 passos
        for i in range(5):
            self.server.add_step(session_id, f"Passo {i+1}", "thought")

        # Buscar apenas últimos 2
        history = self.server.get_history(session_id, limit=2)

        assert len(history["steps"]) == 2
        assert history["steps"][0]["content"] == "Passo 4"
        assert history["steps"][1]["content"] == "Passo 5"

    def test_branch_thinking(self) -> None:
        """Testa criação de branch de pensamento."""
        session_result = self.server.start_session("Sessão original")
        session_id = session_result["session_id"]

        # Adicionar alguns passos
        step1 = self.server.add_step(session_id, "Passo 1", "thought")
        self.server.add_step(session_id, "Passo 2", "thought")

        # Criar branch a partir do primeiro passo
        branch_result = self.server.branch_thinking(
            session_id=session_id,
            step_id=step1["step_id"],
            goal="Branch do passo 1",
        )

        assert "new_session_id" in branch_result
        assert branch_result["parent_session"] == session_id
        assert branch_result["branch_from_step"] == step1["step_id"]

        # Verificar que branch foi criado
        branch_id = branch_result["new_session_id"]
        assert branch_id in self.server._sessions

        branch_session = self.server._sessions[branch_id]
        assert branch_session.parent_session_id == session_id
        assert len(branch_session.steps) == 2  # Passo 1 + passo de branch

    def test_branch_thinking_nonexistent_session(self) -> None:
        """Testa erro ao criar branch de sessão inexistente."""
        with pytest.raises(ValueError, match="Sessão não encontrada"):
            self.server.branch_thinking("nonexistent", "step_123")

    def test_branch_thinking_nonexistent_step(self) -> None:
        """Testa erro ao criar branch de passo inexistente."""
        session_result = self.server.start_session("Teste")
        session_id = session_result["session_id"]

        with pytest.raises(ValueError, match="Passo não encontrado"):
            self.server.branch_thinking(session_id, "nonexistent_step")

    def test_merge_branches(self) -> None:
        """Testa merge de múltiplas sessões."""
        # Criar 2 sessões
        session1 = self.server.start_session("Sessão 1")
        session2 = self.server.start_session("Sessão 2")

        # Adicionar passos a cada uma
        self.server.add_step(session1["session_id"], "Passo 1.1", "thought")
        self.server.add_step(session1["session_id"], "Passo 1.2", "thought")
        self.server.add_step(session2["session_id"], "Passo 2.1", "thought")

        # Mesclar
        merge_result = self.server.merge_branches(
            [session1["session_id"], session2["session_id"]],
            merge_strategy="sequential",
        )

        assert "merged_session_id" in merge_result
        assert len(merge_result["merged_from"]) == 2

        merged_session = self.server._sessions[merge_result["merged_session_id"]]
        assert len(merged_session.steps) == 3

    def test_merge_branches_parallel_strategy(self) -> None:
        """Testa merge com estratégia paralela."""
        session1 = self.server.start_session("Sessão 1")
        session2 = self.server.start_session("Sessão 2")

        self.server.add_step(session1["session_id"], "Passo 1", "thought")
        self.server.add_step(session2["session_id"], "Passo 2", "thought")

        merge_result = self.server.merge_branches(
            [session1["session_id"], session2["session_id"]],
            merge_strategy="parallel",
        )

        merged_session = self.server._sessions[merge_result["merged_session_id"]]
        assert len(merged_session.steps) == 2

    def test_merge_branches_insufficient_sessions(self) -> None:
        """Testa erro ao mesclar menos de 2 sessões."""
        with pytest.raises(ValueError, match="Precisa de pelo menos 2 sessões"):
            self.server.merge_branches(["session1"])

    def test_evaluate_quality(self) -> None:
        """Testa avaliação de qualidade."""
        session_result = self.server.start_session("Teste qualidade")
        session_id = session_result["session_id"]

        # Adicionar passos diversos
        self.server.add_step(session_id, "Observação inicial", "observation")
        self.server.add_step(session_id, "Pensamento sobre o problema", "thought")
        self.server.add_step(session_id, "Ação tomada", "action")
        self.server.add_step(session_id, "Resultado obtido", "result")

        evaluation = self.server.evaluate_quality(session_id)

        assert "score" in evaluation
        assert "feedback" in evaluation
        assert "metrics" in evaluation
        assert 0.0 <= evaluation["score"] <= 1.0
        assert evaluation["metrics"]["total_steps"] == 4
        assert evaluation["metrics"]["type_diversity"] > 0

    def test_evaluate_quality_empty_session(self) -> None:
        """Testa avaliação de sessão vazia."""
        session_result = self.server.start_session("Sessão vazia")
        session_id = session_result["session_id"]

        evaluation = self.server.evaluate_quality(session_id)

        assert evaluation["score"] == 0.0
        assert evaluation["metrics"]["total_steps"] == 0

    def test_export_chain_json(self) -> None:
        """Testa exportação em formato JSON."""
        session_result = self.server.start_session("Teste export")
        session_id = session_result["session_id"]

        self.server.add_step(session_id, "Passo 1", "thought")
        self.server.add_step(session_id, "Passo 2", "action")

        export = self.server.export_chain(session_id, format="json")

        assert export["format"] == "json"
        assert isinstance(export["chain"], dict)
        assert export["chain"]["session_id"] == session_id
        assert len(export["chain"]["steps"]) == 2

    def test_export_chain_text(self) -> None:
        """Testa exportação em formato texto."""
        session_result = self.server.start_session("Teste export texto")
        session_id = session_result["session_id"]

        self.server.add_step(session_id, "Conteúdo do passo", "thought")

        export = self.server.export_chain(session_id, format="text")

        assert export["format"] == "text"
        assert isinstance(export["chain"], str)
        assert "Teste export texto" in export["chain"]
        assert "Conteúdo do passo" in export["chain"]

    def test_export_chain_markdown(self) -> None:
        """Testa exportação em formato markdown."""
        session_result = self.server.start_session("Teste export markdown")
        session_id = session_result["session_id"]

        self.server.add_step(session_id, "Conteúdo", "thought")

        export = self.server.export_chain(session_id, format="markdown")

        assert export["format"] == "markdown"
        assert isinstance(export["chain"], str)
        assert "# Teste export markdown" in export["chain"]
        assert "## Step 1" in export["chain"]

    def test_export_chain_invalid_format(self) -> None:
        """Testa erro com formato inválido."""
        session_result = self.server.start_session("Teste")
        session_id = session_result["session_id"]

        with pytest.raises(ValueError, match="Formato não suportado"):
            self.server.export_chain(session_id, format="invalid")

    def test_resume_session(self) -> None:
        """Testa retomada de sessão."""
        session_result = self.server.start_session("Teste resume")
        session_id = session_result["session_id"]

        # Pausar sessão manualmente
        session = self.server._sessions[session_id]
        session.status = "paused"

        result = self.server.resume_session(session_id)

        assert result["status"] == "resumed"
        assert self.server._sessions[session_id].status == "active"

    def test_resume_already_active_session(self) -> None:
        """Testa retomada de sessão já ativa."""
        session_result = self.server.start_session("Teste")
        session_id = session_result["session_id"]

        result = self.server.resume_session(session_id)

        assert result["status"] == "already_active"

    def test_resume_nonexistent_session(self) -> None:
        """Testa erro ao retomar sessão inexistente."""
        with pytest.raises(ValueError, match="Sessão não encontrada"):
            self.server.resume_session("nonexistent")

    def test_add_step_to_paused_session(self) -> None:
        """Testa erro ao adicionar passo a sessão pausada."""
        session_result = self.server.start_session("Teste")
        session_id = session_result["session_id"]

        # Pausar sessão
        session = self.server._sessions[session_id]
        session.status = "paused"

        with pytest.raises(ValueError, match="Sessão não está ativa"):
            self.server.add_step(session_id, "Conteúdo", "thought")
