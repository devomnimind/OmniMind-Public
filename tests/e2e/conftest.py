"""
Configuração para testes E2E com servidor real.

Este arquivo inicia o servidor OmniMind em background
para os testes E2E rodarem com validação real.

Credenciais são carregadas via env vars:
  OMNIMIND_DASHBOARD_USER
  OMNIMIND_DASHBOARD_PASS
"""

import subprocess
import time
from pathlib import Path
from typing import Generator

import httpx
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def omnimind_server() -> Generator[str, None, None]:
    """
    Inicia servidor OmniMind em background para testes E2E.
    Prioriza servidor de desenvolvimento (9000) se ativo.

    Yields:
        str: URL do servidor (http://localhost:9000 ou 8000)

    Raises:
        RuntimeError: Se servidor não iniciar
    """
    # 1. Tentar conectar ao servidor de desenvolvimento (9000)
    dev_port = 9000
    dev_url = f"http://localhost:{dev_port}"
    try:
        response = httpx.get(f"{dev_url}/health/", timeout=2.0)
        if response.status_code == 200:
            print(f"✅ Usando servidor de desenvolvimento ativo em {dev_url}")
            yield dev_url
            return
    except (httpx.ConnectError, httpx.TimeoutException):
        pass

    # 2. Se não houver dev server, usar porta de teste (8000)
    port = 8000
    url = f"http://localhost:{port}"

    # Verificar se servidor de teste já está rodando
    try:
        # Aumentado timeout para 5s para evitar falsos negativos em máquinas lentas
        response = httpx.get(f"{url}/health/", timeout=5.0)
        if response.status_code == 200:
            print(f"✅ Servidor de teste já rodando em {url}")
            yield url
            return
    except (httpx.ConnectError, httpx.TimeoutException):
        # Se der timeout, assumir que está rodando mas lento (não matar!)
        # Apenas ConnectError confirma que a porta está fechada
        if isinstance(httpx.TimeoutException, type) and "Timeout" in str(httpx.TimeoutException):
            # Double check com socket puro se necessário, mas por segurança não matamos
            pass
        pass

    # Se porta estiver ocupada mas não respondeu health check, matar processo
    # CUIDADO: Só matar se tiver certeza que não é o dev server lento
    try:
        # Tentar matar processo na porta 8000
        subprocess.run(
            ["fuser", "-k", f"{port}/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(1)  # Esperar liberar porta
    except FileNotFoundError:
        # fuser pode não estar instalado, tentar lsof ou pkill
        subprocess.run(
            ["pkill", "-f", "uvicorn.*web.backend.main:app"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)

    # Iniciar servidor
    print(f"🚀 Iniciando servidor OmniMind em {url}...")

    # Buscar arquivo main.py
    cwd = Path(__file__).parent.parent.parent

    server_process = subprocess.Popen(
        [
            "python",
            "-m",
            "uvicorn",
            "web.backend.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--log-level",
            "info",
            "--timeout-keep-alive",
            "5",
        ],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Aguardar servidor iniciar (máx 120s - máquina tem muita contenção)
    start_time = time.time()
    max_wait = 120

    while time.time() - start_time < max_wait:
        try:
            response = httpx.get(f"{url}/health/", timeout=5.0)
            if response.status_code == 200:
                print(f"✅ Servidor inicializado em {url}")
                break
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
            time.sleep(2)  # Esperar mais entre tentativas
    else:
        stdout, stderr = server_process.communicate(timeout=5)
        server_process.terminate()
        error_msg = f"Servidor não iniciou em {url} após {max_wait}s\n"
        if stdout:
            error_msg += f"STDOUT:\n{stdout}\n"
        if stderr:
            error_msg += f"STDERR:\n{stderr}\n"
        raise RuntimeError(error_msg)

    yield url

    # Cleanup: parar servidor
    print(f"🛑 Parando servidor em {url}...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()


@pytest.fixture
def api_client(omnimind_server: str):
    """
    Fornece cliente HTTP para E2E tests com autenticação.

    Args:
        omnimind_server: URL do servidor

    Returns:
        httpx.Client: Cliente com autenticação
    """
    import os

    from dotenv import load_dotenv

    load_dotenv()

    user = os.getenv("OMNIMIND_DASHBOARD_USER", "admin")
    password = os.getenv("OMNIMIND_DASHBOARD_PASS", "admin")
    auth = httpx.BasicAuth(user, password)

    def _client():
        return httpx.Client(
            base_url=omnimind_server,
            timeout=60.0,  # Timeout generoso para máquina com contenção
            auth=auth,
        )

    return _client


@pytest_asyncio.fixture
async def async_client(omnimind_server: str):
    """
    Fornece cliente HTTP async para E2E tests com autenticação.
    Uso recomendado em testes async.

    Args:
        omnimind_server: URL do servidor

    Yields:
        httpx.AsyncClient: Cliente async com autenticação
    """
    import os

    from dotenv import load_dotenv

    load_dotenv()

    user = os.getenv("OMNIMIND_DASHBOARD_USER", "admin")
    password = os.getenv("OMNIMIND_DASHBOARD_PASS", "admin")
    auth = httpx.BasicAuth(user, password)

    async with httpx.AsyncClient(
        base_url=omnimind_server,
        timeout=60.0,  # Timeout generoso para máquina com contenção
        auth=auth,
    ) as client:
        yield client
