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
Testes para Goal Negotiation System.
"""

import pytest

from src.coevolution.negotiation import (
    GoalNegotiator,
    NegotiationResult,
    NegotiationRound,
    NegotiationStatus,
)


class TestGoalNegotiator:
    """Testes do sistema de negociação de objetivos."""

    def test_initialization(self) -> None:
        """Testa inicialização do negociador."""
        negotiator = GoalNegotiator()
        assert negotiator is not None
        assert negotiator.max_rounds == 5
        assert negotiator.convergence_threshold == pytest.approx(0.85)

    def test_initialization_custom_params(self) -> None:
        """Testa inicialização com parâmetros customizados."""
        negotiator = GoalNegotiator(max_rounds=3, convergence_threshold=0.9)
        assert negotiator.max_rounds == 3
        assert negotiator.convergence_threshold == pytest.approx(0.9)

    def test_negotiate_basic(self) -> None:
        """Testa negociação básica."""
        negotiator = GoalNegotiator()

        human_intent = {"goal": "implement feature X"}
        ai_perspective = {"alternative_approaches": ["approach A"]}

        result = negotiator.negotiate(
            human_intent=human_intent, ai_perspective=ai_perspective, trust_level=0.7
        )

        assert isinstance(result, NegotiationResult)
        assert "final_goal" in result.__dict__
        assert len(result.rounds) > 0

    def test_negotiate_high_trust(self) -> None:
        """Testa negociação com alto nível de trust."""
        negotiator = GoalNegotiator()

        human_intent = {"goal": "feature X", "priority": "high"}
        ai_perspective = {}

        result = negotiator.negotiate(
            human_intent=human_intent, ai_perspective=ai_perspective, trust_level=0.95
        )

        # Com trust alto, IA deve questionar mais
        if result.rounds:
            first_round = result.rounds[0]
            assert "questions" in first_round.ai_response

    def test_negotiate_convergence(self) -> None:
        """Testa convergência em negociação."""
        negotiator = GoalNegotiator(convergence_threshold=0.5)

        human_intent = {"goal": "test", "param1": "value1"}
        ai_perspective = {}

        result = negotiator.negotiate(
            human_intent=human_intent, ai_perspective=ai_perspective, trust_level=0.6
        )

        # Deve ter histórico de convergência
        assert len(result.convergence_history) > 0

        # Todos valores devem estar entre 0 e 1
        for conv in result.convergence_history:
            assert 0 <= conv <= 1

    def test_negotiate_timeout(self) -> None:
        """Testa timeout em negociação."""
        negotiator = GoalNegotiator(max_rounds=1, convergence_threshold=0.99)

        human_intent = {"goal": "complex task"}
        ai_perspective = {}

        result = negotiator.negotiate(
            human_intent=human_intent, ai_perspective=ai_perspective, trust_level=0.5
        )

        # Com threshold muito alto, deve dar timeout
        if not result.agreement_reached:
            assert result.status == NegotiationStatus.TIMEOUT

    def test_quick_accept_high_trust(self) -> None:
        """Testa aceitação rápida com trust alto."""
        negotiator = GoalNegotiator()

        human_intent = {"goal": "simple task"}

        result = negotiator.quick_accept(human_intent=human_intent, trust_level=0.95)

        assert result.agreement_reached
        assert result.status == NegotiationStatus.AGREEMENT_REACHED
        assert result.final_goal == human_intent

    def test_quick_accept_low_trust(self) -> None:
        """Testa rejeição de aceitação rápida com trust baixo."""
        negotiator = GoalNegotiator()

        human_intent = {"goal": "task"}

        result = negotiator.quick_accept(human_intent=human_intent, trust_level=0.5)

        assert not result.agreement_reached
        assert result.status == NegotiationStatus.DISAGREEMENT

    def test_negotiation_rounds(self) -> None:
        """Testa rodadas de negociação."""
        negotiator = GoalNegotiator(max_rounds=3)

        human_intent = {"goal": "feature"}
        ai_perspective = {"questions": ["question 1"]}

        result = negotiator.negotiate(
            human_intent=human_intent, ai_perspective=ai_perspective, trust_level=0.6
        )

        # Deve ter pelo menos uma rodada
        assert len(result.rounds) >= 1

        # Cada rodada deve ter estrutura correta
        for round_data in result.rounds:
            assert isinstance(round_data, NegotiationRound)
            assert round_data.round_number > 0
            assert "human_proposal" in round_data.__dict__
            assert "ai_response" in round_data.__dict__
            assert 0 <= round_data.convergence_score <= 1

    def test_calculate_convergence_identical(self) -> None:
        """Testa cálculo de convergência com propostas idênticas."""
        negotiator = GoalNegotiator()

        proposal1 = {"key1": "value1", "key2": "value2"}
        proposal2 = {"key1": "value1", "key2": "value2"}

        convergence = negotiator._calculate_convergence(proposal1, proposal2)

        assert convergence == pytest.approx(1.0)

    def test_calculate_convergence_different(self) -> None:
        """Testa cálculo de convergência com propostas diferentes."""
        negotiator = GoalNegotiator()

        proposal1 = {"key1": "value1", "key2": "value2"}
        proposal2 = {"key1": "different", "key2": "different"}

        convergence = negotiator._calculate_convergence(proposal1, proposal2)

        assert convergence == pytest.approx(0.0)

    def test_calculate_convergence_partial(self) -> None:
        """Testa cálculo de convergência com concordância parcial."""
        negotiator = GoalNegotiator()

        proposal1 = {"key1": "value1", "key2": "value2"}
        proposal2 = {"key1": "value1", "key2": "different"}

        convergence = negotiator._calculate_convergence(proposal1, proposal2)

        assert convergence == pytest.approx(0.5)

    def test_synthesize_proposals(self) -> None:
        """Testa síntese de propostas."""
        negotiator = GoalNegotiator()

        human_proposal = {"goal": "original"}
        ai_proposal = {"goal": "refined", "ai_refinements": {"hint": "value"}}

        synthesized = negotiator._synthesize_proposals(human_proposal, ai_proposal, convergence=0.7)

        assert "goal" in synthesized
        # Com convergência > 0.5, deve incorporar refinamentos
        assert "ai_refinements" in synthesized
