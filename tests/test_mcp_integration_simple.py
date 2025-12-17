#!/usr/bin/env python3
"""
Testes de Integração Tier 1 SIMPLIFICADO
Foco: Validar que MCPs conseguem ser importados e iniciados
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestMCPImports:
    """Testes básicos de importação dos MCPs."""

    def test_memory_server_imports(self):
        """Testa que Memory Server pode ser importado."""
        try:
            from src.integrations.mcp_memory_server import MemoryMCPServer

            assert MemoryMCPServer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MemoryMCPServer: {e}")

    def test_thinking_server_imports(self):
        """Testa que Thinking Server pode ser importado."""
        try:
            from src.integrations.mcp_thinking_server import ThinkingMCPServer

            assert ThinkingMCPServer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ThinkingMCPServer: {e}")

    def test_context_server_imports(self):
        """Testa que Context Server pode ser importado."""
        try:
            from src.integrations.mcp_context_server import ContextMCPServer

            assert ContextMCPServer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ContextMCPServer: {e}")

    def test_filesystem_wrapper_imports(self):
        """Testa que Filesystem Wrapper pode ser importado."""
        try:
            from src.integrations.mcp_filesystem_wrapper import MCPFilesystemWrapper

            assert MCPFilesystemWrapper is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MCPFilesystemWrapper: {e}")

    def test_git_wrapper_imports(self):
        """Testa que Git Wrapper pode ser importado."""
        try:
            from src.integrations.mcp_git_wrapper import MCPGitWrapper

            assert MCPGitWrapper is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MCPGitWrapper: {e}")

    def test_python_server_imports(self):
        """Testa que Python Server pode ser importado."""
        try:
            from src.integrations.mcp_python_server import PythonMCPServer

            assert PythonMCPServer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PythonMCPServer: {e}")


class TestMCPInstantiation:
    """Testes de instanciação dos MCPs."""

    def test_memory_server_instantiation(self):
        """Testa que Memory Server pode ser instanciado."""
        from src.integrations.mcp_memory_server import MemoryMCPServer

        try:
            server = MemoryMCPServer()
            assert server is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate MemoryMCPServer: {e}")

    def test_thinking_server_instantiation(self):
        """Testa que Thinking Server pode ser instanciado."""
        from src.integrations.mcp_thinking_server import ThinkingMCPServer

        try:
            server = ThinkingMCPServer()
            assert server is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate ThinkingMCPServer: {e}")

    def test_context_server_instantiation(self):
        """Testa que Context Server pode ser instanciado."""
        from src.integrations.mcp_context_server import ContextMCPServer

        try:
            server = ContextMCPServer()
            assert server is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate ContextMCPServer: {e}")


class TestConfigurationFiles:
    """Testes de configuração necessária."""

    def test_mcp_config_file_exists(self):
        """Testa que arquivo de configuração principal existe."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers.json"
        assert config_file.exists(), "config/mcp_servers.json not found"

    def test_mcp_internal_config_exists(self):
        """Testa que arquivo de configuração interna existe."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers_internal.json"
        assert config_file.exists(), "config/mcp_servers_internal.json not found"

    def test_mcp_external_config_exists(self):
        """Testa que arquivo de configuração externa existe."""
        config_file = PROJECT_ROOT / "config" / "mcp_servers_external.json"
        assert config_file.exists(), "config/mcp_servers_external.json not found"


class TestStartupScripts:
    """Testes de scripts de inicialização."""

    def test_start_mcp_internal_script_exists(self):
        """Testa que script de startup interno existe."""
        script = PROJECT_ROOT / "scripts" / "production" / "start_mcp_internal.sh"
        assert script.exists(), "scripts/production/start_mcp_internal.sh not found"

    def test_start_mcp_external_script_exists(self):
        """Testa que script de startup externo existe."""
        script = PROJECT_ROOT / "scripts" / "production" / "start_mcp_external.sh"
        assert script.exists(), "scripts/production/start_mcp_external.sh not found"

    def test_start_mcp_servers_script_exists(self):
        """Testa que script de startup principal existe."""
        script = PROJECT_ROOT / "scripts" / "production" / "start_mcp_servers.sh"
        assert script.exists(), "scripts/production/start_mcp_servers.sh not found"


class TestOrchestrator:
    """Testes do orquestrador MCP."""

    def test_orchestrator_imports(self):
        """Testa que o orquestrador pode ser importado."""
        try:
            from src.integrations.mcp_orchestrator import MCPOrchestrator

            assert MCPOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MCPOrchestrator: {e}")

    def test_orchestrator_instantiation(self):
        """Testa que o orquestrador pode ser instanciado."""
        from src.integrations.mcp_orchestrator import MCPOrchestrator

        try:
            orchestrator = MCPOrchestrator()
            assert orchestrator is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate MCPOrchestrator: {e}")


if __name__ == "__main__":
    # Executar testes
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
        ]
    )
    sys.exit(exit_code)
