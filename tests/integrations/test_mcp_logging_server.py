"""Testes para LoggingMCPServer (mcp_logging_server.py).

Cobertura de:
- Inicialização do servidor
- Busca de logs (search_logs)
- Recuperação de logs recentes (get_recent_logs)
- Métodos herdados de MCPServer
"""

from __future__ import annotations

from src.integrations.mcp_logging_server import LoggingMCPServer

class TestLoggingMCPServer:
    """Testes para o servidor MCP de logging."""

    def test_initialization(self) -> None:
        """Testa inicialização do LoggingMCPServer."""
        server = LoggingMCPServer()
        assert server is not None
        assert "search_logs" in server._methods
        assert "get_recent_logs" in server._methods

    def test_search_logs_basic(self) -> None:
        """Testa busca básica de logs."""
        server = LoggingMCPServer()
        result = server.search_logs(query="error")
        assert result is not None
        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        assert result["results"] == []

    def test_search_logs_with_limit(self) -> None:
        """Testa busca de logs com limite especificado."""
        server = LoggingMCPServer()
        result = server.search_logs(query="warning", limit=50)
        assert result is not None
        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_search_logs_default_limit(self) -> None:
        """Testa busca de logs com limite padrão."""
        server = LoggingMCPServer()
        result = server.search_logs(query="info")
        assert result is not None
        assert "results" in result

    def test_search_logs_empty_query(self) -> None:
        """Testa busca com query vazia."""
        server = LoggingMCPServer()
        result = server.search_logs(query="")
        assert result is not None
        assert isinstance(result["results"], list)

    def test_search_logs_complex_query(self) -> None:
        """Testa busca com query complexa."""
        server = LoggingMCPServer()
        complex_query = "level:ERROR AND component:mcp"
        result = server.search_logs(query=complex_query, limit=200)
        assert result is not None
        assert "results" in result

    def test_get_recent_logs_basic(self) -> None:
        """Testa recuperação básica de logs recentes."""
        server = LoggingMCPServer()
        result = server.get_recent_logs()
        assert result is not None
        assert isinstance(result, dict)
        assert "logs" in result
        assert isinstance(result["logs"], list)
        assert result["logs"] == []

    def test_get_recent_logs_with_limit(self) -> None:
        """Testa recuperação de logs recentes com limite."""
        server = LoggingMCPServer()
        result = server.get_recent_logs(limit=25)
        assert result is not None
        assert "logs" in result
        assert isinstance(result["logs"], list)

    def test_get_recent_logs_default_limit(self) -> None:
        """Testa recuperação de logs com limite padrão (100)."""
        server = LoggingMCPServer()
        result = server.get_recent_logs()
        assert result is not None
        assert "logs" in result

    def test_get_recent_logs_large_limit(self) -> None:
        """Testa recuperação de logs com limite grande."""
        server = LoggingMCPServer()
        result = server.get_recent_logs(limit=1000)
        assert result is not None
        assert isinstance(result["logs"], list)

    def test_methods_registered(self) -> None:
        """Testa se todos os métodos estão registrados."""
        server = LoggingMCPServer()
        expected_methods = [
            "search_logs",
            "get_recent_logs",
            # Métodos herdados de MCPServer
            "read_file",
            "write_file",
            "list_dir",
            "stat",
            "get_metrics",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_search_logs_various_queries(self) -> None:
        """Testa busca com várias queries diferentes."""
        server = LoggingMCPServer()
        queries = [
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
            "timestamp:2025-11-24",
            "source:mcp_server",
        ]
        for query in queries:
            result = server.search_logs(query=query, limit=10)
            assert result is not None
            assert "results" in result
            assert isinstance(result["results"], list)

    def test_get_recent_logs_different_limits(self) -> None:
        """Testa recuperação com diferentes limites."""
        server = LoggingMCPServer()
        limits = [1, 10, 50, 100, 500]
        for limit in limits:
            result = server.get_recent_logs(limit=limit)
            assert result is not None
            assert "logs" in result
            assert isinstance(result["logs"], list)
