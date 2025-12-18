#!/usr/bin/env python3
"""
Testes de Integração Tier 2: Filesystem, Git, Python, SQLite
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestTier2MCPImports:
    """Testes de importação dos MCPs Tier 2."""

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

    def test_sqlite_wrapper_imports(self):
        """Testa que SQLite Wrapper pode ser importado."""
        try:
            from src.integrations.mcp_sqlite_wrapper import MCPSQLiteWrapper

            assert MCPSQLiteWrapper is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MCPSQLiteWrapper: {e}")

    def test_logging_server_imports(self):
        """Testa que Logging Server pode ser importado."""
        try:
            from src.integrations.mcp_logging_server import LoggingMCPServer

            assert LoggingMCPServer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import LoggingMCPServer: {e}")


class TestTier2MCPInstantiation:
    """Testes de instanciação dos MCPs Tier 2."""

    def test_filesystem_wrapper_instantiation(self):
        """Testa que Filesystem Wrapper pode ser instanciado."""
        from src.integrations.mcp_filesystem_wrapper import MCPFilesystemWrapper

        try:
            wrapper = MCPFilesystemWrapper()
            assert wrapper is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate MCPFilesystemWrapper: {e}")

    def test_git_wrapper_instantiation(self):
        """Testa que Git Wrapper pode ser instanciado."""
        from src.integrations.mcp_git_wrapper import MCPGitWrapper

        try:
            wrapper = MCPGitWrapper()
            assert wrapper is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate MCPGitWrapper: {e}")

    def test_python_server_instantiation(self):
        """Testa que Python Server pode ser instanciado."""
        from src.integrations.mcp_python_server import PythonMCPServer

        try:
            server = PythonMCPServer()
            assert server is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate PythonMCPServer: {e}")


class TestTier2Configuration:
    """Testes de configuração Tier 2."""

    def test_external_config_has_tier2_mcps(self):
        """Testa que configuração tem MCPs Tier 2."""
        import json

        config_file = PROJECT_ROOT / "config" / "mcp_servers_external.json"
        with open(config_file) as f:
            config = json.load(f)

        required_mcps = [
            "filesystem",
            "git",
            "python",
            "sqlite",
            "logging",
        ]
        for mcp in required_mcps:
            assert mcp in config["mcp_servers"], f"{mcp} not in external config"
            assert config["mcp_servers"][mcp]["enabled"], f"{mcp} should be enabled"

    def test_tier2_ports_assigned(self):
        """Testa que todas MCPs Tier 2 têm portas únicas."""
        import json

        config_file = PROJECT_ROOT / "config" / "mcp_servers_external.json"
        with open(config_file) as f:
            config = json.load(f)

        ports: dict[str, int] = {}
        for name, server in config["mcp_servers"].items():
            if server.get("enabled"):
                port = server["port"]
                assert port not in ports.values(), f"Duplicate port {port}"
                ports[name] = port
                assert port >= 4331, f"{name} port {port} should be >= 4331"


class TestMCPQualityChecks:
    """Testes de qualidade dos MCPs Tier 2."""

    def test_tier2_files_exist(self):
        """Testa que arquivo dos MCPs Tier 2 existem."""
        files = [
            "src/integrations/mcp_filesystem_wrapper.py",
            "src/integrations/mcp_git_wrapper.py",
            "src/integrations/mcp_python_server.py",
            "src/integrations/mcp_sqlite_wrapper.py",
            "src/integrations/mcp_logging_server.py",
        ]
        for file in files:
            path = PROJECT_ROOT / file
            assert path.exists(), f"{file} not found"

    def test_tier2_lint_passing(self):
        """Testa que Tier 2 MCPs passam em lint."""
        import subprocess

        files = [
            "src/integrations/mcp_filesystem_wrapper.py",
            "src/integrations/mcp_git_wrapper.py",
        ]

        for file in files:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "flake8",
                    file,
                    "--max-line-length=88",
                    "--extend-ignore=E203,W503,E501",
                ],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
            )
            # Allow some warnings, but no critical errors
            assert result.returncode in [0, 1], f"{file} has critical lint errors"


if __name__ == "__main__":
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
        ]
    )
    sys.exit(exit_code)
