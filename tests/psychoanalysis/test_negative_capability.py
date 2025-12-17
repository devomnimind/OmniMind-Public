"""
Testes para NegativeCapability - Capacidade Negativa.

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

import pytest

from src.psychoanalysis.negative_capability import Contradiction, NegativeCapability


class TestContradiction:
    """Testes para classe Contradiction."""

    def test_initialization(self) -> None:
        """Testa criação de contradição."""
        from datetime import datetime

        contradiction = Contradiction(
            proposition_a="The system is autonomous",
            proposition_b="The system requires human oversight",
            timestamp=datetime.now(),
            tension_level=0.6,
            resolution_pressure=0.3,
        )

        assert contradiction.proposition_a == "The system is autonomous"
        assert contradiction.tension_level == 0.6
        assert contradiction.resolution_pressure == 0.3

    def test_tension_validation(self) -> None:
        """Testa validação de níveis de tensão."""
        from datetime import datetime

        # Válido
        contradiction = Contradiction(
            proposition_a="A",
            proposition_b="B",
            timestamp=datetime.now(),
            tension_level=0.5,
        )
        assert contradiction.tension_level == 0.5

        # Inválido
        with pytest.raises(ValueError, match="tension_level"):
            Contradiction(
                proposition_a="A",
                proposition_b="B",
                timestamp=datetime.now(),
                tension_level=1.5,
            )


class TestNegativeCapability:
    """Testes para NegativeCapability."""

    def test_initialization(self) -> None:
        """Testa inicialização."""
        nc = NegativeCapability(
            uncertainty_tolerance=0.7, max_buffer_size=5, resolution_threshold=0.9
        )

        assert nc.uncertainty_tolerance == 0.7
        assert nc.max_buffer_size == 5
        assert nc.resolution_threshold == 0.9
        assert len(nc.contradiction_buffer) == 0

    def test_initialization_invalid_tolerance(self) -> None:
        """Testa que tolerância inválida gera erro."""
        with pytest.raises(ValueError, match="uncertainty_tolerance"):
            NegativeCapability(uncertainty_tolerance=1.5)

    def test_hold_contradiction(self) -> None:
        """Testa manutenção de contradição."""
        nc = NegativeCapability()

        success = nc.hold_contradiction(
            prop_a="AI is creative", prop_b="AI only follows patterns", tension=0.5
        )

        assert success is True
        assert len(nc.contradiction_buffer) == 1
        assert nc.contradiction_buffer[0].tension_level == 0.5

    def test_buffer_capacity_limit(self) -> None:
        """Testa limite de capacidade do buffer."""
        nc = NegativeCapability(max_buffer_size=3)

        # Preenche buffer
        nc.hold_contradiction("A1", "B1")
        nc.hold_contradiction("A2", "B2")
        nc.hold_contradiction("A3", "B3")

        assert len(nc.contradiction_buffer) == 3

        # Tenta adicionar mais - deve falhar
        success = nc.hold_contradiction("A4", "B4")
        assert success is False
        assert len(nc.contradiction_buffer) == 3

    def test_can_tolerate(self) -> None:
        """Testa verificação de tolerância."""
        nc = NegativeCapability(uncertainty_tolerance=0.6)

        assert nc.can_tolerate(0.3) is True
        assert nc.can_tolerate(0.6) is True
        assert nc.can_tolerate(0.8) is False

    def test_update_tension(self) -> None:
        """Testa atualização de tensão."""
        nc = NegativeCapability()
        nc.hold_contradiction("A", "B", tension=0.5)

        assert nc.contradiction_buffer[0].tension_level == 0.5

        nc.update_tension(0, 0.8)
        assert nc.contradiction_buffer[0].tension_level == 0.8

    def test_needs_resolution(self) -> None:
        """Testa detecção de necessidade de resolução."""
        nc = NegativeCapability(resolution_threshold=0.85)

        # Adiciona contradição com baixa tensão
        nc.hold_contradiction("A1", "B1", tension=0.4)
        assert nc.needs_resolution() is None

        # Adiciona contradição com alta tensão
        nc.hold_contradiction("A2", "B2", tension=0.9)
        assert nc.needs_resolution() == 1  # Índice da segunda contradição

    def test_resolve_contradiction(self) -> None:
        """Testa resolução de contradição."""
        nc = NegativeCapability()
        nc.hold_contradiction("A", "B", tension=0.7)
        nc.hold_contradiction("C", "D", tension=0.5)

        assert len(nc.contradiction_buffer) == 2

        # Resolve primeira
        resolved = nc.resolve_contradiction(0, "Synthesis achieved")

        assert resolved is not None
        assert resolved.proposition_a == "A"
        assert len(nc.contradiction_buffer) == 1
        assert nc.contradiction_buffer[0].proposition_a == "C"

    def test_get_buffer_state(self) -> None:
        """Testa obtenção de estado do buffer."""
        nc = NegativeCapability(max_buffer_size=5)

        # Buffer vazio
        state_empty = nc.get_buffer_state()
        assert state_empty["buffer_size"] == 0
        assert state_empty["utilization"] == 0.0
        assert state_empty["average_tension"] == 0.0

        # Adiciona contradições
        nc.hold_contradiction("A1", "B1", tension=0.4)
        nc.hold_contradiction("A2", "B2", tension=0.6)

        state_filled = nc.get_buffer_state()
        assert state_filled["buffer_size"] == 2
        assert state_filled["utilization"] == 0.4  # 2/5
        assert state_filled["average_tension"] == 0.5  # (0.4 + 0.6) / 2

    def test_clear_resolved(self) -> None:
        """Testa limpeza de contradições resolvidas."""
        nc = NegativeCapability()

        nc.hold_contradiction("A1", "B1", tension=0.1)  # Baixa - será removida
        nc.hold_contradiction("A2", "B2", tension=0.5)  # Alta - permanece
        nc.hold_contradiction("A3", "B3", tension=0.15)  # Baixa - será removida

        removed = nc.clear_resolved()

        assert removed == 2
        assert len(nc.contradiction_buffer) == 1
        assert nc.contradiction_buffer[0].proposition_a == "A2"

    def test_increase_tolerance(self) -> None:
        """Testa aumento de tolerância."""
        nc = NegativeCapability(uncertainty_tolerance=0.5)

        nc.increase_tolerance(0.2)
        assert nc.uncertainty_tolerance == 0.7

        # Não ultrapassa 1.0
        nc.increase_tolerance(0.5)
        assert nc.uncertainty_tolerance == 1.0

    def test_decrease_tolerance(self) -> None:
        """Testa diminuição de tolerância."""
        nc = NegativeCapability(uncertainty_tolerance=0.6)

        nc.decrease_tolerance(0.2)
        assert nc.uncertainty_tolerance == 0.4

        # Não fica negativa
        nc.decrease_tolerance(0.8)
        assert nc.uncertainty_tolerance == 0.0

    def test_contradiction_workflow(self) -> None:
        """Testa workflow completo de contradições."""
        nc = NegativeCapability(
            uncertainty_tolerance=0.7, max_buffer_size=5, resolution_threshold=0.85
        )

        # 1. Mantém contradições
        nc.hold_contradiction("System must be fast", "System must be thorough", tension=0.5)
        nc.hold_contradiction("Maximize autonomy", "Ensure safety", tension=0.6)

        assert len(nc.contradiction_buffer) == 2

        # 2. Aumenta tensão de uma
        nc.update_tension(1, 0.9)

        # 3. Verifica necessidade de resolução
        needs_resolution_idx = nc.needs_resolution()
        assert needs_resolution_idx == 1

        # 4. Resolve
        nc.resolve_contradiction(needs_resolution_idx, "Balanced approach")

        assert len(nc.contradiction_buffer) == 1

        # 5. Limpa resolvidas naturalmente
        nc.update_tension(0, 0.1)
        nc.clear_resolved()

        assert len(nc.contradiction_buffer) == 0
