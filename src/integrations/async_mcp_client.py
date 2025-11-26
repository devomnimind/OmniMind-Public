from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, cast
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    pass


class AsyncMCPClient:
    """Asynchronous client for MCP server using httpx."""

    def __init__(self, endpoint: str = "http://127.0.0.1:4321/mcp", timeout: float = 15.0) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, params: Dict[str, Any]) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": uuid4().hex,
        }
        logger.debug("AsyncMCPClient request %s %s", method, params)
        try:
            response = await self._client.post(self.endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise MCPClientError(
                f"MCP client HTTP error: {exc.response.status_code} {exc.response.reason_phrase}"
            ) from exc
        except httpx.RequestError as exc:
            raise MCPClientError(f"MCP client connection error: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise MCPClientError("Invalid JSON response from MCP server") from exc

        if "error" in data:
            err = data["error"]
            raise MCPClientError(err.get("message", "MCP error"))

        logger.debug("AsyncMCPClient response %s", data.get("result"))
        return data.get("result")

    async def read_file(self, path: str, encoding: str = "utf-8") -> str:
        return cast(
            str,
            await self._request(
                "read_file",
                {"path": path, "encoding": encoding},
            ),
        )

    async def write_file(self, path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            await self._request(
                "write_file",
                {"path": path, "content": content, "encoding": encoding},
            ),
        )

    async def list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            await self._request(
                "list_dir",
                {"path": path, "recursive": recursive},
            ),
        )

    async def stat(self, path: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            await self._request(
                "stat",
                {"path": path},
            ),
        )

    async def get_metrics(self) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            await self._request(
                "get_metrics",
                {},
            ),
        )

    async def read_env(self, keys: list[str]) -> Dict[str, str]:
        """Read environment variables via MCP."""
        # Assuming MCP server has a read_env method, if not, this will fail gracefully via _request
        return cast(
            Dict[str, str],
            await self._request(
                "read_env",
                {"keys": keys},
            ),
        )
