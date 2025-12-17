"""
Configuração para testes E2E com servidor real.

Este arquivo inicia o servidor OmniMind em background
para os testes E2E rodarem com validação real.

Credenciais são carregadas via env vars:
  OMNIMIND_DASHBOARD_USER
  OMNIMIND_DASHBOARD_PASS

Gerenciamento de estado do servidor:
- Usa ServerStateManager (centralizado) para evitar conflitos
- Fixture omnimind_server adquire propriedade (OWNER_FIXTURE)
- ServerMonitorPlugin respeita e não reinicia servidor em uso
- Evita múltiplas tentativas simultâneas de restart
"""

import json
import os
import time
from pathlib import Path
from typing import Generator

import httpx
import pytest
import pytest_asyncio

from tests.server_state_manager import get_server_state_manager


def get_auth_credentials():
    """
    Resolve credenciais de autenticação na seguinte ordem:
    1. Variáveis de ambiente
    2. Arquivo config/dashboard_auth.json
    3. Default (admin/admin)
    """
    # 1. Env vars
    user = os.getenv("OMNIMIND_DASHBOARD_USER")
    password = os.getenv("OMNIMIND_DASHBOARD_PASS")

    if user and password:
        return user, password

    # 2. Auth file
    root_dir = Path(__file__).parent.parent.parent
    auth_file = root_dir / "config" / "dashboard_auth.json"

    if auth_file.exists():
        try:
            with open(auth_file) as f:
                data = json.load(f)
                return data.get("user", "admin"), data.get("pass", "admin")
        except Exception:
            pass

    # 3. Default
    return "admin", "admin"


@pytest.fixture(scope="session")
def auth_credentials():
    """
    Fixture que retorna as credenciais de autenticação (user, pass).
    """
    return get_auth_credentials()


def _check_port_in_use(port: int) -> bool:
    """Verifica se porta está em uso usando lsof (sem matar processos)."""
    import subprocess

    try:
        # Usar lsof para verificar se há processo na porta (não mata processos)
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-sTCP:LISTEN"],
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # lsof não disponível ou timeout - assumir que porta pode estar em uso
        return False


