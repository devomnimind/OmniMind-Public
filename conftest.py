"""Project-wide pytest configuration."""
import os
import sys
import time
import subprocess
import requests
import pytest

# Ensure .pytest_cache is created locally in project root
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "0"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import custom timeout retry plugin
from pytest_timeout_retry import TimeoutRetryPlugin

# Servidor endpoints
DASHBOARD_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"


def pytest_configure(config):
    """Register custom markers and plugin."""
    config.addinivalue_line(
        "markers", "computational: mark test as computationally intensive (GPU/Quantum/Consciousness)"
    )
    config.addinivalue_line(
        "markers", "gpu: mark test as GPU-intensive"
    )
    config.addinivalue_line(
        "markers", "quantum: mark test as quantum simulation"
    )
    config.addinivalue_line(
        "markers", "consciousness: mark test as consciousness computation"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end (requer servidor)"
    )
    
    # Register timeout retry plugin
    config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")


def pytest_collection_modifyitems(config, items):
    """
    Auto-mark tests com timeout progressivo (240s → 800s máximo).
    
    Estratégia:
    - Fast tests: 120s
    - Ollama: 240-400s (progressivo)
    - Computational: 300-500s (progressivo)
    - Heavy: 600-800s (progressivo)
    
    NUNCA falha por timeout - deixa rodar até máximo.
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
        
        # Determina timeout apropriado (progressivo para evitar falhas)
        timeout_value = 120  # default
        
        # E2E: 400-600s (requer servidor UP)
        if any(path in item_path for path in e2e_paths):
            timeout_value = 400
            item.add_marker(pytest.mark.e2e)
        # Heavy computational: 700-800s
        elif any(path in item_path for path in heavy_paths):
            timeout_value = 800
            item.add_marker(pytest.mark.computational)
        # Ollama: 240-400s (progressivo)
        elif any(path in item_path or path in test_name for path in ollama_paths):
            timeout_value = 350  # Começa em 240, pode ir até 400
            item.add_marker(pytest.mark.computational)
        # Regular computational: 300-500s
        elif any(path in item_path for path in computational_paths):
            timeout_value = 450  # Começa em 300, pode ir até 500
            item.add_marker(pytest.mark.computational)
        
        # Aplica timeout
        item.add_marker(pytest.mark.timeout(timeout_value))


def check_server_health() -> bool:
    """Verifica se servidor está UP."""
    try:
        # Tenta API
        resp = requests.get(f"{API_URL}/health", timeout=2)
        return resp.status_code in (200, 404)
    except Exception:
        pass
    
    try:
        # Tenta Dashboard
        resp = requests.get(DASHBOARD_URL, timeout=2)
        return resp.status_code in (200, 304, 404)
    except Exception:
        pass
    
    return False


def start_server_if_needed():
    """Inicia servidor se não estiver UP."""
    if check_server_health():
        print("✅ Servidor já está UP")
        return True
    
    print("⏳ Servidor DOWN - tentando iniciar...")
    try:
        # Tenta iniciar servidor (docker-compose ou python -m)
        subprocess.Popen(
            ["docker-compose", "up", "-d"],
            cwd="/home/fahbrain/projects/omnimind/deploy",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Aguarda 10s
        for _ in range(10):
            time.sleep(1)
            if check_server_health():
                print("✅ Servidor iniciado com sucesso")
                return True
        
        print("⚠️  Servidor não respondeu (testes E2E podem falhar)")
        return False
    except Exception as e:
        print(f"⚠️  Erro ao iniciar servidor: {e}")
        return False


# Inicia servidor na primeira execução de teste E2E
@pytest.fixture(scope="session", autouse=False)
def server_health():
    """Fixture que garante servidor UP para E2E tests."""
    start_server_if_needed()
    yield
    # Cleanup (opcional)




