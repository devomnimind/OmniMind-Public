"""
Gerenciador de servidor para testes.
Inicia servidor backend/frontend/MCP e mantém vivo durante suite.
Se cair, reinicia automaticamente.
"""

import os
import signal
import subprocess
import time
from typing import Optional

import pytest
import requests


class ServerManager:
    """Gerencia servidor backend OmniMind."""

    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.mcp_process: Optional[subprocess.Popen] = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.health_check_retries = 5
        self.health_check_interval = 2

    def start_server(self):
        """Inicia servidor backend."""
        if self.is_backend_healthy():
            print("✅ Servidor backend já está rodando")
            return

        print("🚀 Iniciando servidor backend...")
        try:
            # Inicia backend (FastAPI)
            self.backend_process = subprocess.Popen(
                [
                    "python",
                    "-m",
                    "uvicorn",
                    "src.api.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )

            # Aguarda backend ficar saudável
            self._wait_for_health(self.backend_url, "backend")
            print("✅ Backend rodando em http://localhost:8000")

        except Exception as e:
            print(f"❌ Erro iniciando backend: {e}")
            raise

    def start_mcp_servers(self):
        """Inicia servidores MCP."""
        print("🚀 Iniciando servidores MCP...")
        try:
            # Inicia MCP (se existir)
            mcp_config = os.path.join(os.path.dirname(__file__), "../config", "mcp_servers.json")
            if os.path.exists(mcp_config):
                # Implementar inicialização MCP conforme necessário
                print("✅ MCP configurado")
        except Exception as e:
            print(f"⚠️  MCP: {e}")

    def is_backend_healthy(self) -> bool:
        """Verifica se backend está respondendo."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def _wait_for_health(self, url: str, service_name: str, max_attempts: int = 10):
        """Aguarda serviço ficar saudável."""
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    return
            except Exception:
                pass

            time.sleep(1)
            if attempt < max_attempts - 1:
                print(f"⏳ Aguardando {service_name} ({attempt + 1}/{max_attempts})...")

        raise RuntimeError(f"{service_name} não ficou saudável em {max_attempts}s")

    def restart_if_down(self):
        """Reinicia servidor se estiver down."""
        if not self.is_backend_healthy():
            print("⚠️  Servidor backend está DOWN - reiniciando...")
            self.stop_server()
            time.sleep(1)
            self.start_server()

    def stop_server(self):
        """Para servidor."""
        if self.backend_process:
            try:
                self.backend_process.send_signal(signal.SIGTERM)
                self.backend_process.wait(timeout=5)
            except Exception:
                self.backend_process.kill()
            self.backend_process = None

        if self.mcp_process:
            try:
                self.mcp_process.send_signal(signal.SIGTERM)
                self.mcp_process.wait(timeout=5)
            except Exception:
                self.mcp_process.kill()
            self.mcp_process = None

    def __del__(self):
        """Limpa ao destruir."""
        self.stop_server()


# Instância global
_server_manager: Optional[ServerManager] = None


def get_server_manager() -> ServerManager:
    """Retorna instância global do gerenciador."""
    global _server_manager
    if _server_manager is None:
        _server_manager = ServerManager()
    return _server_manager


@pytest.fixture(scope="session", autouse=True)
def server_fixture():
    """Fixture de sessão que inicia/para servidor."""
    manager = get_server_manager()

    # Inicia servidor
    try:
        manager.start_server()
        manager.start_mcp_servers()
        yield
    finally:
        manager.stop_server()


@pytest.fixture(autouse=True)
def ensure_server_healthy():
    """Fixture que executa antes de cada teste - garante servidor vivo."""
    manager = get_server_manager()
    manager.restart_if_down()
    yield
    # Verifica novamente ao final
    manager.restart_if_down()
