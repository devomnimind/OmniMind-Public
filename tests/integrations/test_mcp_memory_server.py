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

"""Testes para MemoryMCPServer (mcp_memory_server.py).

Cobertura de:
- Inicialização do servidor
- Armazenamento de memória (store_memory)
- Recuperação de memória (retrieve_memory)
- Atualização de memória (update_memory)
- Deleção de memória (delete_memory)
- Criação de associações (create_association)
- Recuperação de grafo (get_memory_graph)
- Consolidação de memórias (consolidate_memories)
- Exportação de grafo (export_graph)
"""

from __future__ import annotations

from src.integrations.mcp_memory_server import MemoryMCPServer


class TestMemoryMCPServer:
    """Testes para o servidor MCP de memória."""

    def test_initialization(self) -> None:
        """Testa inicialização do MemoryMCPServer."""
        server = MemoryMCPServer()
        assert server is not None
        expected_methods = [
            "store_memory",
            "retrieve_memory",
            "update_memory",
            "delete_memory",
            "create_association",
            "get_memory_graph",
            "consolidate_memories",
            "export_graph",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_store_memory_basic(self) -> None:
        """Testa armazenamento básico de memória."""
        server = MemoryMCPServer()
        result = server.store_memory(content="Test memory content", metadata={"type": "test"})
        assert result is not None
        assert isinstance(result, dict)
        assert "id" in result
        assert "status" in result
        assert result["id"] == "mem_stub_123"
        assert result["status"] == "stored"

    def test_store_memory_with_complex_metadata(self) -> None:
        """Testa armazenamento com metadata complexo."""
        server = MemoryMCPServer()
        metadata = {
            "type": "episodic",
            "timestamp": "2025-11-24T12:00:00Z",
            "tags": ["important", "conversation"],
            "priority": 5,
            "source": "user_interaction",
        }
        result = server.store_memory(content="Complex memory with rich metadata", metadata=metadata)
        assert result["status"] == "stored"
        assert result["id"] == "mem_stub_123"

    def test_store_memory_empty_metadata(self) -> None:
        """Testa armazenamento com metadata vazio."""
        server = MemoryMCPServer()
        result = server.store_memory(content="Memory without metadata", metadata={})
        assert result["status"] == "stored"

    def test_retrieve_memory_basic(self) -> None:
        """Testa recuperação básica de memória."""
        server = MemoryMCPServer()
        result = server.retrieve_memory(query="test")
        assert result is not None
        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        assert result["results"] == []

    def test_retrieve_memory_with_limit(self) -> None:
        """Testa recuperação com limite especificado."""
        server = MemoryMCPServer()
        result = server.retrieve_memory(query="memory", limit=5)
        assert result is not None
        assert "results" in result

    def test_retrieve_memory_default_limit(self) -> None:
        """Testa recuperação com limite padrão."""
        server = MemoryMCPServer()
        result = server.retrieve_memory(query="search")
        assert result is not None
        assert "results" in result

    def test_update_memory_basic(self) -> None:
        """Testa atualização básica de memória."""
        server = MemoryMCPServer()
        result = server.update_memory(memory_id="mem_123", content="Updated content")
        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == "mem_123"
        assert result["status"] == "updated"

    def test_update_memory_different_ids(self) -> None:
        """Testa atualização com diferentes IDs."""
        server = MemoryMCPServer()
        ids = ["mem_001", "mem_abc", "mem_xyz_123"]
        for memory_id in ids:
            result = server.update_memory(memory_id=memory_id, content="New content")
            assert result["id"] == memory_id
            assert result["status"] == "updated"

    def test_delete_memory_basic(self) -> None:
        """Testa deleção básica de memória."""
        server = MemoryMCPServer()
        result = server.delete_memory(memory_id="mem_to_delete")
        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == "mem_to_delete"
        assert result["status"] == "deleted"

    def test_delete_memory_multiple(self) -> None:
        """Testa deleção de múltiplas memórias."""
        server = MemoryMCPServer()
        ids_to_delete = ["mem_1", "mem_2", "mem_3"]
        for memory_id in ids_to_delete:
            result = server.delete_memory(memory_id=memory_id)
            assert result["id"] == memory_id
            assert result["status"] == "deleted"

    def test_create_association_basic(self) -> None:
        """Testa criação básica de associação."""
        server = MemoryMCPServer()
        result = server.create_association(
            source_id="mem_source", target_id="mem_target", type="related"
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result["source"] == "mem_source"
        assert result["target"] == "mem_target"
        assert result["type"] == "related"

    def test_create_association_different_types(self) -> None:
        """Testa criação de associações com diferentes tipos."""
        server = MemoryMCPServer()
        association_types = [
            "causality",
            "similarity",
            "temporal",
            "hierarchical",
            "semantic",
        ]
        for assoc_type in association_types:
            result = server.create_association(
                source_id="source_1", target_id="target_1", type=assoc_type
            )
            assert result["type"] == assoc_type

    def test_get_memory_graph_basic(self) -> None:
        """Testa recuperação básica do grafo de memória."""
        server = MemoryMCPServer()
        result = server.get_memory_graph()
        assert result is not None
        assert isinstance(result, dict)
        assert "nodes" in result
        assert "edges" in result
        assert isinstance(result["nodes"], list)
        assert isinstance(result["edges"], list)
        assert result["nodes"] == []
        assert result["edges"] == []

    def test_consolidate_memories_basic(self) -> None:
        """Testa consolidação básica de memórias."""
        server = MemoryMCPServer()
        result = server.consolidate_memories()
        assert result is not None
        assert isinstance(result, dict)
        assert "consolidated_count" in result
        assert result["consolidated_count"] == 0

    def test_export_graph_default_format(self) -> None:
        """Testa exportação de grafo com formato padrão."""
        server = MemoryMCPServer()
        result = server.export_graph()
        assert result is not None
        assert isinstance(result, dict)
        assert "format" in result
        assert "data" in result
        assert result["format"] == "json"
        assert isinstance(result["data"], dict)

    def test_export_graph_json_format(self) -> None:
        """Testa exportação de grafo em formato JSON."""
        server = MemoryMCPServer()
        result = server.export_graph(format="json")
        assert result["format"] == "json"
        assert "data" in result

    def test_export_graph_different_formats(self) -> None:
        """Testa exportação em diferentes formatos."""
        server = MemoryMCPServer()
        formats = ["json", "xml", "graphml", "dot"]
        for fmt in formats:
            result = server.export_graph(format=fmt)
            assert result["format"] == fmt
            assert "data" in result

    def test_methods_registered(self) -> None:
        """Testa se todos os métodos estão registrados."""
        server = MemoryMCPServer()
        expected_methods = [
            "store_memory",
            "retrieve_memory",
            "update_memory",
            "delete_memory",
            "create_association",
            "get_memory_graph",
            "consolidate_memories",
            "export_graph",
            # Métodos herdados de MCPServer
            "read_file",
            "write_file",
            "list_dir",
            "stat",
            "get_metrics",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_retrieve_memory_various_queries(self) -> None:
        """Testa recuperação com várias queries diferentes."""
        server = MemoryMCPServer()
        queries = [
            "episodic memories",
            "semantic knowledge",
            "recent events",
            "important conversations",
        ]
        for query in queries:
            result = server.retrieve_memory(query=query, limit=20)
            assert result is not None
            assert "results" in result
