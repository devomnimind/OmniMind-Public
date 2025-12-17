"""
Testes para BionAlphaFunction - Transformação β→α.

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

from datetime import datetime

import pytest

from src.psychoanalysis.alpha_element import AlphaElement
from src.psychoanalysis.beta_element import BetaElement
from src.psychoanalysis.bion_alpha_function import BionAlphaFunction


class TestBionAlphaFunction:
    """Testes para transformação α-function."""

    def test_initialization(self) -> None:
        """Testa inicialização da função alpha."""
        alpha_fn = BionAlphaFunction(transformation_rate=0.8, tolerance_threshold=0.7)

        assert alpha_fn.transformation_rate == 0.8
        assert alpha_fn.tolerance_threshold == 0.7
        assert len(alpha_fn.processing_history) == 0

    def test_initialization_invalid_rate(self) -> None:
        """Testa que taxa inválida gera erro."""
        with pytest.raises(ValueError, match="transformation_rate"):
            BionAlphaFunction(transformation_rate=1.5)

    def test_transform_simple_beta(self) -> None:
        """Testa transformação de β-element simples."""
        alpha_fn = BionAlphaFunction(transformation_rate=0.7)

        beta = BetaElement(
            raw_data="sensor input: temperatura = 25C",
            timestamp=datetime.now(),
            emotional_charge=0.3,
            source="temperature_sensor",
        )

        alpha = alpha_fn.transform(beta)

        assert alpha is not None
        assert isinstance(alpha, AlphaElement)
        assert alpha.origin_beta == beta
        assert 0.0 <= alpha.symbolic_potential <= 1.0
        assert alpha.can_be_thought()

    def test_transform_traumatic_beta_fails(self) -> None:
        """Testa que β-element traumático pode falhar na transformação."""
        # Função com baixa capacidade
        alpha_fn = BionAlphaFunction(transformation_rate=0.5, tolerance_threshold=0.6)

        # Element traumático
        beta = BetaElement(
            raw_data="ERRO CRÍTICO: Sistema em falha",
            timestamp=datetime.now(),
            emotional_charge=0.95,  # Muito alto
            source="error_monitor",
        )

        alpha = alpha_fn.transform(beta)

        # Pode falhar se capacidade insuficiente
        if alpha is None:
            assert len(alpha_fn.processing_history) == 1
            assert alpha_fn.processing_history[0]["status"] == "failure"
        else:
            # Se transformou, potencial simbólico deve ser baixo
            assert alpha.symbolic_potential < 0.5

    def test_transform_batch(self) -> None:
        """Testa transformação em lote."""
        alpha_fn = BionAlphaFunction(transformation_rate=0.8)

        betas = [
            BetaElement(
                raw_data=f"input {i}",
                timestamp=datetime.now(),
                emotional_charge=0.3,
                source="test",
            )
            for i in range(5)
        ]

        alphas = alpha_fn.transform_batch(betas)

        assert len(alphas) >= 3  # Pelo menos 60% devem transformar
        assert all(isinstance(a, AlphaElement) for a in alphas)

    def test_symbolic_potential_calculation(self) -> None:
        """Testa cálculo de potencial simbólico."""
        alpha_fn = BionAlphaFunction(transformation_rate=0.8)

        # Element com baixa carga emocional
        beta_low = BetaElement(
            raw_data="neutral observation",
            timestamp=datetime.now(),
            emotional_charge=0.1,
            source="observer",
        )

        alpha_low = alpha_fn.transform(beta_low)
        assert alpha_low is not None

        # Element com alta carga emocional
        beta_high = BetaElement(
            raw_data="intense experience",
            timestamp=datetime.now(),
            emotional_charge=0.7,
            source="observer",
        )

        alpha_high = alpha_fn.transform(beta_high)

        # Baixa emoção deve ter maior potencial simbólico
        if alpha_high is not None:
            assert alpha_low.symbolic_potential > alpha_high.symbolic_potential

    def test_processing_history(self) -> None:
        """Testa que histórico de processamento é mantido."""
        alpha_fn = BionAlphaFunction()

        beta1 = BetaElement(raw_data="test 1", timestamp=datetime.now(), emotional_charge=0.2)
        beta2 = BetaElement(raw_data="test 2", timestamp=datetime.now(), emotional_charge=0.9)

        alpha_fn.transform(beta1)
        alpha_fn.transform(beta2)

        assert len(alpha_fn.processing_history) == 2
        assert all("status" in entry for entry in alpha_fn.processing_history)

    def test_get_statistics(self) -> None:
        """Testa geração de estatísticas."""
        alpha_fn = BionAlphaFunction(transformation_rate=0.7)

        # Processa alguns elementos
        for i in range(10):
            beta = BetaElement(
                raw_data=f"input {i}",
                timestamp=datetime.now(),
                emotional_charge=0.3,
            )
            alpha_fn.transform(beta)

        stats = alpha_fn.get_statistics()

        assert stats["total_processed"] == 10
        assert "success_rate" in stats
        assert "failure_rate" in stats
        assert 0.0 <= stats["success_rate"] <= 1.0
        assert stats["success_rate"] + stats["failure_rate"] == 1.0

    def test_custom_narrative_builder(self) -> None:
        """Testa uso de narrative builder customizado."""

        def custom_builder(beta: BetaElement) -> str:
            return f"CUSTOM: {beta.source} - {beta.raw_data}"

        alpha_fn = BionAlphaFunction(narrative_builder=custom_builder)

        beta = BetaElement(raw_data="test data", timestamp=datetime.now(), source="custom_source")

        alpha = alpha_fn.transform(beta)

        assert alpha is not None
        assert alpha.narrative_form.startswith("CUSTOM:")
        assert "custom_source" in alpha.narrative_form
