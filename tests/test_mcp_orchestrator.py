"""
Testes para o MCP Orchestrator.

Tests the lifecycle management, health checks, and metrics collection
of the MCP Orchestrator system.
"""

import json
import tempfile
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.integrations.mcp_orchestrator import (
    MCPOrchestrator,
    MCPOrchestratorError,
    MCPServerConfig,
    MCPServerStatus,
)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Fixture para configuração de teste."""
    return {
        "version": "1.0.0",
        "global_settings": {
            "audit_enabled": True,
            "log_level": "INFO",
            "health_check_interval_seconds": 60,
        },
        "mcp_servers": {
            "test_server": {
                "enabled": True,
                "priority": "high",
                "tier": 1,
                "command": "echo",
                "args": ["test"],
                "audit_category": "test_mcp",
                "features": {"test_feature": True},
            },
            "disabled_server": {
                "enabled": False,
                "priority": "low",
                "tier": 3,
                "command": "echo",
                "args": ["disabled"],
                "audit_category": "disabled_mcp",
            },
        },
        "orchestrator": {
            "health_checks": {"enabled": True, "interval_seconds": 60},
        },
    }


@pytest.fixture
def temp_config_file(mock_config: Dict[str, Any]) -> Path:
    """Cria arquivo de configuração temporário."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(mock_config, f)
        path = Path(f.name)

    yield path

    # Cleanup
    if path.exists():
        path.unlink()


class TestMCPServerConfig:
    """Testes para MCPServerConfig."""

    def test_server_config_creation(self) -> None:
        """Testa criação de configuração de servidor."""
        config = MCPServerConfig(
            name="test",
            enabled=True,
            priority="high",
            tier=1,
            command="python",
            args=["-m", "test"],
            audit_category="test_mcp",
        )

        assert config.name == "test"
        assert config.enabled is True
        assert config.priority == "high"
        assert config.tier == 1
        assert config.command == "python"
        assert config.args == ["-m", "test"]
        assert config.audit_category == "test_mcp"


class TestMCPServerStatus:
    """Testes para MCPServerStatus."""

    def test_server_status_creation(self) -> None:
        """Testa criação de status de servidor."""
        status = MCPServerStatus(
            name="test",
            enabled=True,
            running=True,
            healthy=True,
            last_health_check=time.time(),
            uptime_seconds=60.0,
            total_requests=100,
            failed_requests=5,
            avg_response_time_ms=50.0,
        )

        assert status.name == "test"
        assert status.running is True
        assert status.healthy is True
        assert status.total_requests == 100
        assert status.failed_requests == 5


