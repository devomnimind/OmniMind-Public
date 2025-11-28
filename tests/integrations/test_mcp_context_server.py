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
        result = server.store_context(
            level="high", content="Test content", metadata={"key": "value"}
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result["status"] == "stored"
        assert result["level"] == "high"

    def test_store_context_different_levels(self) -> None:
        """Testa armazenamento em diferentes níveis."""
        server = ContextMCPServer()

        # Teste com nível "low"
        result_low = server.store_context(level="low", content="Low level content", metadata={})
        assert result_low["level"] == "low"
        assert result_low["status"] == "stored"

        # Teste com nível "medium"
        result_med = server.store_context(
            level="medium",
            content="Medium level content",
            metadata={"priority": "normal"},
        )
        assert result_med["level"] == "medium"
        assert result_med["status"] == "stored"

    def test_retrieve_context(self) -> None:
        """Testa recuperação de contexto."""
        server = ContextMCPServer()
        result = server.retrieve_context(level="high", query="test")
        assert result is not None
        assert isinstance(result, dict)
        assert "content" in result
        assert "level" in result
        assert result["level"] == "high"

    def test_retrieve_context_without_query(self) -> None:
        """Testa recuperação de contexto sem query."""
        server = ContextMCPServer()
        result = server.retrieve_context(level="low")
        assert result is not None
        assert result["level"] == "low"
        assert "content" in result

    def test_compress_context(self) -> None:
        """Testa compressão de contexto."""
        server = ContextMCPServer()
        result = server.compress_context(level="high")
        assert result is not None
        assert isinstance(result, dict)
        assert result["status"] == "compressed"
        assert "ratio" in result
        assert isinstance(result["ratio"], float)
        assert result["ratio"] == 0.5

    def test_compress_context_different_levels(self) -> None:
        """Testa compressão em diferentes níveis."""
        server = ContextMCPServer()

        for level in ["low", "medium", "high"]:
            result = server.compress_context(level=level)
            assert result["status"] == "compressed"
            assert result["ratio"] == 0.5

    def test_snapshot_context(self) -> None:
        """Testa criação de snapshot de contexto."""
        server = ContextMCPServer()
        result = server.snapshot_context()
        assert result is not None
        assert isinstance(result, dict)
        assert "snapshot_id" in result
        assert result["snapshot_id"] == "snap_123"

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
        result = server.store_context(level="test", content="Content without metadata", metadata={})
        assert result["status"] == "stored"
        assert result["level"] == "test"

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
            level="high", content="Complex content", metadata=complex_metadata
        )
        assert result["status"] == "stored"
        assert result["level"] == "high"
