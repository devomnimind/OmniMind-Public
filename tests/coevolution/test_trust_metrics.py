import pytest
from src.coevolution.trust_metrics import TrustEvent, TrustMetrics

"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Testes para Trust Metrics System.
"""


class TestTrustMetrics:
    """Testes do sistema de métricas de confiança."""

    def test_initialization(self) -> None:
        """Testa inicialização do sistema de trust."""
        trust = TrustMetrics()
        assert trust is not None
        assert len(trust.trust_scores) == 0
        assert len(trust.trust_history) == 0

    def test_get_trust_level_new_user(self) -> None:
        """Testa trust inicial para novo usuário."""
        trust = TrustMetrics()
        level = trust.get_trust_level("user1")

        assert level == pytest.approx(0.5)
        assert "user1" in trust.trust_scores

    def test_update_trust_success(self) -> None:
        """Testa atualização de trust após sucesso."""
        trust = TrustMetrics()

        # Trust inicial
        initial = trust.get_trust_level("user1")

        # Atualiza com sucesso
        delta = trust.update_trust("user1", {"success": True, "transparent": True})

        # Trust deve aumentar
        new_level = trust.get_trust_level("user1")
        assert new_level > initial
        assert delta > 0

    def test_update_trust_failure(self) -> None:
        """Testa atualização de trust após falha."""
        trust = TrustMetrics()

        # Trust inicial
        initial = trust.get_trust_level("user1")

        # Atualiza com falha
        delta = trust.update_trust("user1", {"success": False})

        # Trust deve diminuir
        new_level = trust.get_trust_level("user1")
        assert new_level < initial
        assert delta < 0

    def test_trust_breakdown(self) -> None:
        """Testa breakdown de trust por componente."""
        trust = TrustMetrics()

        breakdown = trust.get_trust_breakdown("user1")

        assert "overall" in breakdown
        assert "reliability" in breakdown
        assert "competence" in breakdown
        assert "transparency" in breakdown
        assert "alignment" in breakdown

        # Todos devem estar entre 0 e 1
        for score in breakdown.values():
            assert 0 <= score <= 1

    def test_trust_history(self) -> None:
        """Testa histórico de eventos de trust."""
        trust = TrustMetrics()

        # Cria alguns eventos
        trust.update_trust("user1", {"success": True})
        trust.update_trust("user1", {"success": False})
        trust.update_trust("user1", {"success": True})

        history = trust.get_trust_history("user1")

        assert len(history) == 3
        assert all(isinstance(e, TrustEvent) for e in history)

    def test_trust_history_limit(self) -> None:
        """Testa limite de histórico."""
        trust = TrustMetrics()

        # Cria vários eventos
        for _ in range(10):
            trust.update_trust("user1", {"success": True})

        history = trust.get_trust_history("user1", limit=5)

        assert len(history) == 5

    def test_reset_trust(self) -> None:
        """Testa reset de trust."""
        trust = TrustMetrics()

        # Constrói trust
        trust.update_trust("user1", {"success": True})
        trust.update_trust("user1", {"success": True})

        assert trust.get_trust_level("user1") > 0.5

        # Reset
        trust.reset_trust("user1")

        assert trust.get_trust_level("user1") == pytest.approx(0.5)
        assert len(trust.get_trust_history("user1")) == 0

    def test_multiple_users(self) -> None:
        """Testa múltiplos usuários independentes."""
        trust = TrustMetrics()

        # Usuário 1: sucesso
        trust.update_trust("user1", {"success": True})

        # Usuário 2: falha
        trust.update_trust("user2", {"success": False})

        level1 = trust.get_trust_level("user1")
        level2 = trust.get_trust_level("user2")

        assert level1 > level2

    def test_trust_components_weights(self) -> None:
        """Testa pesos dos componentes de trust."""
        trust = TrustMetrics()

        # Define valores específicos
        trust._initialize_trust("user1")
        trust.reliability_scores["user1"] = 1.0
        trust.competence_scores["user1"] = 1.0
        trust.transparency_scores["user1"] = 0.0
        trust.alignment_scores["user1"] = 0.0

        # Trust = 0.3 * 1.0 + 0.3 * 1.0 + 0.2 * 0.0 + 0.2 * 0.0 = 0.6
        assert trust.get_trust_level("user1") == pytest.approx(0.6)
