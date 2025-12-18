#!/usr/bin/env python3
"""
Testes de Integração Tier 1: Memory + Thinking + Context
Valida que MCPs críticos funcionam juntos corretamente
"""
import json
import sys
from pathlib import Path

import pytest

from src.integrations.mcp_context_server import ContextMCPServer
from src.integrations.mcp_memory_server import MemoryMCPServer
from src.integrations.mcp_thinking_server import ThinkingMCPServer

PROJECT_ROOT = Path(__file__).parent.parent  # /home/fahbrain/projects/omnimind
sys.path.insert(0, str(PROJECT_ROOT))


class TestMemoryIntegration:
    """Testes do Memory Server."""

    def test_memory_server_imports(self):
        """Testa que MemoryMCPServer pode ser importado."""

        assert MemoryMCPServer is not None

    def test_memory_server_tools_defined(self):
        """Testa que ferramentas de memória estão definidas."""

        server = MemoryMCPServer()
        tools = server.get_tools()

        expected_tools = [
            "store_memory",
            "retrieve_memory",
            "update_memory",
            "delete_memory",
            "create_association",
        ]

        tool_names = [t.get("name") for t in tools]
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in memory server"

    def test_memory_configuration(self):
        """Testa configuração de memória."""

        server = MemoryMCPServer()
        config = server.config

        assert config.port == 4321
        assert config.enabled is True
        assert config.priority == "critical"


class TestThinkingIntegration:
    """Testes do Thinking Server."""

    def test_thinking_server_imports(self):
        """Testa que ThinkingMCPServer pode ser importado."""

        assert ThinkingMCPServer is not None

    def test_thinking_server_tools_defined(self):
        """Testa que ferramentas de pensamento estão definidas."""

        server = ThinkingMCPServer()
        tools = server.get_tools()

        expected_tools = [
            "start_session",
            "add_step",
            "get_history",
            "branch_thinking",
            "merge_branches",
        ]

        tool_names = [t.get("name") for t in tools]
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in thinking server"

    def test_thinking_configuration(self):
        """Testa configuração de pensamento."""

        server = ThinkingMCPServer()
        config = server.config

        assert config.port == 4322
        assert config.enabled is True
        assert config.priority == "critical"


class TestContextIntegration:
    """Testes do Context Server."""

    def test_context_server_imports(self):
        """Testa que ContextMCPServer pode ser importado."""

        assert ContextMCPServer is not None

    def test_context_server_tools_defined(self):
        """Testa que ferramentas de contexto estão definidas."""

        server = ContextMCPServer()
        tools = server.get_tools()

        expected_tools = [
            "get_context",
            "set_context",
            "compress_context",
            "get_priority_levels",
        ]

        tool_names = [t.get("name") for t in tools]
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in context server"

    def test_context_configuration(self):
        """Testa configuração de contexto."""

        server = ContextMCPServer()
        config = server.config

        assert config.port == 4323
        assert config.enabled is True
        assert config.priority == "high"


class TestMCPInteroperability:
    """Testes de interoperabilidade entre MCPs."""

    def test_all_servers_have_health_endpoint(self):
        """Testa que todos servidores têm endpoint de health."""

        servers = [MemoryMCPServer(), ThinkingMCPServer(), ContextMCPServer()]

        for server in servers:
            assert hasattr(
                server, "get_health"
            ), f"{server.__class__.__name__} missing get_health method"

    def test_all_servers_support_mcp_protocol(self):
        """Testa que todos servidores suportam protocolo MCP."""

        servers = [MemoryMCPServer(), ThinkingMCPServer(), ContextMCPServer()]

        for server in servers:
            assert hasattr(
                server, "get_tools"
            ), f"{server.__class__.__name__} missing get_tools method"
            tools = server.get_tools()
            assert isinstance(tools, list), "get_tools() should return list"
            assert len(tools) > 0, f"{server.__class__.__name__} has no tools"

    def test_configuration_consistency(self):
        """Testa que configurações são consistentes."""

        servers = {
            "memory": MemoryMCPServer(),
            "thinking": ThinkingMCPServer(),
            "context": ContextMCPServer(),
        }

        for name, server in servers.items():
            config = server.config
            assert config.host == "127.0.0.1", f"{name}: host should be localhost"
            assert config.port > 4320, f"{name}: port should be > 4320"
            assert config.enabled is True, f"{name}: should be enabled"


class TestMCPConfiguration:
    """Testes de configuração dos MCPs."""

    def test_mcp_servers_config_exists(self):
        """Testa que arquivo de configuração existe."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers.json"
        assert config_file.exists(), "mcp_servers.json not found"

    def test_mcp_internal_config_exists(self):
        """Testa que arquivo de configuração interna existe."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers_internal.json"
        assert config_file.exists(), "mcp_servers_internal.json not found"

    def test_mcp_external_config_exists(self):
        """Testa que arquivo de configuração externa existe."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers_external.json"
        assert config_file.exists(), "mcp_servers_external.json not found"

    def test_internal_config_has_tier1_mcps(self):
        """Testa que configuração interna tem MCPs Tier 1."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers_internal.json"

        with open(config_file) as f:
            config = json.load(f)

        required_mcps = ["memory", "sequential_thinking", "context"]
        for mcp in required_mcps:
            assert mcp in config["mcp_servers"], f"{mcp} not in internal config"
            assert config["mcp_servers"][mcp]["enabled"], f"{mcp} should be enabled"


class TestMCPStartupScripts:
    """Testes dos scripts de startup."""

    def test_start_mcp_internal_exists(self):
        """Testa que script de startup interno existe."""
        script = PROJECT_ROOT / "scripts" / "production" / "start_mcp_internal.sh"
        assert script.exists(), "start_mcp_internal.sh not found"

    def test_start_mcp_external_exists(self):
        """Testa que script de startup externo existe."""
        script = PROJECT_ROOT / "scripts" / "production" / "start_mcp_external.sh"
        assert script.exists(), "start_mcp_external.sh not found"

    def test_start_mcp_servers_exists(self):
        """Testa que script de startup principal existe."""
        script = PROJECT_ROOT / "scripts" / "production" / "start_mcp_servers.sh"
        assert script.exists(), "start_mcp_servers.sh not found"


# Marcadores para grouping
def pytest_configure(config):
    """Configurar marcadores customizados."""
    config.addinivalue_line("markers", "tier1: Testes Tier 1 (Memory/Thinking/Context)")
    config.addinivalue_line("markers", "integration: Testes de integração entre MCPs")
    config.addinivalue_line("markers", "config: Testes de configuração")


if __name__ == "__main__":
    # Executar testes
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-m",
            "not slow",
        ]
    )
    sys.exit(exit_code)
