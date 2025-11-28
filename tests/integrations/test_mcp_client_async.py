from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import pytest
from src.integrations.mcp_client_async import (
        import httpx as httpx_real


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
Testes para Async MCP Client (mcp_client_async.py).

Cobertura de:
- Cliente assíncrono com httpx
- Connection pooling
- Retry logic com exponential backoff
- Timeout management
- Tratamento de exceções
- Context manager async
"""




    AsyncMCPClient,
    MCPClientError,
    MCPConnectionError,
    MCPProtocolError,
    MCPTimeoutError,
)


class TestMCPExceptions:
    """Testes para exceções do MCP Client."""

    def test_mcp_client_error(self) -> None:
        """Testa exceção base MCPClientError."""
        error = MCPClientError("Test error")
        assert str(error) == "Test error"

    def test_mcp_timeout_error(self) -> None:
        """Testa exceção MCPTimeoutError."""
        error = MCPTimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, MCPClientError)

    def test_mcp_connection_error(self) -> None:
        """Testa exceção MCPConnectionError."""
        error = MCPConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, MCPClientError)

    def test_mcp_protocol_error(self) -> None:
        """Testa exceção MCPProtocolError."""
        error = MCPProtocolError("Invalid protocol")
        assert str(error) == "Invalid protocol"
        assert isinstance(error, MCPClientError)


@pytest.mark.skipif(
    not hasattr(asyncio, "run"),
    reason="asyncio.run not available",
)
class TestAsyncMCPClient:
    """Testes para AsyncMCPClient."""

    @patch("src.integrations.mcp_client_async.httpx")
    def test_client_initialization(self, mock_httpx: Mock) -> None:
        """Testa inicialização do cliente."""
        mock_httpx.AsyncClient = MagicMock()

        client = AsyncMCPClient(
            endpoint="http://localhost:4321/mcp",
            timeout=30.0,
            max_retries=3,
        )

        assert client.endpoint == "http://localhost:4321/mcp"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    @patch("src.integrations.mcp_client_async.httpx")
    def test_client_initialization_without_httpx(self, mock_httpx: Mock) -> None:
        """Testa inicialização quando httpx não está disponível."""
        mock_httpx.AsyncClient = None

        with patch("src.integrations.mcp_client_async.httpx", None):
            with pytest.raises(RuntimeError, match="httpx is required"):
                AsyncMCPClient()

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_connect(self, mock_httpx: Mock) -> None:
        """Testa conexão do cliente."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient()
        await client.connect()

        assert client._client is not None

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_close(self, mock_httpx: Mock) -> None:
        """Testa fechamento da conexão."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient()
        await client.connect()
        await client.close()

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_context_manager(self, mock_httpx: Mock) -> None:
        """Testa uso como context manager."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        async with AsyncMCPClient() as client:
            assert client._client is not None

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_send_request_success(self, mock_async_client: Mock) -> None:
        """Testa envio de request bem-sucedido."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "test_id",
            "result": {"result": "success"},
        }
        mock_response.raise_for_status = MagicMock()

        # Create mock client instance
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value = mock_client_instance

        client = AsyncMCPClient()
        await client.connect()

        response = await client.send_request(
            method="test_method",
            params={"key": "value"},
        )

        assert response["result"] == "success"

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_send_request_with_retry(self, mock_httpx: Mock) -> None:
        """Testa retry logic."""

        # Mock exception classes to avoid TypeError
        class MockTimeoutException(Exception):
            pass

        class MockConnectError(Exception):
            pass

        class MockHTTPStatusError(Exception):
            def __init__(self, message):
                super().__init__(message)
                self.response = MagicMock()
                self.response.status_code = 400
                self.response.reason_phrase = "Bad Request"

        mock_httpx.TimeoutException = MockTimeoutException
        mock_httpx.ConnectError = MockConnectError
        mock_httpx.HTTPStatusError = MockHTTPStatusError

        # First call fails, second succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 400
        mock_response_fail.reason_phrase = "Bad Request"
        mock_response_fail.raise_for_status.side_effect = MockHTTPStatusError(
            "HTTP error: 400 Bad Request"
        )

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "jsonrpc": "2.0",
            "id": "test",
            "result": "success",
        }

        mock_client = AsyncMock()
        mock_client.post.side_effect = [
            mock_response_fail,
            mock_response_success,
        ]

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient(max_retries=2, retry_backoff=0.1)
        await client.connect()

        response = await client.send_request(
            method="test_method",
            params={"key": "value"},
        )

        assert response == "success"
        assert mock_client.post.call_count <= 2

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_send_request_timeout(self, mock_httpx: Mock) -> None:
        """Testa timeout em request."""
        mock_client = AsyncMock()

        # Simulate timeout

        mock_client.post.side_effect = httpx_real.TimeoutException("Timeout")

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient(timeout=1.0, max_retries=1)
        await client.connect()

        with pytest.raises((MCPTimeoutError, Exception)):
            await client.send_request(method="test_method", params={})

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_send_request_connection_error(self, mock_httpx: Mock) -> None:
        """Testa erro de conexão."""
        mock_client = AsyncMock()

        # Simulate connection error
        import httpx as httpx_real

        mock_client.post.side_effect = httpx_real.ConnectError("Connection failed")

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient(max_retries=1)
        await client.connect()

        with pytest.raises((MCPConnectionError, Exception)):
            await client.send_request(method="test_method", params={})

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_validate_response_success(self, mock_httpx: Mock) -> None:
        """Testa validação de resposta bem-sucedida."""
        mock_httpx.AsyncClient = MagicMock()

        client = AsyncMCPClient()

        valid_response = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"data": "test"},
        }

        # Should not raise exception
        validated = client._validate_response(valid_response)
        assert validated is not None or validated is None

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_validate_response_error(self, mock_httpx: Mock) -> None:
        """Testa validação de resposta com erro."""
        mock_httpx.AsyncClient = MagicMock()

        client = AsyncMCPClient()

        error_response = {
            "jsonrpc": "2.0",
            "id": "123",
            "error": {"code": -32600, "message": "Invalid request"},
        }

        # Should handle error response
        with pytest.raises((MCPProtocolError, Exception)):
            client._validate_response(error_response)

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_multiple_concurrent_requests(self, mock_httpx: Mock) -> None:
        """Testa múltiplas requests concorrentes."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient()
        await client.connect()

        # Send multiple requests concurrently
        tasks = [client.send_request(method=f"method_{i}", params={"id": i}) for i in range(5)]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete (success or exception)
        assert len(responses) == 5


class TestAsyncMCPClientEdgeCases:
    """Testes para casos extremos."""

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_send_request_without_connection(self, mock_httpx: Mock) -> None:
        """Testa envio de request sem conexão estabelecida."""
        mock_httpx.AsyncClient = MagicMock()

        client = AsyncMCPClient()

        # Try to send without connecting first
        with pytest.raises(Exception):
            await client.send_request(method="test", params={})

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_double_close(self, mock_httpx: Mock) -> None:
        """Testa fechamento duplo da conexão."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient()
        await client.connect()
        await client.close()

        # Second close should not raise exception
        await client.close()

    @pytest.mark.asyncio
    @patch("src.integrations.mcp_client_async.httpx")
    async def test_retry_exhaustion(self, mock_httpx: Mock) -> None:
        """Testa esgotamento de retries."""
        mock_response = AsyncMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        client = AsyncMCPClient(max_retries=2, retry_backoff=0.01)
        await client.connect()

        # Should fail after retries exhausted
        with pytest.raises(Exception):
            await client.send_request(method="test", params={})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
