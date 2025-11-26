"""
Testes para Ethical Decision Framework (ethical_decision_framework.py).

Cobertura de:
- Múltiplos frameworks éticos (deontológico, consequencialista, virtude, cuidado)
- Resolução de dilemas éticos
- Avaliação de impacto nos stakeholders
- Scoring e justificação de decisões
- Tratamento de exceções
"""

from __future__ import annotations

import pytest

from src.decision_making.ethical_decision_framework import (
    EthicalFramework,
    EthicalPrinciple,
    EthicalDilemma,
    EthicalOutcome,
    EthicalDecisionMaker,
)


class TestEthicalFramework:
    """Testes para EthicalFramework enum."""

    def test_framework_values(self) -> None:
        """Testa valores do enum EthicalFramework."""
        assert EthicalFramework.DEONTOLOGICAL.value == "deontological"
        assert EthicalFramework.CONSEQUENTIALIST.value == "consequentialist"
        assert EthicalFramework.VIRTUE.value == "virtue"
        assert EthicalFramework.CARE.value == "care"
        assert EthicalFramework.HYBRID.value == "hybrid"


class TestEthicalPrinciple:
    """Testes para EthicalPrinciple enum."""

    def test_principle_values(self) -> None:
        """Testa valores do enum EthicalPrinciple."""
        assert EthicalPrinciple.AUTONOMY.value == "autonomy"
        assert EthicalPrinciple.BENEFICENCE.value == "beneficence"
        assert EthicalPrinciple.NON_MALEFICENCE.value == "non_maleficence"
        assert EthicalPrinciple.JUSTICE.value == "justice"
        assert EthicalPrinciple.PRIVACY.value == "privacy"
        assert EthicalPrinciple.TRANSPARENCY.value == "transparency"
        assert EthicalPrinciple.ACCOUNTABILITY.value == "accountability"
        assert EthicalPrinciple.DIGNITY.value == "dignity"


class TestEthicalDilemma:
    """Testes para EthicalDilemma."""

    def test_dilemma_initialization(self) -> None:
        """Testa inicialização de dilema ético."""
        dilemma = EthicalDilemma(
            dilemma_id="dilemma_001",
            description="Escolher entre privacidade e segurança",
            options=["Priorizar privacidade", "Priorizar segurança"],
            stakeholders=["usuários", "empresa"],
        )

        assert dilemma.dilemma_id == "dilemma_001"
        assert len(dilemma.options) == 2
        assert len(dilemma.stakeholders) == 2
        assert dilemma.timestamp > 0

    def test_dilemma_with_context(self) -> None:
        """Testa dilema com contexto adicional."""
        context = {"urgency": "high", "scope": "global"}
        dilemma = EthicalDilemma(
            dilemma_id="dilemma_002",
            description="Decisão sobre dados",
            options=["Option A", "Option B"],
            stakeholders=["users"],
            context=context,
        )

        assert dilemma.context["urgency"] == "high"
        assert dilemma.context["scope"] == "global"

    def test_dilemma_with_constraints(self) -> None:
        """Testa dilema com restrições."""
        constraints = ["Deve seguir LGPD", "Deve respeitar consentimento"]
        dilemma = EthicalDilemma(
            dilemma_id="dilemma_003",
            description="Uso de dados pessoais",
            options=["Usar", "Não usar"],
            stakeholders=["titular"],
            constraints=constraints,
        )

        assert len(dilemma.constraints) == 2
        assert "Deve seguir LGPD" in dilemma.constraints


