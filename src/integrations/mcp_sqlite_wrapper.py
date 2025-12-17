"""
MCP SQLite Wrapper - Wrapper Python para mcp-server-sqlite via uvx.

Este módulo cria um servidor HTTP que faz a ponte entre o protocolo HTTP usado
pelo OmniMind e o protocolo stdio usado pelo mcp-server-sqlite via uvx.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from src.audit.immutable_audit import get_audit_system
from src.integrations.mcp_cache import get_mcp_cache

logger = logging.getLogger(__name__)


@dataclass
class MCPSQLiteConfig:
    """Configuração do wrapper sqlite MCP."""

    host: str = "127.0.0.1"
    port: int = 4329
    db_path: str = "data/omnimind_cache.db"
    audit_category: str = "sqlite_mcp"


class MCPStdioBridge:
    """Bridge entre HTTP e stdio para comunicação com MCPs externos."""

    def __init__(
        self,
        command: list[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Inicializa o bridge stdio.

        Args:
            command: Comando completo para executar o MCP.
            cwd: Diretório de trabalho para o processo.
            env: Variáveis de ambiente customizadas. Se None, usa os.environ.copy().
        """
        self.command = command
        self.cwd = cwd or Path.cwd()
        self.process: Optional[subprocess.Popen[str]] = None
        self._lock = threading.Lock()
        self.custom_env = env

    def start(self) -> None:
        """Inicia o processo MCP."""
        if self.process is not None:
            raise RuntimeError("Process already started")

        if self.custom_env is not None:
            env = self.custom_env.copy()
        else:
            env = os.environ.copy()

        env.pop("DISPLAY", None)
        env.pop("WAYLAND_DISPLAY", None)
        env["MCP_PORT"] = str(os.environ.get("MCP_PORT", "4329"))

        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.cwd,
            env=env,
            start_new_session=True,
        )

        logger.info("MCP stdio bridge iniciado: %s", " ".join(self.command))

    def stop(self) -> None:
        """Para o processo MCP."""
        if self.process is None:
            return

        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=2)
        finally:
            self.process = None

    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia uma requisição JSON-RPC via stdio e retorna a resposta.

        Args:
            method: Nome do método MCP.
            params: Parâmetros do método.

        Returns:
            Resposta JSON-RPC.
        """
        if self.process is None:
            raise RuntimeError("Process not started")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }

        with self._lock:
            try:
                # Enviar requisição
                request_json = json.dumps(request) + "\n"
                if self.process.stdin:
                    self.process.stdin.write(request_json)
                    self.process.stdin.flush()

                # Ler resposta
                if self.process.stdout:
                    response_line = self.process.stdout.readline()
                    response = json.loads(response_line)

                    if "error" in response:
                        raise RuntimeError(
                            f"MCP error: {response['error'].get('message', 'Unknown error')}"
                        )

                    return response.get("result", {})
            except Exception as e:
                logger.error("Erro na comunicação stdio: %s", e)
                raise

        # This should never be reached, but added for type checker
        raise RuntimeError("Unexpected code path in send_request")


class MCPSQLiteWrapper:
    """Wrapper HTTP para mcp-server-sqlite."""

    def __init__(self, config: Optional[MCPSQLiteConfig] = None) -> None:
        """
        Inicializa o wrapper sqlite MCP.

        Args:
            config: Configuração do wrapper. Se None, usa valores de ambiente ou defaults.
        """
        if config is None:
            port = int(os.environ.get("MCP_PORT", "4329"))
            db_path = os.environ.get("MCP_SQLITE_DB_PATH", "data/omnimind_cache.db")
            config = MCPSQLiteConfig(
                host="127.0.0.1",
                port=port,
                db_path=db_path,
                audit_category="sqlite_mcp",
            )

        self.config = config
        self.audit_system = get_audit_system()
        self.cache = get_mcp_cache()
        self.project_root = Path(__file__).resolve().parents[2]

        # Resolver caminho do banco de dados
        db_path_obj = Path(config.db_path).expanduser()
        if not db_path_obj.is_absolute():
            db_path_obj = self.project_root / db_path_obj
        db_path_obj = db_path_obj.resolve()
        self.db_path = str(db_path_obj)

        # Garantir que o diretório existe
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Inicializar bridge stdio
        uvx_path = os.environ.get("UVX_PATH", "/home/fahbrain/.local/bin/uvx")
        if not os.path.exists(uvx_path):
            uvx_path = shutil.which("uvx") or "uvx"

        command = [
            uvx_path,
            "mcp-server-sqlite",
            "--db-path",
            str(self.db_path),
        ]
        env_clean = os.environ.copy()
        env_clean.pop("DISPLAY", None)

        # Configurar PATH para usar o ambiente virtual correto
        venv_python = self.project_root / ".venv" / "bin" / "python"
        env_clean["PATH"] = f"{str(venv_python.parent)}:{env_clean.get('PATH', '')}"

        self.bridge = MCPStdioBridge(command, cwd=self.project_root, env=env_clean)

        self._server: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, daemon: bool = True) -> None:
        """Inicia o servidor HTTP e o bridge stdio."""
        if self._server is not None:
            raise RuntimeError("Server already running")

        # Iniciar bridge stdio
        self.bridge.start()

        # Criar servidor HTTP
        handler = self._make_handler()
        server = ThreadingHTTPServer((self.config.host, self.config.port), handler)
        self._server = server

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=daemon,
            name="MCPSQLiteWrapperThread",
        )
        thread.start()
        self._thread = thread

        logger.info("MCP SQLite Wrapper listening on %s:%s", self.config.host, self.config.port)

    def stop(self) -> None:
        """Para o servidor HTTP e o bridge stdio."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2)
            self._server = None
            self._thread = None

        self.bridge.stop()

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        """Cria o handler HTTP."""
        parent = self

        class MCPSQLiteHandler(BaseHTTPRequestHandler):
            server_version = "OmniMindMCPSQLite/1.0"

            def do_POST(self) -> None:
                if self.path != "/mcp":
                    self.send_error(404, "Only /mcp endpoint is supported")
                    return

                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)

                try:
                    request = json.loads(raw.decode("utf-8"))
                    method = request.get("method")
                    params = request.get("params", {})

                    # Check cache first
                    cache_key = f"sql_{method}_{hash(str(params)) % 10000}"
                    try:
                        if hasattr(parent.cache, "_get_sync"):
                            cached = parent.cache._get_sync(cache_key)
                            if cached:
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": request.get("id"),
                                    "result": cached,
                                }
                                self.send_response(200)
                                self.send_header("Content-type", "application/json")
                                self.end_headers()
                                self.wfile.write(json.dumps(response).encode("utf-8"))
                                return
                    except Exception:
                        pass

                    # Enviar para o MCP via stdio
                    result = parent.bridge.send_request(method, params)

                    # Cache result
                    try:
                        if hasattr(parent.cache, "_put_sync"):
                            parent.cache._put_sync(cache_key, result)
                    except Exception:
                        pass

                    # Auditoria
                    parent.audit_system.log_action(
                        action=method,
                        details={"params": params, "result": result},
                        category=parent.config.audit_category,
                    )

                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": result,
                    }
                except Exception as exc:
                    logger.error("Erro ao processar requisição: %s", exc)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if "request" in locals() else None,
                        "error": {"code": -32000, "message": str(exc)},
                    }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            def log_message(self, fmt: str, *args: Any) -> None:
                return

        return MCPSQLiteHandler


if __name__ == "__main__":
    import signal
    import sys

    wrapper = MCPSQLiteWrapper()
    wrapper.start(daemon=False)

    def signal_handler(sig: int, frame: Any) -> None:
        logger.info("Recebido sinal de parada, encerrando...")
        wrapper.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("MCP SQLite Wrapper rodando. Pressione Ctrl+C para parar.")
    if wrapper._thread:
        wrapper._thread.join()
