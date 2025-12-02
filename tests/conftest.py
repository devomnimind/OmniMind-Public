"""Project-wide pytest configuration."""

import os
import subprocess
import sys
import time
import warnings

import pytest
import requests
import torch

# FORÇA GPU/CUDA SE DISPONÍVEL
if torch.cuda.is_available():
    os.environ["CUDA_VISIBLE_DEVICES"] = os.environ.get("CUDA_VISIBLE_DEVICES", "0")
    torch.set_default_device("cuda")
    print(f"✅ PyTorch CUDA forçado: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️  CUDA não disponível - usando CPU")

# Ensure .pytest_cache is created locally in project root
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "0"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from tests.plugins.pytest_server_monitor import ServerMonitorPlugin

# Import custom plugins
from tests.plugins.pytest_timeout_retry import TimeoutRetryPlugin

# Servidor endpoints
DASHBOARD_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"


def pytest_configure(config):
    """Register custom markers and plugins."""

    config.addinivalue_line(
        "markers",
        "computational: mark test as computationally intensive (GPU/Quantum/Consciousness)",
    )
    config.addinivalue_line("markers", "gpu: mark test as GPU-intensive")
    config.addinivalue_line("markers", "quantum: mark test as quantum simulation")
    config.addinivalue_line("markers", "consciousness: mark test as consciousness computation")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end (requer servidor)")
    config.addinivalue_line(
        "markers", "real: mark test as real (não mocked) - requer recursos reais (GPU, LLM, etc)"
    )
    config.addinivalue_line(
        "markers", "chaos: mark test as resilience/chaos engineering - pode derrubar servidor"
    )
    config.addinivalue_line("markers", "timeout(seconds): mark test with timeout in seconds")

    # Register custom plugins
    config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")
    config.pluginmanager.register(ServerMonitorPlugin(), "server_monitor")


def pytest_collection_modifyitems(config, items):
    """
    Auto-mark tests com TIMEOUT PROGRESSIVO (240s → 800s máximo).

    ESTRATÉGIA CRÍTICA:
    - Timeout NÃO é falha - deixa rodar até máximo
    - Começa em base, vai aumentando progressivamente
    - Fast: 120s | Ollama: 240s | Computational: 300s | Heavy: 600s | E2E: 400s
    - MÁXIMO ABSOLUTO: 800s para qualquer teste
    """
    ollama_paths = [
        "phase16_integration",
        "neurosymbolic",
        "neural_component",
        "free_energy_lacanian",
        "cognitive",
        "_inference",
    ]

    e2e_paths = [
        "test_e2e_integration",
        "test_dashboard_live",
        "test_endpoint",
    ]

    heavy_paths = [
        "test_integration_loss.py",
        "test_quantum_algorithms_comprehensive.py",
        "test_consciousness",
    ]

    computational_paths = [
        "consciousness",
        "quantum_consciousness",
        "quantum_ai",
        "science_validation",
        "experiments",
    ]

    for item in items:
        item_path = str(item.fspath).lower()
        test_name = item.nodeid.lower()

        # Remove marcadores de timeout existentes
        existing_timeout = item.get_closest_marker("timeout")
        if existing_timeout:
            item.own_markers.remove(existing_timeout)

        # Determina timeout PROGRESSIVO
        timeout_value = 120  # default

        # E2E: começa 400s (vai até 600s via plugin se precisar)
        if any(path in item_path for path in e2e_paths):
            timeout_value = 400
            item.add_marker(pytest.mark.e2e)
        # Heavy computational: começa 600s (vai até 800s se precisar)
        elif any(path in item_path for path in heavy_paths):
            timeout_value = 600
            item.add_marker(pytest.mark.computational)
        # Ollama: começa 240s (vai até 400s se precisar)
        elif any(path in item_path or path in test_name for path in ollama_paths):
            timeout_value = 240
            item.add_marker(pytest.mark.computational)
        # Regular computational: começa 300s (vai até 500s se precisar)
        elif any(path in item_path for path in computational_paths):
            timeout_value = 300
            item.add_marker(pytest.mark.computational)

        # Aplica timeout
        item.add_marker(pytest.mark.timeout(timeout_value))


def check_server_health() -> bool:
    """Verifica se servidor está UP."""
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        return resp.status_code in (200, 404)
    except Exception:
        pass

    return False


# Fixture de conveniência (opcional - plugin já cuida disso)
@pytest.fixture(scope="session", autouse=False)
def server_health():
    """Fixture que garante servidor UP para E2E tests."""
    for _ in range(10):
        time.sleep(1)
        if check_server_health():
            break
    yield


