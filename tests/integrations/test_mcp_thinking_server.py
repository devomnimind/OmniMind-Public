"""Testes para ThinkingMCPServer (mcp_thinking_server.py).

Cobertura de:
- Inicialização do servidor
- Início de sessão (start_session)
- Adição de passo (add_step)
- Recuperação de histórico (get_history)
- Ramificação de pensamento (branch_thinking)
- Fusão de ramificações (merge_branches)
- Avaliação de qualidade (evaluate_quality)
- Exportação de cadeia (export_chain)
- Retomada de sessão (resume_session)
"""

from __future__ import annotations

from src.integrations.mcp_thinking_server import ThinkingMCPServer


class TestThinkingMCPServer:
    """Testes para o servidor MCP de thinking."""

    def test_initialization(self) -> None:
        """Testa inicialização do ThinkingMCPServer."""
        server = ThinkingMCPServer()
        assert server is not None
        expected_methods = [
            "start_session",
            "add_step",
            "get_history",
            "branch_thinking",
            "merge_branches",
            "evaluate_quality",
            "export_chain",
            "resume_session",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_start_session_basic(self) -> None:
        """Testa início básico de sessão."""
        server = ThinkingMCPServer()
        result = server.start_session(goal="Solve problem X")
        assert result is not None
        assert isinstance(result, dict)
        assert "session_id" in result
        assert "goal" in result
        assert result["session_id"] == "sess_stub_123"
        assert result["goal"] == "Solve problem X"

    def test_start_session_different_goals(self) -> None:
        """Testa início de sessão com diferentes objetivos."""
        server = ThinkingMCPServer()
        goals = ["Analyze data", "Generate code", "Debug issue", "Plan architecture"]
        for goal in goals:
            result = server.start_session(goal=goal)
            assert result["goal"] == goal
            assert result["session_id"] == "sess_stub_123"

    def test_start_session_empty_goal(self) -> None:
        """Testa início de sessão com objetivo vazio."""
        server = ThinkingMCPServer()
        result = server.start_session(goal="")
        assert result is not None
        assert result["goal"] == ""

    def test_add_step_basic(self) -> None:
        """Testa adição básica de passo."""
        server = ThinkingMCPServer()
        result = server.add_step(
            session_id="sess_123", content="First thinking step", type="reasoning"
        )
        assert result is not None
        assert isinstance(result, dict)
        assert "step_id" in result
        assert "session_id" in result
        assert result["step_id"] == "step_stub_1"
        assert result["session_id"] == "sess_123"

    def test_add_step_different_types(self) -> None:
        """Testa adição de passos com diferentes tipos."""
        server = ThinkingMCPServer()
        step_types = ["reasoning", "analysis", "synthesis", "evaluation", "decision"]
        for step_type in step_types:
            result = server.add_step(
                session_id="sess_test",
                content=f"Step of type {step_type}",
                type=step_type,
            )
            assert result["session_id"] == "sess_test"
            assert result["step_id"] == "step_stub_1"

    def test_add_step_multiple_to_session(self) -> None:
        """Testa adição de múltiplos passos à mesma sessão."""
        server = ThinkingMCPServer()
        session_id = "sess_multi"
        for i in range(5):
            result = server.add_step(
                session_id=session_id, content=f"Step {i}", type="reasoning"
            )
            assert result["session_id"] == session_id

    def test_get_history_basic(self) -> None:
        """Testa recuperação básica de histórico."""
        server = ThinkingMCPServer()
        result = server.get_history(session_id="sess_123")
        assert result is not None
        assert isinstance(result, dict)
        assert "steps" in result
        assert isinstance(result["steps"], list)
        assert result["steps"] == []

    def test_get_history_different_sessions(self) -> None:
        """Testa recuperação de histórico de diferentes sessões."""
        server = ThinkingMCPServer()
        session_ids = ["sess_1", "sess_2", "sess_3"]
        for session_id in session_ids:
            result = server.get_history(session_id=session_id)
            assert result is not None
            assert "steps" in result

    def test_branch_thinking_basic(self) -> None:
        """Testa ramificação básica de pensamento."""
        server = ThinkingMCPServer()
        result = server.branch_thinking(session_id="sess_main", step_id="step_5")
        assert result is not None
        assert isinstance(result, dict)
        assert "new_session_id" in result
        assert "parent_session" in result
        assert result["new_session_id"] == "sess_branch_123"
        assert result["parent_session"] == "sess_main"

    def test_branch_thinking_different_points(self) -> None:
        """Testa ramificação em diferentes pontos."""
        server = ThinkingMCPServer()
        step_ids = ["step_1", "step_2", "step_3"]
        for step_id in step_ids:
            result = server.branch_thinking(session_id="sess_parent", step_id=step_id)
            assert result["parent_session"] == "sess_parent"
            assert result["new_session_id"] == "sess_branch_123"

    def test_merge_branches_basic(self) -> None:
        """Testa fusão básica de ramificações."""
        server = ThinkingMCPServer()
        result = server.merge_branches(session_ids=["sess_1", "sess_2"])
        assert result is not None
        assert isinstance(result, dict)
        assert "merged_session_id" in result
        assert result["merged_session_id"] == "sess_merged_123"

    def test_merge_branches_multiple(self) -> None:
        """Testa fusão de múltiplas ramificações."""
        server = ThinkingMCPServer()
        session_lists = [
            ["sess_a", "sess_b"],
            ["sess_1", "sess_2", "sess_3"],
            ["sess_x", "sess_y", "sess_z", "sess_w"],
        ]
        for sessions in session_lists:
            result = server.merge_branches(session_ids=sessions)
            assert result["merged_session_id"] == "sess_merged_123"

    def test_merge_branches_single_session(self) -> None:
        """Testa fusão com uma única sessão."""
        server = ThinkingMCPServer()
        result = server.merge_branches(session_ids=["sess_only"])
        assert result["merged_session_id"] == "sess_merged_123"

    def test_evaluate_quality_basic(self) -> None:
        """Testa avaliação básica de qualidade."""
        server = ThinkingMCPServer()
        result = server.evaluate_quality(session_id="sess_test")
        assert result is not None
        assert isinstance(result, dict)
        assert "score" in result
        assert "feedback" in result
        assert result["score"] == 0.8
        assert result["feedback"] == "Good thinking"

    def test_evaluate_quality_different_sessions(self) -> None:
        """Testa avaliação de qualidade de diferentes sessões."""
        server = ThinkingMCPServer()
        session_ids = ["sess_eval_1", "sess_eval_2", "sess_eval_3"]
        for session_id in session_ids:
            result = server.evaluate_quality(session_id=session_id)
            assert isinstance(result["score"], float)
            assert isinstance(result["feedback"], str)
            assert 0 <= result["score"] <= 1

    def test_export_chain_basic(self) -> None:
        """Testa exportação básica de cadeia."""
        server = ThinkingMCPServer()
        result = server.export_chain(session_id="sess_export")
        assert result is not None
        assert isinstance(result, dict)
        assert "chain" in result
        assert isinstance(result["chain"], list)
        assert result["chain"] == []

    def test_export_chain_different_sessions(self) -> None:
        """Testa exportação de cadeias de diferentes sessões."""
        server = ThinkingMCPServer()
        session_ids = ["sess_exp_1", "sess_exp_2", "sess_exp_3"]
        for session_id in session_ids:
            result = server.export_chain(session_id=session_id)
            assert "chain" in result
            assert isinstance(result["chain"], list)

    def test_resume_session_basic(self) -> None:
        """Testa retomada básica de sessão."""
        server = ThinkingMCPServer()
        result = server.resume_session(session_id="sess_resume")
        assert result is not None
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "resumed"

    def test_resume_session_different_sessions(self) -> None:
        """Testa retomada de diferentes sessões."""
        server = ThinkingMCPServer()
        session_ids = ["sess_res_1", "sess_res_2", "sess_res_3"]
        for session_id in session_ids:
            result = server.resume_session(session_id=session_id)
            assert result["status"] == "resumed"

    def test_methods_registered(self) -> None:
        """Testa se todos os métodos estão registrados."""
        server = ThinkingMCPServer()
        expected_methods = [
            "start_session",
            "add_step",
            "get_history",
            "branch_thinking",
            "merge_branches",
            "evaluate_quality",
            "export_chain",
            "resume_session",
            # Métodos herdados de MCPServer
            "read_file",
            "write_file",
            "list_dir",
            "stat",
            "get_metrics",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_full_thinking_workflow(self) -> None:
        """Testa fluxo completo de pensamento."""
        server = ThinkingMCPServer()

        # Inicia sessão
        session = server.start_session(goal="Complete workflow test")
        assert session["session_id"] == "sess_stub_123"

        # Adiciona passos
        step1 = server.add_step(
            session_id=session["session_id"], content="First step", type="reasoning"
        )
        assert step1["step_id"] == "step_stub_1"

        # Obtém histórico
        history = server.get_history(session_id=session["session_id"])
        assert "steps" in history

        # Avalia qualidade
        quality = server.evaluate_quality(session_id=session["session_id"])
        assert quality["score"] == 0.8

        # Exporta cadeia
        chain = server.export_chain(session_id=session["session_id"])
        assert "chain" in chain

    def test_branching_workflow(self) -> None:
        """Testa fluxo de ramificação."""
        server = ThinkingMCPServer()

        # Cria ramificação
        branch = server.branch_thinking(session_id="sess_main", step_id="step_3")
        assert branch["new_session_id"] == "sess_branch_123"

        # Mescla ramificações
        merged = server.merge_branches(
            session_ids=["sess_main", branch["new_session_id"]]
        )
        assert merged["merged_session_id"] == "sess_merged_123"
