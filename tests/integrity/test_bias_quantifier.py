"""Tests for Bias Quantifier - Phase 26D

DEPRECATED: Módulo integrity.bias_quantifier não existe mais.

SUBSTITUIÇÃO:
- ✅ Substituído por: src.coevolution.bias_detector.BiasDetector
- ✅ Arquivo: src/coevolution/bias_detector.py
- ✅ Funcionalidade: Detecção e correção de vieses algorítmicos
- ✅ Status: Implementado e operacional

MIGRAÇÃO:
```python
# ANTES (deprecated):
from integrity.bias_quantifier import BiasQuantifier
quantifier = BiasQuantifier()
bias_score = quantifier.quantify_bias(...)

# DEPOIS (atual):
from src.coevolution.bias_detector import BiasDetector
detector = BiasDetector()
detections = detector.detect_bias(result)
corrected = detector.correct_bias(result)
```

Este teste foi marcado como skip até que seja atualizado para usar BiasDetector.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason=(
        "Módulo integrity.bias_quantifier foi substituído por "
        "src.coevolution.bias_detector.BiasDetector"
    )
)

# Import removido - módulo não existe
# from integrity.bias_quantifier import BiasQuantifier
#
# SUBSTITUIÇÃO: Use src.coevolution.bias_detector.BiasDetector


class TestBiasQuantifier:
    """Test Bias Quantifier - DEPRECATED: Use BiasDetector instead"""

    def test_init(self):
        """Test initialization - DEPRECATED"""
        # Nota: BiasQuantifier foi substituído por BiasDetector
        # Este teste está skip e mantido apenas para documentação
        # quantifier = BiasQuantifier()  # DEPRECATED
        # assert quantifier is not None
        # assert len(quantifier.bias_scores) == 0
        pytest.skip("Use test_bias_detector.py instead")

    def test_quantify_bias(self):
        """Test bias quantification - DEPRECATED"""
        # Nota: BiasQuantifier foi substituído por BiasDetector
        # quantifier = BiasQuantifier()  # DEPRECATED
        # content = {
        #     "text": "Western approaches to consciousness emphasize integration",
        #     "source": "paper_1",
        # }
        # bias_score = quantifier.quantify_bias(
        #     source_id="test_1",
        #     source_type="paper",
        #     content=content,
        # )
        # assert bias_score is not None
        # assert bias_score.source_id == "test_1"
        # assert 0.0 <= bias_score.score <= 1.0
        pytest.skip("Use test_bias_detector.py instead")

    def test_get_bias_score(self):
        """Test getting bias score - DEPRECATED"""
        # Nota: BiasQuantifier foi substituído por BiasDetector
        # quantifier = BiasQuantifier()  # DEPRECATED
        # content = {"text": "Test content"}
        # quantifier.quantify_bias("test_1", "paper", content)
        # score = quantifier.get_bias_score("test_1")
        # assert score is not None
        # assert score.source_id == "test_1"
        pytest.skip("Use test_bias_detector.py instead")