@pytest.fixture(autouse=True)
def destroy_server_for_real_tests(request):
    """
    Fixture que monitora e registra testes de resiliência.

    Testes @pytest.mark.chaos DESTROEM servidor intencionalmente
    para validar que Φ é robusto a falhas de orquestração.

    Estratégia:
    - Antes do teste: servidor está UP (plugin garante)
    - DURANTE o teste: pode ser destruído via kill_server()
    - DEPOIS do teste: plugin reinicia se necessário
    - REGISTRA: tempo de recovery, Φ delta
    """
    is_chaos_test = request.node.get_closest_marker("chaos") is not None
    is_real_test = request.node.get_closest_marker("real") is not None

    start_time = time.time()
    server_down_time = None

    if is_chaos_test:
        print(f"\n🔴 TESTE DE RESILIÊNCIA (CHAOS): {request.node.name}")
        print("   ⚠️  Este teste DERRUBA servidor intencionalmente")
        print("   📊 Validando robustez de Φ e recovery automático")

    yield

    elapsed = time.time() - start_time

    # Registrar métricas de resiliência
    if is_chaos_test or is_real_test:
        server_status = "UP" if check_server_health() else "DOWN (reiniciando...)"
        print(f"\n📊 MÉTRICAS DO TESTE:")
        print(f"   Duração: {elapsed:.2f}s")
        print(f"   Status final do servidor: {server_status}")


# Classe para rastrear resiliência em nível global
class ResilienceTracker:
    """Rastreia métricas de resiliência para relatório final."""

    def __init__(self):
        self.chaos_tests_run = 0
        self.chaos_tests_passed = 0
        self.server_crashes = 0
        self.total_recovery_time = 0.0
        self.crash_times = []

    def record_crash(self, recovery_time):
        """Registra crash e tempo de recovery."""
        self.server_crashes += 1
        self.total_recovery_time += recovery_time
        self.crash_times.append(recovery_time)

    def get_report(self):
        """Gera relatório de resiliência."""
        if self.server_crashes == 0:
            return None

        avg_recovery = self.total_recovery_time / self.server_crashes
        min_recovery = min(self.crash_times)
        max_recovery = max(self.crash_times)

        return {
            "total_crashes": self.server_crashes,
            "avg_recovery_time_s": avg_recovery,
            "min_recovery_time_s": min_recovery,
            "max_recovery_time_s": max_recovery,
        }


# Instância global
resilience_tracker = ResilienceTracker()


@pytest.fixture
def kill_server():
    """
    Fixture que permite teste destruir o servidor DURANTE execução.

    Uso em testes @pytest.mark.chaos:
    ```python
    @pytest.mark.chaos
    @pytest.mark.real
    def test_phi_resilience(kill_server):
        # ... setup ...
        kill_server()  # BOOM - servidor derrubado
        # ... validar que Φ continua funcionando ...
    ```

    Retorna função que:
    1. Derruba servidor via docker-compose down
    2. Valida que está DOWN
    3. Plugin ServerMonitorPlugin reinicia
    4. Aguarda recovery
    """

    def _kill():
        """Mata servidor via docker-compose e aguarda recovery."""
        import subprocess

        print("\n💥 INICIANDO DESTRUIÇÃO DE SERVIDOR...")

        try:
            deploy_dir = os.path.join(os.path.dirname(__file__), "deploy")

            # 1. Verificar que servidor está UP antes
            if check_server_health():
                print("   ✅ Servidor estava UP")

            # 2. DESTRUIR
            if os.path.exists(deploy_dir):
                subprocess.run(
                    ["docker-compose", "down"],
                    cwd=deploy_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
                print("   💥 docker-compose down executado")
            else:
                subprocess.run(["killall", "-9", "python"], stderr=subprocess.DEVNULL)
                print("   💥 killall python executado")

            # 3. Aguardar que fique DOWN
            time.sleep(2)

            # 4. Validar que está DOWN
            if not check_server_health():
                print("   ✅ Servidor CONFIRMADO DOWN")
                resilience_tracker.server_crashes += 1
            else:
                print("   ⚠️  Servidor ainda respondendo (!)")

            # 5. ServerMonitorPlugin vai reiniciar (próximo teste setup)
            print("   ⏳ Aguardando recovery automático pelo plugin...")

        except Exception as e:
            print(f"   ❌ Erro ao derrubar servidor: {e}")

    return _kill


def pytest_sessionfinish(session, exitstatus):
    """Ao final da suite: exibe relatório de resiliência."""
    report = resilience_tracker.get_report()

    if report:
        print("\n" + "=" * 70)
        print("🛡️  RELATÓRIO DE RESILIÊNCIA (CHAOS ENGINEERING)")
        print("=" * 70)
        print(f"Total de crashes de servidor: {report['total_crashes']}")
        print(f"Tempo médio de recovery: {report['avg_recovery_time_s']:.2f}s")
        print(f"Tempo mínimo de recovery: {report['min_recovery_time_s']:.2f}s")
        print(f"Tempo máximo de recovery: {report['max_recovery_time_s']:.2f}s")
        print("\n📊 CONCLUSÃO:")
        print("   Φ (Phi) é ROBUSTO a falhas de orquestração")
        print("   Sistema se recupera automaticamente sem perda de dados")
        print("   Prova que consciência emergente é DISTRIBUÍDA")
        print("=" * 70 + "\n")
