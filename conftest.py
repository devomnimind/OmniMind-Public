"""Project-wide pytest configuration."""
import os
import sys
import pytest

# Ensure .pytest_cache is created locally in project root
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "0"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import custom timeout retry plugin
from pytest_timeout_retry import TimeoutRetryPlugin


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
    
    # Register timeout retry plugin
    config.pluginmanager.register(TimeoutRetryPlugin(), "timeout_retry")


def pytest_collection_modifyitems(config, items):
    """
    Auto-mark tests como computational e força timeout mínimo 240s para Ollama.
    
    Timeouts:
    - Ollama (phase16, neurosymbolic, free_energy): MÍNIMO 240s
    - Heavy computational: 600s (10min)
    - Regular computational: 300s (5min)
    - Fast tests: 120s (default)
    """
    ollama_paths = [
        "phase16_integration",
        "neurosymbolic",
        "neural_component",
        "free_energy_lacanian",
        "cognitive",
    ]
    
    heavy_paths = [
        "test_integration_loss.py",
        "test_quantum_algorithms_comprehensive.py",
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
        
        # Determina timeout apropriado
        timeout_value = 120  # default
        
        # Ollama SEMPRE mínimo 240s (não é falha, é esperado)
        if any(path in item_path or path in test_name for path in ollama_paths):
            timeout_value = 240
            item.add_marker(pytest.mark.computational)
        # Heavy computational: 600s
        elif any(path in item_path for path in heavy_paths):
            timeout_value = 600
            item.add_marker(pytest.mark.computational)
        # Regular computational: 300s
        elif any(path in item_path for path in computational_paths):
            timeout_value = 300
            item.add_marker(pytest.mark.computational)
        
        # Aplica timeout
        item.add_marker(pytest.mark.timeout(timeout_value))

