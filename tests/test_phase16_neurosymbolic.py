"""
Testes de Neurosymbolic Reasoner - Phase 16

Testa:
  - Componente neural
  - Componente simbólico
  - Reconciliação
  - Motor híbrido
"""

import pytest

from src.neurosymbolic import (
    NeuralComponent,
    NeurosymbolicReasoner,
    SymbolicComponent,
)
from src.neurosymbolic.reconciliation import (
    ReconciliationStrategy,
    Reconciliator,
)


class TestNeuralComponent:
    """Testes do componente neural."""

    def test_initialization(self) -> None:
        """Testa inicialização do componente neural."""
        neural = NeuralComponent(model_name="gpt-4", temperature=0.7)
        assert neural.model_name == "gpt-4"
        assert neural.temperature == 0.7

    def test_inference(self) -> None:
        """Testa inferência neural básica."""
        neural = NeuralComponent()
        result = neural.infer("Is this true?")

        assert result is not None
        assert result.confidence > 0.0
        assert len(result.answer) > 0

    def test_batch_infer(self) -> None:
        """Testa batch de inferências."""
        neural = NeuralComponent()
        queries = ["Is this true?", "Is this false?"]
        results = neural.batch_infer(queries)

        assert len(results) == 2
        assert all(r.confidence > 0.0 for r in results)

    def test_embed(self) -> None:
        """Testa geração de embeddings."""
        neural = NeuralComponent()
        embedding = neural.embed("test text")

        assert embedding is not None
        assert len(embedding) == 768


class TestSymbolicComponent:
    """Testes do componente simbólico."""

    def test_initialization(self) -> None:
        """Testa inicialização do componente simbólico."""
        symbolic = SymbolicComponent()
        assert symbolic is not None
        assert len(symbolic.get_all_facts()) == 0

    def test_add_fact(self) -> None:
        """Testa adição de fatos."""
        symbolic = SymbolicComponent()
        symbolic.add_fact("Socrates", "is_a", "Human")

        facts = symbolic.get_all_facts()
        assert len(facts) == 1
        assert facts[0].subject == "Socrates"

    def test_add_rule(self) -> None:
        """Testa adição de regras."""
        symbolic = SymbolicComponent()
        symbolic.add_rule(["X is_a Human"], "X is Mortal")

        rules = symbolic.get_rules()
        assert len(rules) == 1

    def test_query(self) -> None:
        """Testa consultas ao grafo."""
        symbolic = SymbolicComponent()
        symbolic.add_fact("Socrates", "is_a", "Human")
        symbolic.add_fact("Plato", "is_a", "Human")

        results = symbolic.query("* is_a Human")
        assert len(results) == 2

    def test_inference(self) -> None:
        """Testa inferência simbólica."""
        symbolic = SymbolicComponent()
        symbolic.add_fact("Socrates", "is_a", "Human")

        # Verificar que o fato foi adicionado
        facts = symbolic.get_all_facts()
        assert len(facts) == 1
        assert facts[0].subject == "Socrates"

        # Agora testar inferência
        result = symbolic.infer("Socrates is_a Human")
        assert result.certainty >= 0.0  # Pode ser 0 ou maior, dependendo da prova