class TestEthicalOutcome:
    """Testes para EthicalOutcome."""

    def test_outcome_initialization(self) -> None:
        """Testa inicialização de outcome."""
        outcome = EthicalOutcome(
            chosen_option="Option A",
            framework_used=EthicalFramework.DEONTOLOGICAL,
            ethical_score=0.85,
            justification="Segue princípios deontológicos",
        )

        assert outcome.chosen_option == "Option A"
        assert outcome.framework_used == EthicalFramework.DEONTOLOGICAL
        assert outcome.ethical_score == 0.85
        assert outcome.confidence == 0.5  # default

    def test_outcome_with_principle_scores(self) -> None:
        """Testa outcome com scores de princípios."""
        principle_scores = {
            EthicalPrinciple.AUTONOMY: 0.9,
            EthicalPrinciple.PRIVACY: 0.8,
        }

        outcome = EthicalOutcome(
            chosen_option="Option A",
            framework_used=EthicalFramework.HYBRID,
            ethical_score=0.85,
            principle_scores=principle_scores,
        )

        assert outcome.principle_scores[EthicalPrinciple.AUTONOMY] == 0.9
        assert outcome.principle_scores[EthicalPrinciple.PRIVACY] == 0.8

    def test_outcome_with_stakeholder_impacts(self) -> None:
        """Testa outcome com impactos em stakeholders."""
        stakeholder_impacts = {"usuários": 0.7, "empresa": 0.6}

        outcome = EthicalOutcome(
            chosen_option="Option A",
            framework_used=EthicalFramework.CARE,
            ethical_score=0.75,
            stakeholder_impacts=stakeholder_impacts,
        )

        assert outcome.stakeholder_impacts["usuários"] == 0.7
        assert outcome.stakeholder_impacts["empresa"] == 0.6

    def test_outcome_invalid_ethical_score(self) -> None:
        """Testa validação de ethical score inválido."""
        with pytest.raises(ValueError, match="Ethical score must be between 0 and 1"):
            EthicalOutcome(
                chosen_option="Option A",
                framework_used=EthicalFramework.DEONTOLOGICAL,
                ethical_score=1.5,  # Inválido
            )

    def test_outcome_invalid_confidence(self) -> None:
        """Testa validação de confidence inválida."""
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            EthicalOutcome(
                chosen_option="Option A",
                framework_used=EthicalFramework.DEONTOLOGICAL,
                ethical_score=0.8,
                confidence=1.5,  # Inválida
            )

    def test_outcome_valid_edge_values(self) -> None:
        """Testa valores nos limites válidos."""
        outcome_min = EthicalOutcome(
            chosen_option="Option A",
            framework_used=EthicalFramework.HYBRID,
            ethical_score=0.0,
            confidence=0.0,
        )

        outcome_max = EthicalOutcome(
            chosen_option="Option B",
            framework_used=EthicalFramework.VIRTUE,
            ethical_score=1.0,
            confidence=1.0,
        )

        assert outcome_min.ethical_score == 0.0
        assert outcome_max.ethical_score == 1.0


