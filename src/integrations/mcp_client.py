from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, cast
from uuid import uuid4

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    pass


class MCPClient:
    def __init__(self, endpoint: str = "http://127.0.0.1:4321/mcp", timeout: float = 15.0) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._headers = {"Content-Type": "application/json"}

    def _request(self, method: str, params: Dict[str, Any]) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": uuid4().hex,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers=self._headers,
            method="POST",
        )
        logger.debug("MCPClient request %s %s", method, params)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise MCPClientError(f"MCP client HTTP error: {exc.code} {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise MCPClientError(f"MCP client connection error: {exc}") from exc
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise MCPClientError("Invalid JSON response from MCP server") from exc
        if "error" in payload:
            err = payload["error"]
            raise MCPClientError(err.get("message", "MCP error"))
        logger.debug("MCPClient response %s", payload.get("result"))
        return payload.get("result")

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        return cast(
            str,
            self._request(
                "read_file",
                {"path": path, "encoding": encoding},
            ),
        )

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._request(
                "write_file",
                {"path": path, "content": content, "encoding": encoding},
            ),
        )

    def list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._request(
                "list_dir",
                {"path": path, "recursive": recursive},
            ),
        )

    def stat(self, path: str) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._request(
                "stat",
                {"path": path},
            ),
        )

    def get_metrics(self) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._request(
                "get_metrics",
                {},
            ),
        )
