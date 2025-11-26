from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, cast

from src.audit.immutable_audit import get_audit_system


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MCPConfig:
    host: str = "127.0.0.1"
    port: int = 4321
    allowed_paths: List[str] = field(default_factory=lambda: ["."])
    max_read_size: int = 2 * 1024 * 1024
    allowed_extensions: List[str] = field(
        default_factory=lambda: ["py", "md", "json", "yaml", "yml", "txt", "sh"]
    )
    audit_category: str = "mcp"

    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None) -> "MCPConfig":
        default = cls()
        if path is None:
            path = Path(__file__).resolve().parents[2] / "config" / "mcp.json"
        config_path = Path(path).expanduser()

        # Ler porta e host de variáveis de ambiente (prioridade sobre arquivo)
        env_port = os.environ.get("MCP_PORT")
        env_host = os.environ.get("MCP_HOST", "127.0.0.1")  # Sempre localhost por padrão

        if not config_path.exists():
            # Usar valores de ambiente ou defaults
            port = int(env_port) if env_port else default.port
            return cls(
                host=env_host,
                port=port,
                allowed_paths=default.allowed_paths,
                max_read_size=default.max_read_size,
                allowed_extensions=default.allowed_extensions,
                audit_category=default.audit_category,
            )
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - best effort config
            logger.warning("Failed to read MCP config %s: %s", config_path, exc)
            port = int(env_port) if env_port else default.port
            return cls(
                host=env_host,
                port=port,
                allowed_paths=default.allowed_paths,
                max_read_size=default.max_read_size,
                allowed_extensions=default.allowed_extensions,
                audit_category=default.audit_category,
            )

        # Variáveis de ambiente têm prioridade sobre arquivo de configuração
        port = int(env_port) if env_port else payload.get("port", default.port)
        host = env_host if env_host != "127.0.0.1" else payload.get("host", env_host)

        # Garantir que host seja sempre localhost para segurança
        if host != "127.0.0.1" and host != "localhost":
            logger.warning("Host não é localhost, forçando 127.0.0.1 por segurança")
            host = "127.0.0.1"

        return cls(
            host=host,
            port=port,
            allowed_paths=payload.get("allowed_paths", default.allowed_paths),
            max_read_size=payload.get("max_read_size", default.max_read_size),
            allowed_extensions=payload.get("allowed_extensions", default.allowed_extensions),
            audit_category=payload.get("audit_category", default.audit_category),
        )


