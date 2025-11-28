from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from src.security.playbooks.data_exfiltration_response import DataExfiltrationPlaybook

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

"""
Testes para src/security/playbooks/data_exfiltration_response.py.

Testa o playbook de resposta a exfiltração de dados.
"""


class MockEvent:
    """Mock event for testing."""

    def __init__(
        self,
        event_type: str = "data_exfiltration",
        description: str = "Test exfiltration",
        details: Dict[str, Any] = None,
    ):
        self.event_type = event_type
        self.description = description
        self.details = details or {}


class TestDataExfiltrationPlaybook:
    """Testes para DataExfiltrationPlaybook."""

    @pytest.fixture
    def playbook(self) -> DataExfiltrationPlaybook:
        """Cria instância do playbook."""
        return DataExfiltrationPlaybook()

    @pytest.fixture
    def mock_agent(self) -> MagicMock:
        """Cria mock agent."""
        return MagicMock()

    @pytest.fixture
    def mock_event(self) -> MockEvent:
        """Cria mock event."""
        return MockEvent(
            event_type="data_exfiltration",
            description="Suspicious data transfer detected",
            details={"remote": "192.168.1.100"},
        )

    @pytest.mark.asyncio
    async def test_execute_playbook(
        self,
        playbook: DataExfiltrationPlaybook,
        mock_agent: MagicMock,
        mock_event: MockEvent,
    ) -> None:
        """Testa execução completa do playbook."""
        with (
            patch.object(
                playbook, "_detect_anomalous_transfer", new_callable=AsyncMock
            ) as mock_detect,
            patch.object(playbook, "_block_connection", new_callable=AsyncMock) as mock_block,
            patch.object(playbook, "_throttle_bandwidth", new_callable=AsyncMock) as mock_throttle,
            patch.object(playbook, "_preserve_logs", new_callable=AsyncMock) as mock_preserve,
            patch.object(playbook, "_notify_team", new_callable=AsyncMock) as mock_notify,
        ):

            # Configure mocks
            mock_detect.return_value = {"status": "success"}
            mock_block.return_value = {"status": "success"}
            mock_throttle.return_value = {"status": "success"}
            mock_preserve.return_value = {"path": "/tmp/test.json", "status": "saved"}
            mock_notify.return_value = {"status": "success"}

            # Execute
            result = await playbook.execute(mock_agent, mock_event)

            # Verify
            assert result["status"] == "completed"
            assert "detection" in result
            assert "blocked" in result
            assert "throttle" in result
            assert "preserved" in result
            assert "notification" in result

    @pytest.mark.asyncio
    async def test_detect_anomalous_transfer_available(
        self, playbook: DataExfiltrationPlaybook
    ) -> None:
        """Testa detecção de transferência anômala quando ss disponível."""
        with (
            patch(
                "src.security.playbooks.data_exfiltration_response.command_available",
                return_value=True,
            ),
            patch(
                "src.security.playbooks.data_exfiltration_response.run_command_async",
                new_callable=AsyncMock,
            ) as mock_run,
        ):

            mock_run.return_value = {"stdout": "test output", "success": True}

            result = await playbook._detect_anomalous_transfer()

            assert "stdout" in result or "success" in result
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_anomalous_transfer_unavailable(
        self, playbook: DataExfiltrationPlaybook
    ) -> None:
        """Testa detecção quando ss não disponível."""
        with (
            patch(
                "src.security.playbooks.data_exfiltration_response.command_available",
                return_value=False,
            ),
            patch(
                "src.security.playbooks.data_exfiltration_response.skipped_command"
            ) as mock_skipped,
        ):

            mock_skipped.return_value = {
                "status": "skipped",
                "reason": "tool unavailable",
            }

            result = await playbook._detect_anomalous_transfer()

            assert result["status"] == "skipped"
            mock_skipped.assert_called_once_with("ss", "tool unavailable")

    @pytest.mark.asyncio
    async def test_block_connection_with_remote_ip(
        self, playbook: DataExfiltrationPlaybook
    ) -> None:
        """Testa bloqueio de conexão com IP remoto."""
        mock_event = MockEvent(details={"remote": "10.0.0.1"})

        with (
            patch(
                "src.security.playbooks.data_exfiltration_response.command_available",
                return_value=True,
            ),
            patch(
                "src.security.playbooks.data_exfiltration_response.run_command_async",
                new_callable=AsyncMock,
            ) as mock_run,
        ):

            mock_run.return_value = {"success": True}

            result = await playbook._block_connection(mock_event)

            # Verify command was called with correct IP
            call_args = mock_run.call_args[0][0]
            assert "10.0.0.1" in call_args
            assert result is not None

    @pytest.mark.asyncio
    async def test_block_connection_no_remote_ip(self, playbook: DataExfiltrationPlaybook) -> None:
        """Testa bloqueio de conexão sem IP remoto."""
        mock_event = MockEvent(details={})

        with (
            patch(
                "src.security.playbooks.data_exfiltration_response.command_available",
                return_value=True,
            ),
            patch(
                "src.security.playbooks.data_exfiltration_response.run_command_async",
                new_callable=AsyncMock,
            ) as mock_run,
            patch(
                "src.security.playbooks.data_exfiltration_response.skipped_command"
            ) as mock_skipped,
        ):

            mock_run.return_value = {"success": True}
            mock_skipped.return_value = {
                "status": "skipped",
                "reason": "invalid remote",
            }

            result = await playbook._block_connection(mock_event)

            # Should skip when remote is 0.0.0.0 (default/invalid)
            assert result is not None
            # Either it was skipped or command was called
            if result.get("status") == "skipped":
                mock_skipped.assert_called_once()
            else:
                # If command was called, verify it was with valid arguments
                assert mock_run.called or mock_skipped.called

    @pytest.mark.asyncio
    async def test_throttle_bandwidth_available(self, playbook: DataExfiltrationPlaybook) -> None:
        """Testa throttling de bandwidth quando tc disponível."""
        with (
            patch(
                "src.security.playbooks.data_exfiltration_response.command_available",
                return_value=True,
            ),
            patch(
                "src.security.playbooks.data_exfiltration_response.run_command_async",
                new_callable=AsyncMock,
            ) as mock_run,
        ):

            mock_run.return_value = {"success": True}

            result = await playbook._throttle_bandwidth()

            # Verify tc command was called
            call_args = mock_run.call_args[0][0]
            assert "tc" in call_args
            assert result is not None

    @pytest.mark.asyncio
    async def test_throttle_bandwidth_unavailable(self, playbook: DataExfiltrationPlaybook) -> None:
        """Testa throttling quando tc não disponível."""
        with patch(
            "src.security.playbooks.data_exfiltration_response.command_available",
            return_value=False,
        ):

            result = await playbook._throttle_bandwidth()

            assert result["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_preserve_logs(
        self, playbook: DataExfiltrationPlaybook, mock_event: MockEvent
    ) -> None:
        """Testa preservação de logs forenses."""
        with patch.object(playbook, "_write_artifact") as mock_write:

            result = await playbook._preserve_logs(mock_event)

            assert "path" in result
            assert "status" in result
            assert result["status"] == "saved"
            assert "/tmp/exfil_" in result["path"]

            # Verify write_artifact was called
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_team(
        self, playbook: DataExfiltrationPlaybook, mock_event: MockEvent
    ) -> None:
        """Testa notificação da equipe."""
        with patch(
            "src.security.playbooks.data_exfiltration_response.run_command_async",
            new_callable=AsyncMock,
        ) as mock_run:

            mock_run.return_value = {"success": True}

            result = await playbook._notify_team(mock_event)

            # Verify echo command was called
            call_args = mock_run.call_args[0][0]
            assert "/bin/echo" in call_args
            assert result is not None

    def test_write_artifact(self, playbook: DataExfiltrationPlaybook, tmp_path: Any) -> None:
        """Testa escrita de artefato forense."""
        import json

        test_file = tmp_path / "test_artifact.json"
        test_payload = {"event": "test", "logs": ["/var/log/test.log"]}

        playbook._write_artifact(str(test_file), test_payload)

        # Verify file was created
        assert test_file.exists()

        # Verify content
        with open(test_file, "r", encoding="utf-8") as f:
            content = json.load(f)
            assert content["event"] == "test"
            assert "/var/log/test.log" in content["logs"]

    @pytest.mark.asyncio
    async def test_execute_handles_exceptions(
        self,
        playbook: DataExfiltrationPlaybook,
        mock_agent: MagicMock,
        mock_event: MockEvent,
    ) -> None:
        """Testa que execute lida com exceções gracefully."""
        with patch.object(
            playbook, "_detect_anomalous_transfer", new_callable=AsyncMock
        ) as mock_detect:

            # Simulate exception
            mock_detect.side_effect = Exception("Test exception")

            # Should raise the exception
            with pytest.raises(Exception, match="Test exception"):
                await playbook.execute(mock_agent, mock_event)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
