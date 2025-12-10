# tests/autopoietic/test_code_synthesizer_strategies.py
import pytest

from src.autopoietic.code_synthesizer import CodeSynthesizer
from src.autopoietic.meta_architect import ComponentSpec


@pytest.fixture
def synthesizer():
    return CodeSynthesizer()


def test_stabilize_synthesis(synthesizer):
    """Test code generation for STABILIZE strategy."""
    spec = ComponentSpec(name="safe_module", type="worker", config={"strategy": "STABILIZE"})

    result = synthesizer.synthesize([spec])
    signed_name = f"modulo_autopoiesis_data_{spec.name}"
    code = result[signed_name].source_code

    assert "try:" in code
    assert "except Exception as e:" in code
    assert "self._logger.error" in code
    assert "(STABILIZED)" in code


def test_optimize_synthesis(synthesizer):
    """Test code generation for OPTIMIZE strategy."""
    spec = ComponentSpec(name="fast_module", type="worker", config={"strategy": "OPTIMIZE"})

    result = synthesizer.synthesize([spec])
    signed_name = f"modulo_autopoiesis_data_{spec.name}"
    code = result[signed_name].source_code

    assert "import functools" in code
    assert "@functools.lru_cache(maxsize=128)" in code


def test_expand_synthesis(synthesizer):
    """Test code generation for EXPAND strategy."""
    spec = ComponentSpec(name="big_module", type="worker", config={"strategy": "EXPAND"})

    result = synthesizer.synthesize([spec])
    signed_name = f"modulo_autopoiesis_data_{spec.name}"
    code = result[signed_name].source_code

    assert "def _run_extended_features(self)" in code
    assert "(EXPANDED)" in code
    assert "self._run_extended_features()" in code
