"""Async MCP client with enhanced reliability and performance.

This module provides an enhanced Model Context Protocol client with:
- Async httpx for better performance
- Connection pooling for efficiency
- Automatic retries with exponential backoff
- Better error handling and timeout management
- Protocol validation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional
from uuid import uuid4

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """Base exception for MCP client errors."""

    pass


class MCPTimeoutError(MCPClientError):
    """Raised when MCP request times out."""

    pass


class MCPConnectionError(MCPClientError):
    """Raised when connection to MCP server fails."""

    pass


class MCPProtocolError(MCPClientError):
    """Raised when protocol validation fails."""

    pass


class AsyncMCPClient:
    """Enhanced async MCP client with retry logic and connection pooling."""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:4321/mcp",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ) -> None:
        """Initialize async MCP client.

        Args:
            endpoint: MCP server endpoint URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff: Initial backoff time for retries (doubles each retry)
        """
        if httpx is None:
            raise RuntimeError(
                "httpx is required for AsyncMCPClient. "
                "Install with: pip install httpx"
            )

        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._client: Optional[httpx.AsyncClient] = None
        self._headers = {"Content-Type": "application/json"}

    async def __aenter__(self) -> "AsyncMCPClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Establish connection pool."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                ),
            )
            logger.info(f"AsyncMCPClient connected to {self.endpoint}")

    async def close(self) -> None:
        """Close connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("AsyncMCPClient connection closed")

    def _validate_response(self, payload: Dict[str, Any]) -> None:
        """Validate JSON-RPC response format.

        Args:
            payload: Response payload to validate

        Raises:
            MCPProtocolError: If response format is invalid
        """
        if "jsonrpc" not in payload:
            raise MCPProtocolError("Response missing 'jsonrpc' field")

        if payload["jsonrpc"] != "2.0":
            raise MCPProtocolError(f"Invalid JSON-RPC version: {payload['jsonrpc']}")

        if "id" not in payload:
            raise MCPProtocolError("Response missing 'id' field")

        if "error" in payload:
            error = payload["error"]
            error_msg = error.get("message", "Unknown MCP error")
            error_code = error.get("code", -1)
            raise MCPClientError(f"MCP error ({error_code}): {error_msg}")

        if "result" not in payload:
            raise MCPProtocolError("Response missing 'result' field")

    async def _request_with_retry(self, method: str, params: Dict[str, Any]) -> Any:
        """Make MCP request with automatic retries.

        Args:
            method: MCP method name
            params: Method parameters

        Returns:
            Result from MCP server

        Raises:
            MCPClientError: If request fails after all retries
        """
        if self._client is None:
            await self.connect()

        request_id = uuid4().hex
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id,
        }

        last_exception: MCPTimeoutError | MCPConnectionError | MCPClientError | None = (
            None
        )
        backoff = self.retry_backoff

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"MCP request {method} (attempt {attempt + 1}/{self.max_retries})"
                )

                response = await self._client.post(  # type: ignore
                    self.endpoint, json=payload, headers=self._headers
                )

                # Check HTTP status
                if response.status_code >= 500:
                    raise MCPConnectionError(
                        f"Server error: {response.status_code} {response.reason_phrase}"
                    )

                response.raise_for_status()

                # Parse and validate response
                response_payload = response.json()
                self._validate_response(response_payload)

                logger.debug(f"MCP request {method} succeeded")
                return response_payload["result"]

            except httpx.TimeoutException as exc:
                last_exception = MCPTimeoutError(
                    f"Request timed out after {self.timeout}s: {exc}"
                )
                logger.warning(f"MCP timeout (attempt {attempt + 1}): {exc}")

            except httpx.ConnectError as exc:
                last_exception = MCPConnectionError(f"Connection failed: {exc}")
                logger.warning(f"MCP connection error (attempt {attempt + 1}): {exc}")

            except httpx.HTTPStatusError as exc:
                last_exception = MCPClientError(
                    f"HTTP error: {exc.response.status_code} {exc.response.reason_phrase}"
                )
                logger.warning(f"MCP HTTP error (attempt {attempt + 1}): {exc}")

            except (MCPProtocolError, MCPClientError) as exc:
                # Don't retry protocol errors
                logger.error(f"MCP protocol error: {exc}")
                raise

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                await asyncio.sleep(backoff)
                backoff *= 2

        # All retries exhausted
        if last_exception:
            raise last_exception
        raise MCPClientError(f"Request failed after {self.max_retries} retries")

    async def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Read file contents from MCP server.

        Args:
            path: File path to read
            encoding: File encoding (default: utf-8)

        Returns:
            File contents as string

        Raises:
            MCPClientError: If read fails
        """
        result = await self._request_with_retry(
            "read_file", {"path": path, "encoding": encoding}
        )
        return str(result)

    async def write_file(
        self, path: str, content: str, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Write file contents to MCP server.

        Args:
            path: File path to write
            content: Content to write
            encoding: File encoding (default: utf-8)

        Returns:
            Write operation result

        Raises:
            MCPClientError: If write fails
        """
        result = await self._request_with_retry(
            "write_file", {"path": path, "content": content, "encoding": encoding}
        )
        return dict(result)

    async def list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """List directory contents from MCP server.

        Args:
            path: Directory path to list
            recursive: Whether to list recursively

        Returns:
            Directory listing

        Raises:
            MCPClientError: If list fails
        """
        result = await self._request_with_retry(
            "list_dir", {"path": path, "recursive": recursive}
        )
        return dict(result)

    async def stat(self, path: str) -> Dict[str, Any]:
        """Get file/directory statistics from MCP server.

        Args:
            path: Path to stat

        Returns:
            File statistics

        Raises:
            MCPClientError: If stat fails
        """
        result = await self._request_with_retry("stat", {"path": path})
        return dict(result)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get MCP server metrics.

        Returns:
            Server metrics

        Raises:
            MCPClientError: If metrics request fails
        """
        result = await self._request_with_retry("get_metrics", {})
        return dict(result)

    async def health_check(self) -> bool:
        """Check MCP server health.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            await self.get_metrics()
            return True
        except Exception as exc:
            logger.warning(f"MCP health check failed: {exc}")
            return False
