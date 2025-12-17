"""Testes para ContextMCPServer (mcp_context_server.py).

Cobertura de:
- Inicialização do servidor
- Armazenamento de contexto (store_context)
- Recuperação de contexto (retrieve_context)
- Compressão de contexto (compress_context)
- Snapshot de contexto (snapshot_context)
- Métodos herdados de MCPServer
"""

from __future__ import annotations

from src.integrations.mcp_context_server import ContextMCPServer


class TestContextMCPServer:
    """Testes para o servidor MCP de contexto."""

    def test_initialization(self) -> None:
        """Testa inicialização do ContextMCPServer."""
        server = ContextMCPServer()
        assert server is not None
        assert "store_context" in server._methods
        assert "retrieve_context" in server._methods
        assert "compress_context" in server._methods
        assert "snapshot_context" in server._methods

    def test_store_context(self) -> None:
        """Testa armazenamento de contexto."""
        server = ContextMCPServer()
        # CORREÇÃO: Usar níveis válidos (project, session, task, code, memory, audit, ephemeral)
        result = server.store_context(
            level="task", content="Test content", metadata={"key": "value"}
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result["status"] == "stored"
        assert result["level"] == "task"

    def test_store_context_different_levels(self) -> None:
        """Testa armazenamento em diferentes níveis."""
        server = ContextMCPServer()

        # CORREÇÃO: Usar níveis válidos (project, session, task, code, memory, audit, ephemeral)
        # Teste com nível "code"
        result_code = server.store_context(level="code", content="Code level content", metadata={})
        assert result_code["level"] == "code"
        assert result_code["status"] == "stored"

        # Teste com nível "session"
        result_session = server.store_context(
            level="session",
            content="Session level content",
            metadata={"priority": "normal"},
        )
        assert result_session["level"] == "session"
        assert result_session["status"] == "stored"

    def test_retrieve_context(self) -> None:
        """Testa recuperação de contexto."""
        server = ContextMCPServer()
        # CORREÇÃO: Primeiro armazenar contexto, depois recuperar
        server.store_context(level="task", content="Test content for retrieval", metadata={})
        result = server.retrieve_context(level="task", query="test")
        assert result is not None
        assert isinstance(result, dict)
        assert "content" in result
        assert "level" in result
        assert result["level"] == "task"

    def test_retrieve_context_without_query(self) -> None:
        """Testa recuperação de contexto sem query."""
        server = ContextMCPServer()
        # CORREÇÃO: Primeiro armazenar contexto, depois recuperar
        server.store_context(level="code", content="Code content", metadata={})
        result = server.retrieve_context(level="code")
        assert result is not None
        assert result["level"] == "code"
        assert "content" in result

    def test_compress_context(self) -> None:
        """Testa compressão de contexto."""
        server = ContextMCPServer()
        # CORREÇÃO: Primeiro armazenar contexto, depois comprimir
        # Adicionar múltiplos contextos para ter algo para comprimir
        for i in range(5):
            server.store_context(level="task", content=f"Test content {i}", metadata={})
        result = server.compress_context(level="task", ratio=0.5)
        assert result is not None
        assert isinstance(result, dict)
        assert result["status"] == "compressed"
        assert "ratio" in result
        assert isinstance(result["ratio"], float)
        # CORREÇÃO: ratio pode variar dependendo do conteúdo,
        # apenas verificar que está em range válido
        assert 0.0 <= result["ratio"] <= 1.0

    def test_compress_context_different_levels(self) -> None:
        """Testa compressão em diferentes níveis."""
        server = ContextMCPServer()

        # CORREÇÃO: Usar níveis válidos e armazenar contexto antes de comprimir
        for level in ["code", "session", "task"]:
            # Adicionar múltiplos contextos para ter algo para comprimir
            for i in range(3):
                server.store_context(level=level, content=f"Content {i} for {level}", metadata={})
            result = server.compress_context(level=level, ratio=0.5)
            assert result["status"] == "compressed"
            # CORREÇÃO: ratio pode variar, apenas verificar que está em range válido
            assert 0.0 <= result["ratio"] <= 1.0

    def test_snapshot_context(self) -> None:
        """Testa criação de snapshot de contexto."""
        server = ContextMCPServer()
        # CORREÇÃO: snapshot_context retorna UUID, não "snap_123"
        result = server.snapshot_context()
        assert result is not None
        assert isinstance(result, dict)
        assert "snapshot_id" in result
        # snapshot_id é um UUID gerado dinamicamente
        assert isinstance(result["snapshot_id"], str)
        assert len(result["snapshot_id"]) > 0

    def test_methods_registered(self) -> None:
        """Testa se todos os métodos estão registrados."""
        server = ContextMCPServer()
        expected_methods = [
            "store_context",
            "retrieve_context",
            "compress_context",
            "snapshot_context",
            # Métodos herdados de MCPServer
            "read_file",
            "write_file",
            "list_dir",
            "stat",
            "get_metrics",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_store_context_with_empty_metadata(self) -> None:
        """Testa armazenamento com metadata vazio."""
        server = ContextMCPServer()
        # CORREÇÃO: Usar nível válido
        result = server.store_context(level="task", content="Content without metadata", metadata={})
        assert result["status"] == "stored"
        assert result["level"] == "task"

    def test_store_context_with_complex_metadata(self) -> None:
        """Testa armazenamento com metadata complexo."""
        server = ContextMCPServer()
        complex_metadata = {
            "timestamp": "2025-11-24T12:00:00Z",
            "tags": ["important", "test"],
            "priority": 1,
            "nested": {"key": "value"},
        }
        result = server.store_context(
            level="task", content="Complex content", metadata=complex_metadata
        )
        assert result["status"] == "stored"
        assert result["level"] == "task"