def _start_server_safely(url: str, state_manager) -> bool:
    """
    Inicia servidor apenas se não estiver rodando.

    IMPORTANTE: Não mata processos por sobrecarga de CPU (comportamento normal).
    Apenas verifica se porta está em uso e inicia se necessário.
    """
    import subprocess
    from pathlib import Path

    port = 8000

    # Verificar se porta está em uso (sem matar processos)
    if _check_port_in_use(port):
        print(f"✅ Porta {port} já está em uso - servidor provavelmente rodando")
        # Aguardar um pouco e verificar health
        for attempt in range(10):
            try:
                response = httpx.get(f"{url}/health/", timeout=2.0)
                if response.status_code == 200:
                    print(f"✅ Servidor confirmado rodando em {url}")
                    state_manager.mark_running()
                    return True
            except (httpx.ConnectError, httpx.TimeoutException):
                if attempt < 9:
                    time.sleep(1)
                    continue
        # Porta em uso mas não responde - pode estar iniciando ainda
        print(f"⚠️  Porta {port} em uso mas não responde - aguardando...")
        return False

    # Porta não está em uso - iniciar servidor
    print(f"🚀 Iniciando servidor OmniMind em {url}...")
    state_manager.mark_starting()

    root_dir = Path(__file__).parent.parent.parent
    start_script = root_dir / "scripts" / "canonical" / "system" / "start_omnimind_system.sh"

    if not start_script.exists():
        print(f"⚠️  Script de inicialização não encontrado: {start_script}")
        return False

    try:
        # Iniciar servidor em background (não bloquear)
        # NOTA: process não é usado diretamente, mas mantido para possível cleanup futuro
        subprocess.Popen(
            ["bash", str(start_script)],
            cwd=str(root_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Aguardar servidor iniciar (até 60s)
        for attempt in range(60):
            try:
                response = httpx.get(f"{url}/health/", timeout=2.0)
                if response.status_code == 200:
                    print(f"✅ Servidor iniciado com sucesso em {url}")
                    state_manager.mark_running()
                    return True
            except (httpx.ConnectError, httpx.TimeoutException):
                if attempt < 59:
                    time.sleep(1)
                    continue

        # Timeout - servidor não iniciou
        print("⚠️  Timeout aguardando servidor iniciar")
        return False

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False


@pytest.fixture(scope="session")
def omnimind_server() -> Generator[str, None, None]:
    """
    Inicia servidor OmniMind em background para testes E2E.
    Usa o servidor principal na porta 8000.

    Gerenciamento de estado:
    - Adquire propriedade no ServerStateManager
    - Verifica se servidor está rodando (via lsof + health check)
    - Inicia servidor apenas se não estiver rodando
    - NÃO mata processos por sobrecarga de CPU (comportamento normal)
    - Libera propriedade ao final da sessão

    Yields:
        str: URL do servidor (http://localhost:8000)

    Raises:
        RuntimeError: Se servidor não iniciar e não estiver rodando
    """
    # Usar porta principal do sistema (8000)
    port = 8000
    url = f"http://localhost:{port}"

    # Adquirir propriedade do servidor (impede reinicialização do plugin)
    state_manager = get_server_state_manager()
    acquired = state_manager.acquire_ownership("fixture")
    if not acquired:
        raise RuntimeError(
            "Não conseguiu adquirir propriedade do servidor " "(outro componente já controla)"
        )

    server_started_by_fixture = False
    try:
        # Verificar se servidor já está rodando e saudável
        try:
            response = httpx.get(f"{url}/health/", timeout=5.0)
            if response.status_code == 200:
                print(f"✅ Servidor já está rodando e saudável em {url}")
                state_manager.mark_running()
                yield url
                return
        except (httpx.ConnectError, httpx.TimeoutException):
            # Servidor não responde - verificar se porta está em uso
            pass

        # Verificar se porta está em uso (pode estar iniciando ainda)
        if _check_port_in_use(port):
            print(f"🔍 Porta {port} está em uso - aguardando servidor ficar pronto...")
            # Aguardar até 30s para servidor ficar pronto
            for attempt in range(30):
                try:
                    response = httpx.get(f"{url}/health/", timeout=2.0)
                    if response.status_code == 200:
                        print(f"✅ Servidor ficou pronto em {url}")
                        state_manager.mark_running()
                        yield url
                        return
                except (httpx.ConnectError, httpx.TimeoutException):
                    if attempt < 29:
                        time.sleep(1)
                        continue

            # Porta em uso mas não responde - pode estar com problema
            print(f"⚠️  Porta {port} em uso mas servidor não responde após 30s")
            print("   Tentando iniciar servidor mesmo assim...")

        # Servidor não está rodando - iniciar apenas nesses testes E2E
        if _start_server_safely(url, state_manager):
            server_started_by_fixture = True
            yield url
            return

        # Se chegou aqui, não conseguiu iniciar nem encontrar servidor rodando
        print(f"⚠️  Servidor não está acessível em {url}")
        print("   Para testes E2E, o servidor deve estar rodando via:")
        print("   - scripts/canonical/system/start_omnimind_system.sh")
        print("   - Ou via systemd/service manager")
        state_manager.mark_down()
        raise RuntimeError(
            f"Servidor OmniMind não está acessível em {url}. "
            "Para testes E2E, o servidor deve estar rodando em produção."
        )

    finally:
        # Cleanup: liberar propriedade do servidor
        # NOTA: Não para servidor em produção - apenas libera propriedade
        state_manager.release_ownership("fixture")
        if server_started_by_fixture:
            print("✅ Propriedade do servidor liberada (servidor continua rodando)")
        else:
            print("✅ Propriedade do servidor liberada")


@pytest.fixture
def api_client(omnimind_server: str):
    """
    Fornece cliente HTTP para E2E tests com autenticação.

    Args:
        omnimind_server: URL do servidor

    Returns:
        httpx.Client: Cliente com autenticação
    """
    user, password = get_auth_credentials()
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
    user, password = get_auth_credentials()
    auth = httpx.BasicAuth(user, password)

    async with httpx.AsyncClient(
        base_url=omnimind_server,
        timeout=60.0,  # Timeout generoso para máquina com contenção
        auth=auth,
    ) as client:
        yield client