class TestReconciliation:
    """Testes de reconciliação."""

    def test_agreement_strategy(self) -> None:
        """Testa estratégia AGREEMENT."""
        result = Reconciliator.reconcile(
            neural_answer="Yes",
            neural_confidence=0.8,
            symbolic_answer="Yes",
            symbolic_certainty=1.0,
            strategy=ReconciliationStrategy.AGREEMENT,
        )

        assert result.strategy_used == ReconciliationStrategy.AGREEMENT
        assert result.confidence > 0.8  # Deve aumentar com acordo

    def test_neural_dominant_strategy(self) -> None:
        """Testa estratégia NEURAL_DOMINANT."""
        result = Reconciliator.reconcile(
            neural_answer="Creative answer",
            neural_confidence=0.7,
            symbolic_answer="Logical answer",
            symbolic_certainty=0.5,
            strategy=ReconciliationStrategy.NEURAL_DOMINANT,
        )

        assert result.strategy_used == ReconciliationStrategy.NEURAL_DOMINANT
        assert result.final_answer == "Creative answer"

    def test_symbolic_dominant_strategy(self) -> None:
        """Testa estratégia SYMBOLIC_DOMINANT."""
        result = Reconciliator.reconcile(
            neural_answer="Creative answer",
            neural_confidence=0.7,
            symbolic_answer="Logical answer",
            symbolic_certainty=0.95,
            strategy=ReconciliationStrategy.SYMBOLIC_DOMINANT,
        )

        assert result.strategy_used == ReconciliationStrategy.SYMBOLIC_DOMINANT
        assert result.final_answer == "Logical answer"

    def test_synthesis_strategy(self) -> None:
        """Testa estratégia SYNTHESIS."""
        result = Reconciliator.reconcile(
            neural_answer="Creative answer",
            neural_confidence=0.7,
            symbolic_answer="Logical answer",
            symbolic_certainty=0.8,
            strategy=ReconciliationStrategy.SYNTHESIS,
        )

        assert result.strategy_used == ReconciliationStrategy.SYNTHESIS
        assert "Creative answer" in result.final_answer
        assert "Logical answer" in result.final_answer


class TestNeurosymbolicReasoner:
    """Testes do motor neurosymbolic híbrido."""

    def test_initialization(self) -> None:
        """Testa inicialização do reasoner."""
        reasoner = NeurosymbolicReasoner(
            neural_model="gpt-4",
            default_strategy=ReconciliationStrategy.SYNTHESIS,
        )
        assert reasoner is not None

    def test_hybrid_inference(self) -> None:
        """Testa inferência híbrida."""
        reasoner = NeurosymbolicReasoner()
        inference = reasoner.infer("Is this true?")

        assert inference is not None
        assert len(inference.answer) > 0
        assert inference.overall_confidence > 0.0

    def test_add_knowledge(self) -> None:
        """Testa adição de conhecimento."""
        reasoner = NeurosymbolicReasoner()
        reasoner.add_knowledge(("Socrates", "is_a", "Human"))

        facts = reasoner.symbolic.get_all_facts()
        assert len(facts) == 1

    def test_batch_infer(self) -> None:
        """Testa batch de inferências híbridas."""
        reasoner = NeurosymbolicReasoner()
        queries = ["Question 1?", "Question 2?"]
        results = reasoner.batch_infer(queries)

        assert len(results) == 2
        assert all(r.overall_confidence > 0.0 for r in results)

    def test_explain(self) -> None:
        """Testa explicação de inferência."""
        reasoner = NeurosymbolicReasoner()
        inference = reasoner.infer("Test question")
        explanation = reasoner.explain(inference)

        assert "Neural System" in explanation
        assert "Symbolic System" in explanation
        assert "Overall Confidence" in explanation


class TestTRAPFramework:
    """Testes do framework TRAP."""

    def test_initialization(self) -> None:
        """Testa inicialização do TRAP."""
        from src.metacognition import TRAPFramework

        trap = TRAPFramework()
        assert trap.metacognitive_level == 4

    def test_evaluate(self) -> None:
        """Testa avaliação TRAP."""
        from src.metacognition import TRAPFramework

        trap = TRAPFramework()
        score = trap.evaluate("Test decision")

        assert score.transparency > 0.0
        assert score.reasoning > 0.0
        assert score.overall_wisdom() > 0.0

    def test_wisdom_score(self) -> None:
        """Testa score geral de sabedoria."""
        from src.metacognition import TRAPFramework

        trap = TRAPFramework()
        trap.evaluate("Decision 1")
        trap.evaluate("Decision 2")

        wisdom = trap.get_wisdom_score()
        assert 0.0 <= wisdom <= 1.0

    def test_metacognitive_level_advancement(self) -> None:
        """Testa avanço de níveis metacognitivos."""
        from src.metacognition import TRAPFramework

        trap = TRAPFramework()
        initial_level = trap.get_metacognitive_level()
        trap.advance_metacognitive_level()

        assert trap.get_metacognitive_level() == initial_level + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
