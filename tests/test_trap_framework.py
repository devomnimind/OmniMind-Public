"""
Testes para TRAP Framework - Transparency, Reasoning, Adaptation, Perception

Phase 16: 11-tier metacognition hierarchy com scoring
"""

import pytest
from src.metacognition.trap_framework import (
    TRAPFramework,
    TRAPScore,
    TRAPComponent,
)


class TestTRAPScore:
    """Testes de score TRAP."""

    def test_trap_score_initialization(self) -> None:
        """Testa inicialização de score TRAP."""
        score = TRAPScore(
            transparency=0.8,
            reasoning=0.75,
            adaptation=0.9,
            perception=0.85,
        )
        assert score.transparency == 0.8
        assert score.reasoning == 0.75
        assert score.adaptation == 0.9
        assert score.perception == 0.85

    def test_overall_wisdom_calculation(self) -> None:
        """Testa cálculo de sabedoria geral."""
        score = TRAPScore(
            transparency=0.8,
            reasoning=0.75,
            adaptation=0.9,
            perception=0.85,
        )

        wisdom = score.overall_wisdom()
        assert 0.0 <= wisdom <= 1.0
        # Média ponderada: (0.8 + 0.75 + 0.9 + 0.85) / 4 = 0.825
        assert wisdom == pytest.approx(0.825, abs=0.01)

    def test_trap_score_bounds(self) -> None:
        """Testa que scores ficam dentro de 0-1."""
        score = TRAPScore(
            transparency=1.0,
            reasoning=0.0,
            adaptation=0.5,
            perception=0.75,
        )

        assert 0.0 <= score.transparency <= 1.0
        assert 0.0 <= score.reasoning <= 1.0
        assert 0.0 <= score.adaptation <= 1.0
        assert 0.0 <= score.perception <= 1.0


class TestTRAPComponent:
    """Testes de componentes TRAP."""

    def test_component_enum_values(self) -> None:
        """Testa valores de enum TRAPComponent."""
        assert TRAPComponent.TRANSPARENCY.value == "transparency"
        assert TRAPComponent.REASONING.value == "reasoning"
        assert TRAPComponent.ADAPTATION.value == "adaptation"
        assert TRAPComponent.PERCEPTION.value == "perception"

    def test_component_count(self) -> None:
        """Testa que há 4 componentes TRAP."""
        components = list(TRAPComponent)
        assert len(components) == 4


class TestTRAPFramework:
    """Testes do framework TRAP."""

    def test_initialization(self) -> None:
        """Testa inicialização do TRAP framework."""
        trap = TRAPFramework()
        assert trap is not None
        assert trap.metacognitive_level >= 0
        assert trap.metacognitive_level <= 4

    def test_evaluate_decision(self) -> None:
        """Testa avaliação de decisão."""
        trap = TRAPFramework()
        score = trap.evaluate("Merge PR with 100% test pass rate")

        assert isinstance(score, TRAPScore)
        assert score.transparency > 0.0
        assert score.reasoning > 0.0

    def test_get_wisdom_score(self) -> None:
        """Testa recuperação de score de sabedoria."""
        trap = TRAPFramework()
        trap.evaluate("Decision 1")
        trap.evaluate("Decision 2")

        wisdom = trap.get_wisdom_score()
        assert 0.0 <= wisdom <= 1.0

    def test_explain_decision(self) -> None:
        """Testa explicação de decisão."""
        trap = TRAPFramework()
        explanation = trap.explain_decision("Prioritize test coverage")

        assert "Prioritize test coverage" in explanation

    def test_metacognitive_level_getter(self) -> None:
        """Testa getter de nível metacognitivo."""
        trap = TRAPFramework()
        level = trap.get_metacognitive_level()

        assert isinstance(level, int)
        assert 0 <= level <= 4

    def test_advance_metacognitive_level(self) -> None:
        """Testa avanço de nível metacognitivo."""
        trap = TRAPFramework()
        initial_level = trap.get_metacognitive_level()

        # Começa no nível 4
        assert initial_level == 4

        trap.advance_metacognitive_level()
        new_level = trap.get_metacognitive_level()

        # Deve aumentar em 1 (até limite de 10)
        assert new_level == initial_level + 1

    def test_transparency_scoring(self) -> None:
        """Testa scoring de transparência."""
        trap = TRAPFramework()

        # Decisão com alta transparência
        score = trap.evaluate("Deploy to staging with full logging and monitoring")
        assert score.transparency > 0.5

    def test_reasoning_scoring(self) -> None:
        """Testa scoring de raciocínio."""
        trap = TRAPFramework()

        # Decisão com lógica clara
        score = trap.evaluate(
            "Increase test coverage from 78% to 85% by writing tests "
            "for 24 modules with <60% coverage"
        )
        assert score.reasoning > 0.5

    def test_adaptation_scoring(self) -> None:
        """Testa scoring de adaptação."""
        trap = TRAPFramework()

        # Decisão adaptativa
        score = trap.evaluate("Adjust strategy based on test results feedback")
        assert score.adaptation > 0.5

    def test_perception_scoring(self) -> None:
        """Testa scoring de percepção."""
        trap = TRAPFramework()

        # Decisão com boa percepção de contexto
        score = trap.evaluate(
            "Implement Phase 16 in parallel with remote tests " "considering available resources"
        )
        assert score.perception > 0.5

    def test_multiple_decisions_aggregation(self) -> None:
        """Testa agregação de múltiplas decisões."""
        trap = TRAPFramework()

        decisions = [
            "Fix failing tests",
            "Increase code coverage",
            "Implement neurosymbolic reasoning",
        ]

        scores = [trap.evaluate(d) for d in decisions]
        final_wisdom = trap.get_wisdom_score()

        # Deve refletir agregação de todas decisões
        assert 0.0 <= final_wisdom <= 1.0
        assert len(scores) == 3

    def test_trap_levels_0_through_4(self) -> None:
        """Testa que níveis 0-4 funcionam."""
        trap = TRAPFramework()

        # Começa no nível 4
        assert trap.get_metacognitive_level() == 4

        # Pode avançar até nível 10 (11-tier hierarchy 0-10)
        for i in range(6):  # Avança de 4 até 10
            level_before = trap.get_metacognitive_level()
            trap.advance_metacognitive_level()
            level_after = trap.get_metacognitive_level()
            assert level_after == level_before + 1

            score = trap.evaluate(f"Test decision at level {level_after}")
            assert score is not None


class TestTRAPIntegration:
    """Testes de integração TRAP com Neurosymbolic."""

    def test_trap_with_neurosymbolic_inference(self) -> None:
        """Testa TRAP avaliando inferência neurosymbolic."""
        from src.neurosymbolic import NeurosymbolicReasoner

        trap = TRAPFramework()
        reasoner = NeurosymbolicReasoner()

        # Fazer inferência
        inference = reasoner.infer("Should we deploy Phase 16?")

        # Avaliar com TRAP
        score = trap.evaluate(f"Reasoning: {inference.answer}")

        assert score is not None
        assert score.overall_wisdom() > 0.0

    def test_trap_explain_reasoning_chain(self) -> None:
        """Testa TRAP explicando cadeia de raciocínio."""
        from src.neurosymbolic import NeurosymbolicReasoner

        trap = TRAPFramework()
        reasoner = NeurosymbolicReasoner()

        # Inferência e explicação
        inference = reasoner.infer("Phase 16 implementation plan")
        reasoning_explanation = reasoner.explain(inference)
        trap_explanation = trap.explain_decision(reasoning_explanation)

        assert "Phase 16" in trap_explanation or "implementation" in trap_explanation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
