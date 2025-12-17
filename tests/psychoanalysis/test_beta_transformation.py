"""
Testes para transformação β→α (BetaElement e AlphaElement).

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

from datetime import datetime

import pytest

from src.psychoanalysis.alpha_element import AlphaElement
from src.psychoanalysis.beta_element import BetaElement


class TestBetaElement:
    """Testes para BetaElement."""

    def test_initialization(self) -> None:
        """Testa criação de β-element."""
        beta = BetaElement(
            raw_data="sensor input",
            timestamp=datetime.now(),
            emotional_charge=0.5,
            source="temperature_sensor",
        )

        assert beta.raw_data == "sensor input"
        assert beta.emotional_charge == 0.5
        assert beta.source == "temperature_sensor"
        assert beta.metadata == {}

    def test_emotional_charge_validation(self) -> None:
        """Testa validação de carga emocional."""
        # Válido
        beta = BetaElement(raw_data="test", timestamp=datetime.now(), emotional_charge=0.5)
        assert beta.emotional_charge == 0.5

        # Inválido - muito alto
        with pytest.raises(ValueError, match="emotional_charge"):
            BetaElement(raw_data="test", timestamp=datetime.now(), emotional_charge=1.5)

        # Inválido - negativo
        with pytest.raises(ValueError, match="emotional_charge"):
            BetaElement(raw_data="test", timestamp=datetime.now(), emotional_charge=-0.1)

    def test_get_intensity(self) -> None:
        """Testa cálculo de intensidade."""
        beta = BetaElement(raw_data="test", timestamp=datetime.now(), emotional_charge=0.7)

        intensity = beta.get_intensity()
        assert intensity == 0.7

    def test_is_traumatic(self) -> None:
        """Testa detecção de elemento traumático."""
        # Não traumático
        beta_low = BetaElement(
            raw_data="normal input", timestamp=datetime.now(), emotional_charge=0.4
        )
        assert not beta_low.is_traumatic()

        # Traumático
        beta_high = BetaElement(
            raw_data="critical error", timestamp=datetime.now(), emotional_charge=0.9
        )
        assert beta_high.is_traumatic(threshold=0.8)

    def test_to_dict(self) -> None:
        """Testa serialização para dict."""
        beta = BetaElement(
            raw_data="test data",
            timestamp=datetime(2025, 12, 9, 12, 0, 0),
            emotional_charge=0.6,
            source="test_source",
            metadata={"key": "value"},
        )

        beta_dict = beta.to_dict()

        assert beta_dict["raw_data"] == "test data"
        assert beta_dict["emotional_charge"] == 0.6
        assert beta_dict["source"] == "test_source"
        assert beta_dict["metadata"]["key"] == "value"
        assert beta_dict["type"] == "beta_element"

    def test_from_dict(self) -> None:
        """Testa reconstrução a partir de dict."""
        beta_dict = {
            "raw_data": "test data",
            "timestamp": "2025-12-09T12:00:00",
            "emotional_charge": 0.6,
            "source": "test_source",
            "metadata": {"key": "value"},
        }

        beta = BetaElement.from_dict(beta_dict)

        assert beta.raw_data == "test data"
        assert beta.emotional_charge == 0.6
        assert beta.source == "test_source"
        assert beta.metadata is not None
        assert beta.metadata["key"] == "value"


class TestAlphaElement:
    """Testes para AlphaElement."""

    def test_initialization(self) -> None:
        """Testa criação de α-element."""
        beta = BetaElement(raw_data="origin", timestamp=datetime.now())

        alpha = AlphaElement(
            content="processed content",
            origin_beta=beta,
            timestamp=datetime.now(),
            narrative_form="A narrative about the experience",
            symbolic_potential=0.7,
        )

        assert alpha.content == "processed content"
        assert alpha.origin_beta == beta
        assert alpha.symbolic_potential == 0.7
        assert alpha.narrative_form == "A narrative about the experience"

    def test_symbolic_potential_validation(self) -> None:
        """Testa validação de potencial simbólico."""
        beta = BetaElement(raw_data="test", timestamp=datetime.now())

        # Válido
        alpha = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.5,
        )
        assert alpha.symbolic_potential == 0.5

        # Inválido - muito alto
        with pytest.raises(ValueError, match="symbolic_potential"):
            AlphaElement(
                content="test",
                origin_beta=beta,
                timestamp=datetime.now(),
                symbolic_potential=1.5,
            )

    def test_can_be_thought(self) -> None:
        """Testa se elemento pode ser pensado."""
        beta = BetaElement(raw_data="test", timestamp=datetime.now())

        # Baixo potencial - não pensável
        alpha_low = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.2,
        )
        assert not alpha_low.can_be_thought()

        # Alto potencial - pensável
        alpha_high = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.6,
        )
        assert alpha_high.can_be_thought()

    def test_is_dream_capable(self) -> None:
        """Testa se elemento pode formar sonhos."""
        beta = BetaElement(raw_data="test", timestamp=datetime.now())

        # Baixo potencial
        alpha_low = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.4,
        )
        assert not alpha_low.is_dream_capable()

        # Alto potencial
        alpha_high = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.8,
        )
        assert alpha_high.is_dream_capable()

    def test_add_association(self) -> None:
        """Testa adição de associações."""
        beta = BetaElement(raw_data="test", timestamp=datetime.now())
        alpha = AlphaElement(content="test", origin_beta=beta, timestamp=datetime.now())

        assert len(alpha.associations) == 0

        alpha.add_association("alpha_id_1")
        assert len(alpha.associations) == 1

        alpha.add_association("alpha_id_2")
        assert len(alpha.associations) == 2

        # Não adiciona duplicata
        alpha.add_association("alpha_id_1")
        assert len(alpha.associations) == 2

    def test_get_complexity(self) -> None:
        """Testa cálculo de complexidade."""
        beta = BetaElement(raw_data="test", timestamp=datetime.now())

        # Sem associações
        alpha_simple = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.5,
        )
        complexity_simple = alpha_simple.get_complexity()
        assert complexity_simple == 0.5

        # Com associações
        alpha_complex = AlphaElement(
            content="test",
            origin_beta=beta,
            timestamp=datetime.now(),
            symbolic_potential=0.5,
        )
        alpha_complex.add_association("id1")
        alpha_complex.add_association("id2")
        complexity_complex = alpha_complex.get_complexity()
        assert complexity_complex > complexity_simple

    def test_to_dict(self) -> None:
        """Testa serialização para dict."""
        beta = BetaElement(raw_data="origin", timestamp=datetime.now())
        alpha = AlphaElement(
            content="processed",
            origin_beta=beta,
            timestamp=datetime(2025, 12, 9, 12, 0, 0),
            narrative_form="A narrative",
            symbolic_potential=0.7,
        )

        alpha_dict = alpha.to_dict()

        assert alpha_dict["content"] == "processed"
        assert alpha_dict["narrative_form"] == "A narrative"
        assert alpha_dict["symbolic_potential"] == 0.7
        assert alpha_dict["type"] == "alpha_element"
        assert "origin_beta" in alpha_dict

    def test_from_dict(self) -> None:
        """Testa reconstrução a partir de dict."""
        alpha_dict = {
            "content": "processed",
            "origin_beta": {
                "raw_data": "origin",
                "timestamp": "2025-12-09T12:00:00",
                "emotional_charge": 0.5,
                "source": "test",
                "metadata": {},
            },
            "timestamp": "2025-12-09T12:05:00",
            "narrative_form": "A narrative",
            "symbolic_potential": 0.7,
            "associations": ["id1", "id2"],
            "metadata": {},
        }

        alpha = AlphaElement.from_dict(alpha_dict)

        assert alpha.content == "processed"
        assert alpha.symbolic_potential == 0.7
        assert len(alpha.associations) == 2