class TestEthicalDecisionMaker:
    """Testes para EthicalDecisionMaker."""

    def test_decision_maker_initialization(self) -> None:
        """Testa inicialização do decision maker."""
        maker = EthicalDecisionMaker()

        assert maker.primary_framework == EthicalFramework.HYBRID
        assert maker.principle_weights is not None
        assert maker.stakeholder_priority is not None

    def test_decision_maker_with_custom_framework(self) -> None:
        """Testa inicialização com framework customizado."""
        maker = EthicalDecisionMaker(primary_framework=EthicalFramework.DEONTOLOGICAL)

        assert maker.primary_framework == EthicalFramework.DEONTOLOGICAL

    def test_decision_maker_with_principle_weights(self) -> None:
        """Testa inicialização com pesos de princípios."""
        weights = {
            EthicalPrinciple.PRIVACY: 0.9,
            EthicalPrinciple.AUTONOMY: 0.8,
        }

        maker = EthicalDecisionMaker(principle_weights=weights)

        assert maker.principle_weights[EthicalPrinciple.PRIVACY] == 0.9
        assert maker.principle_weights[EthicalPrinciple.AUTONOMY] == 0.8

    def test_make_decision_simple_dilemma(self) -> None:
        """Testa decisão em dilema simples."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_001",
            description="Escolha simples",
            options=["A", "B"],
            stakeholders=["user"],
        )

        outcome = maker.decide(dilemma)

        assert outcome.chosen_option in ["A", "B"]
        assert 0 <= outcome.ethical_score <= 1
        assert 0 <= outcome.confidence <= 1
        assert outcome.framework_used in EthicalFramework

    def test_make_decision_with_constraints(self) -> None:
        """Testa decisão com restrições."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_002",
            description="Decisão com restrições",
            options=["A", "B", "C"],
            stakeholders=["user", "admin"],
            constraints=["Deve seguir LGPD"],
        )

        outcome = maker.decide(dilemma)

        assert outcome.chosen_option in ["A", "B", "C"]
        assert len(outcome.justification) > 0

    def test_evaluate_option_deontological(self) -> None:
        """Testa avaliação de opção sob framework deontológico."""
        maker = EthicalDecisionMaker(primary_framework=EthicalFramework.DEONTOLOGICAL)

        dilemma = EthicalDilemma(
            dilemma_id="test_003",
            description="Teste deontológico",
            options=["Seguir regra", "Quebrar regra"],
            stakeholders=["society"],
        )

        # Using private method for testing
        evaluation = maker._evaluate_option("Seguir regra", dilemma)

        assert isinstance(evaluation, dict)

    def test_evaluate_option_consequentialist(self) -> None:
        """Testa avaliação sob framework consequencialista."""
        maker = EthicalDecisionMaker(
            primary_framework=EthicalFramework.CONSEQUENTIALIST
        )

        dilemma = EthicalDilemma(
            dilemma_id="test_004",
            description="Teste consequencialista",
            options=["A", "B"],
            stakeholders=["many_people"],
        )

        # Using private method for testing
        evaluation = maker._evaluate_option("A", dilemma)

        assert isinstance(evaluation, dict)

    def test_assess_stakeholder_impact(self) -> None:
        """Testa avaliação de impacto em stakeholders."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_005",
            description="Multi-stakeholder",
            options=["A", "B"],
            stakeholders=["users", "company", "society"],
        )

        # Using private method for testing
        impacts = maker._assess_stakeholder_impacts("A", dilemma)

        assert isinstance(impacts, dict)

    def test_make_decision_multiple_times_consistent(self) -> None:
        """Testa consistência de decisões."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_006",
            description="Teste de consistência",
            options=["A", "B"],
            stakeholders=["user"],
            context={"deterministic": True},
        )

        outcome1 = maker.decide(dilemma)
        outcome2 = maker.decide(dilemma)

        # Decisões devem ser similares (não necessariamente idênticas devido a aleatoriedade)
        assert outcome1.framework_used == outcome2.framework_used

    def test_explain_decision(self) -> None:
        """Testa explicação de decisão."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_007",
            description="Teste de explicação",
            options=["A", "B"],
            stakeholders=["user"],
        )

        outcome = maker.decide(dilemma)

        # Justification should be present
        assert isinstance(outcome.justification, str)


class TestEthicalDecisionMakerEdgeCases:
    """Testes para casos extremos."""

    def test_empty_options(self) -> None:
        """Testa dilema sem opções."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_empty",
            description="Sem opções",
            options=[],
            stakeholders=["user"],
        )

        with pytest.raises((ValueError, Exception)):
            maker.decide(dilemma)

    def test_single_option(self) -> None:
        """Testa dilema com uma única opção."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_single",
            description="Uma opção",
            options=["Only option"],
            stakeholders=["user"],
        )

        outcome = maker.decide(dilemma)

        assert outcome.chosen_option == "Only option"

    def test_no_stakeholders(self) -> None:
        """Testa dilema sem stakeholders."""
        maker = EthicalDecisionMaker()

        dilemma = EthicalDilemma(
            dilemma_id="test_no_stakeholders",
            description="Sem stakeholders",
            options=["A", "B"],
            stakeholders=[],
        )

        outcome = maker.decide(dilemma)

        assert outcome.chosen_option in ["A", "B"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