class TestMCPOrchestrator:
    """Testes para MCPOrchestrator."""

    def test_orchestrator_initialization(self, temp_config_file: Path) -> None:
        """Testa inicialização do orquestrador."""
        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        assert orchestrator.config_path == temp_config_file
        assert len(orchestrator.servers) == 2  # test_server + disabled_server
        assert "test_server" in orchestrator.servers
        assert "disabled_server" in orchestrator.servers

    def test_orchestrator_missing_config(self) -> None:
        """Testa erro quando configuração não existe."""
        with pytest.raises(MCPOrchestratorError, match="não encontrado"):
            MCPOrchestrator(config_path="/nonexistent/config.json")

    def test_load_server_configs(self, temp_config_file: Path) -> None:
        """Testa carregamento de configurações de servidores."""
        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        # Verificar test_server
        test_server = orchestrator.servers["test_server"]
        assert test_server.name == "test_server"
        assert test_server.enabled is True
        assert test_server.priority == "high"
        assert test_server.tier == 1

        # Verificar disabled_server
        disabled = orchestrator.servers["disabled_server"]
        assert disabled.enabled is False

    def test_get_server_status(self, temp_config_file: Path) -> None:
        """Testa obtenção de status de servidor."""
        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        status = orchestrator.get_server_status("test_server")
        assert status.name == "test_server"
        assert status.enabled is True
        assert status.running is False  # Não iniciado ainda

    def test_get_server_status_not_found(self, temp_config_file: Path) -> None:
        """Testa erro ao buscar servidor inexistente."""
        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        with pytest.raises(MCPOrchestratorError, match="não encontrado"):
            orchestrator.get_server_status("nonexistent")

    def test_get_all_statuses(self, temp_config_file: Path) -> None:
        """Testa obtenção de todos os status."""
        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        statuses = orchestrator.get_all_statuses()
        assert len(statuses) == 2
        assert "test_server" in statuses
        assert "disabled_server" in statuses

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_start_server(
        self,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa inicialização de servidor."""
        # Mock do processo
        mock_process = Mock()
        mock_process.poll.return_value = None  # Processo rodando
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        # Mock do audit
        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)
        result = orchestrator.start_server("test_server")

        assert result is True
        assert "test_server" in orchestrator.processes
        assert orchestrator.status["test_server"].running is True

        # Verificar se processo foi iniciado
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "echo" in call_args
        assert "test" in call_args

    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_start_disabled_server(self, mock_audit: MagicMock, temp_config_file: Path) -> None:
        """Testa que servidor desabilitado não é iniciado."""
        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)
        result = orchestrator.start_server("disabled_server")

        assert result is False
        assert "disabled_server" not in orchestrator.processes

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    @patch("time.sleep")  # Mock sleep para acelerar testes
    def test_start_server_already_running(
        self,
        mock_sleep: MagicMock,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa iniciar servidor que já está rodando."""
        mock_process = Mock()
        # poll() sempre retorna None (processo ainda rodando)
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        # Primeiro start
        result1 = orchestrator.start_server("test_server")
        assert result1 is True

        # Segundo start (já rodando)
        result2 = orchestrator.start_server("test_server")
        assert result2 is True

        # Deve ter chamado Popen apenas uma vez
        assert mock_popen.call_count == 1

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_stop_server(
        self,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa parada de servidor."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait = Mock()
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        # Iniciar servidor
        orchestrator.start_server("test_server")

        # Parar servidor
        result = orchestrator.stop_server("test_server")

        assert result is True
        assert "test_server" not in orchestrator.processes
        assert orchestrator.status["test_server"].running is False

        # Verificar chamadas
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called()

    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_stop_server_not_running(self, mock_audit: MagicMock, temp_config_file: Path) -> None:
        """Testa parar servidor que não está rodando."""
        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)
        result = orchestrator.stop_server("test_server")

        assert result is True  # Sucesso (já estava parado)

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    @patch("time.sleep")  # Mock sleep para acelerar testes
    def test_restart_server(
        self,
        mock_sleep: MagicMock,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa reinício de servidor."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait = Mock()
        mock_process.terminate = Mock()
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        # Iniciar
        orchestrator.start_server("test_server")

        # Reiniciar
        result = orchestrator.restart_server("test_server")

        assert result is True
        # Deve ter chamado Popen duas vezes (start + restart)
        assert mock_popen.call_count == 2

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_check_server_health(
        self,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa verificação de saúde de servidor."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Rodando
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        # Iniciar servidor
        orchestrator.start_server("test_server")

        # Verificar saúde
        healthy = orchestrator.check_server_health("test_server")

        assert healthy is True
        assert orchestrator.status["test_server"].healthy is True

    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_check_server_health_not_running(
        self, mock_audit: MagicMock, temp_config_file: Path
    ) -> None:
        """Testa health check de servidor não rodando."""
        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        healthy = orchestrator.check_server_health("test_server")

        assert healthy is False
        assert orchestrator.status["test_server"].healthy is False

    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_export_metrics(self, mock_audit: MagicMock, temp_config_file: Path) -> None:
        """Testa exportação de métricas."""
        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        metrics = orchestrator.export_metrics()

        assert "timestamp" in metrics
        assert "total_servers" in metrics
        assert metrics["total_servers"] == 2
        assert "enabled_servers" in metrics
        assert metrics["enabled_servers"] == 1
        assert "servers" in metrics
        assert "test_server" in metrics["servers"]

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_context_manager(
        self,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa uso como context manager."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait = Mock()
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        with MCPOrchestrator(config_path=temp_config_file) as orchestrator:
            # Dentro do contexto, servidor habilitado deve estar rodando
            assert "test_server" in orchestrator.processes

        # Fora do contexto, servidores devem estar parados
        # (difícil testar sem acesso direto ao estado)
        mock_process.terminate.assert_called()

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    @patch("time.sleep")  # Mock sleep para acelerar testes
    def test_start_all_servers(
        self,
        mock_sleep: MagicMock,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa iniciar todos servidores."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)
        results = orchestrator.start_all_servers()

        # test_server habilitado deve ser iniciado
        assert results["test_server"] is True

        # disabled_server não deve ser iniciado
        assert results["disabled_server"] is False

    @patch("subprocess.Popen")
    @patch("src.integrations.mcp_orchestrator.get_audit_system")
    def test_stop_all_servers(
        self,
        mock_audit: MagicMock,
        mock_popen: MagicMock,
        temp_config_file: Path,
    ) -> None:
        """Testa parar todos servidores."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait = Mock()
        mock_popen.return_value = mock_process

        mock_audit_system = Mock()
        mock_audit.return_value = mock_audit_system

        orchestrator = MCPOrchestrator(config_path=temp_config_file)

        # Iniciar servidores
        orchestrator.start_all_servers()

        # Parar todos
        results = orchestrator.stop_all_servers()

        # test_server deve ser parado
        assert results["test_server"] is True

        # Processos devem estar vazios
        assert len(orchestrator.processes) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
