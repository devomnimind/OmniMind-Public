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
    Auto-mark tests as computational based on file path and content.
    Sets appropriate timeouts:
    - Fast tests: 120s (default)
    - Computational tests: 300s (5min)
    - Heavy computational: 600s (10min)
    """
    computational_paths = [
        "consciousness",
        "quantum_consciousness",
        "quantum_ai",
        "science_validation",
        "experiments",
    ]
    
    heavy_paths = [
        "test_integration_loss.py",
        "test_free_energy_lacanian.py",
        "test_quantum_algorithms_comprehensive.py",
    ]
    
    for item in items:
        item_path = str(item.fspath)
        
        # Check if test is in heavy computational directories
        is_heavy = any(path in item_path for path in heavy_paths)
        
        # Check if test is in computational directories
        is_computational = any(path in item_path for path in computational_paths)
        
        # ALWAYS add timeout marker (override previous if exists)
        existing_timeout = item.get_closest_marker("timeout")
        if existing_timeout:
            item.own_markers.remove(existing_timeout)
        
        if is_heavy:
            # Heavy computational tests: 600s timeout
            item.add_marker(pytest.mark.timeout(600))
            item.add_marker(pytest.mark.computational)
        elif is_computational:
            # Regular computational tests: 300s timeout
            item.add_marker(pytest.mark.timeout(300))
            item.add_marker(pytest.mark.computational)
        else:
            # Fast tests: 120s timeout (default)
            item.add_marker(pytest.mark.timeout(120))