class MCPRequestError(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.data = data


class MCPServer:
    def __init__(
        self,
        config: Optional[MCPConfig] = None,
        allowed_roots: Optional[Iterable[str]] = None,
    ) -> None:
        self.config = config or MCPConfig.load()
        self.project_root = Path(__file__).resolve().parents[2]
        base_roots = allowed_roots or self.config.allowed_paths
        self.allowed_roots = self._normalize_roots(base_roots)
        self.audit_system = get_audit_system()
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "methods": {},
        }
        self._server: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._methods: Dict[str, Callable[..., Any]] = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_dir": self.list_dir,
            "stat": self.stat,
            "get_metrics": self.get_metrics,
        }

    def _normalize_roots(self, paths: Iterable[str]) -> List[Path]:
        normalized = []
        for raw in paths:
            candidate = Path(raw).expanduser()
            if not candidate.is_absolute():
                candidate = self.project_root / candidate
            normalized.append(candidate.resolve())
        return sorted(set(normalized))

    def start(self, daemon: bool = True) -> None:
        if self._server:
            raise RuntimeError("MCPServer already running")
        handler = self._make_handler()
        server = ThreadingHTTPServer((self.config.host, self.config.port), handler)
        self._server = server
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=daemon,
            name="MCPServerThread",
        )
        thread.start()
        self._thread = thread
        self.config = MCPConfig(
            host=server.server_address[0],  # type: ignore[arg-type]
            port=server.server_address[1],
            allowed_paths=self.config.allowed_paths,
            max_read_size=self.config.max_read_size,
            allowed_extensions=self.config.allowed_extensions,
            audit_category=self.config.audit_category,
        )
        logger.info("MCPServer listening on %s:%s", *server.server_address)

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._server = None
        self._thread = None

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        parent = self

        class MCPRequestHandler(BaseHTTPRequestHandler):
            server_version = "OmniMindMCP/1.0"

            def do_POST(self) -> None:
                if self.path != "/mcp":
                    self.send_error(404, "Only /mcp endpoint is supported")
                    return
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                try:
                    response = parent.handle_rpc(raw)
                except Exception as exc:
                    response = parent._error_response(None, -32000, str(exc))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(response.encode("utf-8"))

            def log_message(self, fmt: str, *args: Any) -> None:
                return

        return MCPRequestHandler

    def handle_rpc(self, payload: Union[str, bytes]) -> str:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        try:
            request = json.loads(payload)
        except json.JSONDecodeError:
            return self._error_response(None, -32700, "Invalid JSON payload")

        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        if method not in self._methods:
            return self._error_response(request_id, -32601, f"Unknown method {method}")
        start = perf_counter()
        try:
            result = self._dispatch(method, params)
            duration = perf_counter() - start
            self._record_metrics(method, duration)
            self._audit(method, params, result, "SUCCESS")
            return self._success_response(request_id, result)
        except MCPRequestError as exc:
            duration = perf_counter() - start
            self._record_metrics(method, duration)
            self._audit(method, params, exc, "FAILED")
            return self._error_response(request_id, exc.code, str(exc), exc.data)
        except Exception as exc:  # pragma: no cover
            duration = perf_counter() - start
            self._record_metrics(method, duration)
            self._audit(method, params, exc, "ERROR")
            return self._error_response(request_id, -32603, "Internal error")

    def _dispatch(self, method: str, params: Any) -> Any:
        callable_method = self._methods[method]
        if isinstance(params, dict):
            return callable_method(**params)
        if isinstance(params, list):
            return callable_method(*params)
        raise MCPRequestError(-32602, "Params must be dict or list", params)

    def _record_metrics(self, method: str, duration: float) -> None:
        self.metrics["total_requests"] += 1
        method_stats = self.metrics["methods"].setdefault(
            method, {"calls": 0, "avg_latency": 0.0, "last_latency": 0.0}
        )
        method_stats["calls"] += 1
        method_stats["last_latency"] = duration
        method_stats["avg_latency"] = (
            (method_stats["avg_latency"] * (method_stats["calls"] - 1)) + duration
        ) / method_stats["calls"]

    def _audit(self, method: str, params: Any, result: Any, status: str) -> str:
        details = {
            "method": method,
            "params": params,
            "result": result if not isinstance(result, Exception) else None,
            "status": status,
        }
        if isinstance(result, Exception):
            details["error"] = str(result)
        return self.audit_system.log_action(method, details, category=self.config.audit_category)

    def _success_response(self, request_id: Optional[Any], result: Any) -> str:
        return json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result})

    def _error_response(
        self,
        request_id: Optional[Any],
        code: int,
        message: str,
        data: Optional[Any] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
        if data is not None:
            cast(Dict[str, Any], payload["error"])["data"] = data
        return json.dumps(payload)

    def _resolve_path(self, path: str) -> Path:
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            candidate = self.project_root / candidate
        resolved = candidate.resolve()
        for root in self.allowed_roots:
            if root == resolved or root in resolved.parents:
                return resolved
        raise MCPRequestError(
            -32602,
            "Path outside allowed roots",
            {"resolved": str(resolved), "roots": [str(r) for r in self.allowed_roots]},
        )

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        resolved = self._resolve_path(path)
        if not resolved.is_file():
            raise MCPRequestError(-32602, f"File does not exist: {resolved}")
        if self.config.max_read_size and resolved.stat().st_size > self.config.max_read_size:
            raise MCPRequestError(-32602, "File exceeds maximum read size")
        return resolved.read_text(encoding=encoding)

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        resolved = self._resolve_path(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        if self.config.allowed_extensions:
            candidate_ext = resolved.suffix.lstrip(".").lower()
            if candidate_ext and candidate_ext not in self.config.allowed_extensions:
                raise MCPRequestError(
                    -32602,
                    f"Extension not allowed: {candidate_ext}",
                    {"allowed": self.config.allowed_extensions},
                )
        resolved.write_text(content, encoding=encoding)
        content_hash = self.audit_system.hash_content(resolved.read_bytes())
        try:
            self.audit_system.set_file_xattr(str(resolved), content_hash)
        except Exception:
            logger.debug("Failed to set xattr for %s", resolved)
        return {
            "path": str(resolved),
            "size": len(content.encode(encoding)),
            "hash": content_hash,
        }

    def list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            raise MCPRequestError(-32602, f"Path does not exist: {resolved}")
        entries = []
        if recursive:
            for child in resolved.rglob("*"):
                entries.append(self._entry_summary(child))
        else:
            for child in resolved.iterdir():
                entries.append(self._entry_summary(child))
        return {"path": str(resolved), "entries": entries}

    def stat(self, path: str) -> Dict[str, Any]:
        resolved = self._resolve_path(path)
        stats = resolved.stat()
        return {
            "path": str(resolved),
            "is_file": resolved.is_file(),
            "is_dir": resolved.is_dir(),
            "size": stats.st_size,
            "modified": stats.st_mtime,
        }

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "server": f"{self.config.host}:{self.config.port}",
            "allowed_roots": [str(r) for r in self.allowed_roots],
            "metrics": self.metrics,
        }

    def _entry_summary(self, child: Path) -> Dict[str, Any]:
        return {
            "path": str(child),
            "name": child.name,
            "type": "dir" if child.is_dir() else "file",
            "size": child.stat().st_size if child.is_file() else 0,
        }

    @property
    def url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}/mcp"


if __name__ == "__main__":
    server = MCPServer()
    try:
        server.start()
        logger.info("Press Ctrl+C to stop MCPServer")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
