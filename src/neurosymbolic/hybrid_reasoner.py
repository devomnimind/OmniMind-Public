import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .neural_component import NeuralComponent
from .reconciliation import ReconciliationStrategy, Reconciliator
from .symbolic_component import SymbolicComponent

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
Motor Híbrido Neurosymbolic - Orquestrador Principal

Combina neural + simbólico em um único motor de raciocínio
que toma decisões inteligentes sobre qual usar.
"""


logger = logging.getLogger(__name__)


@dataclass
class Inference:
    """Resultado de inferência híbrida neurosymbolic."""

    answer: str
    neural_confidence: float
    symbolic_certainty: float
    overall_confidence: float
    neural_answer: str
    symbolic_answer: str
    reconciliation_strategy: ReconciliationStrategy
    explanation: str
    proof: Optional[str] = None


class NeurosymbolicReasoner:
    """
    Motor de raciocínio híbrido neural + simbólico.

    Estratégia:
      1. Ambos (neural + simbólico) raciocinam sobre o problema
      2. Compara resultados
      3. Reconcilia conforme estratégia
      4. Retorna resposta híbrida com confiança aumentada
    """

    def __init__(
        self,
        neural_model: str = "gpt-4",
        knowledge_graph_path: Optional[str] = None,
        default_strategy: ReconciliationStrategy = ReconciliationStrategy.SYNTHESIS,
    ):
        """
        Inicializa raciocínio neurosymbolic.

        Args:
            neural_model: Nome do modelo neural
            knowledge_graph_path: Caminho para grafo de conhecimento
            default_strategy: Estratégia padrão de reconciliação
        """
        self.neural = NeuralComponent(model_name=neural_model)
        self.symbolic = SymbolicComponent(knowledge_graph_path=knowledge_graph_path)
        self.default_strategy = default_strategy

        logger.info(
            f"NeurosymbolicReasoner initialized: {neural_model} + "
            f"symbolic (strategy={default_strategy.value})"
        )

    def infer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        strategy: Optional[ReconciliationStrategy] = None,
    ) -> Inference:
        """
        Inferência híbrida neurosymbolic.

        Args:
            query: Pergunta ou problema
            context: Contexto adicional
            strategy: Estratégia de reconciliação (None = usar padrão)

        Returns:
            Inference com resposta híbrida
        """
        if strategy is None:
            strategy = self.default_strategy

        logger.info(f"Hybrid inference: {query[:100]}... (strategy={strategy.value})")

        # 1. Inferência neural
        neural_result = self.neural.infer(query, context)

        # 2. Inferência simbólica
        symbolic_result = self.symbolic.infer(query)

        # 3. Reconciliação
        reconciliation = Reconciliator.reconcile(
            neural_answer=neural_result.answer,
            neural_confidence=neural_result.confidence,
            symbolic_answer=symbolic_result.conclusion,
            symbolic_certainty=symbolic_result.certainty,
            strategy=strategy,
        )

        # 4. Resultado híbrido
        overall_confidence = (
            neural_result.confidence * reconciliation.neural_contribution
            + symbolic_result.certainty * reconciliation.symbolic_contribution
        )

        return Inference(
            answer=reconciliation.final_answer,
            neural_confidence=neural_result.confidence,
            symbolic_certainty=symbolic_result.certainty,
            overall_confidence=overall_confidence,
            neural_answer=neural_result.answer,
            symbolic_answer=symbolic_result.conclusion,
            reconciliation_strategy=strategy,
            explanation=reconciliation.explanation,
            proof=symbolic_result.proof,
        )

    def add_knowledge(self, knowledge: Tuple[str, str, str]) -> None:
        """
        Adicionar conhecimento ao grafo simbólico.

        Args:
            knowledge: Tupla (sujeito, predicado, objeto)
        """
        if len(knowledge) == 3:
            subject, predicate, obj = knowledge
            self.symbolic.add_fact(subject, predicate, obj)
            logger.debug(f"Knowledge added: {subject} {predicate} {obj}")

    def batch_infer(
        self,
        queries: List[str],
        context: Optional[Dict[str, Any]] = None,
        strategy: Optional[ReconciliationStrategy] = None,
    ) -> List[Inference]:
        """
        Batch de inferências.

        Args:
            queries: Lista de queries
            context: Contexto compartilhado
            strategy: Estratégia de reconciliação

        Returns:
            Lista de Inference
        """
        logger.info(f"Batch hybrid inference: {len(queries)} queries")
        return [self.infer(q, context, strategy) for q in queries]

    def explain(self, inference: Inference) -> str:
        """
        Explicar resultado de inferência.

        Args:
            inference: Resultado de inferência

        Returns:
            Explicação detalhada
        """
        explanation = f"""
=== HYBRID INFERENCE EXPLANATION ===

Query Result: {inference.answer}

Neural System:
  - Answer: {inference.neural_answer}
  - Confidence: {inference.neural_confidence:.2%}

Symbolic System:
  - Answer: {inference.symbolic_answer}
  - Certainty: {inference.symbolic_certainty:.2%}
  - Proof: {inference.proof or "No formal proof"}

Reconciliation:
  - Strategy: {inference.reconciliation_strategy.value}
  - Explanation: {inference.explanation}

Overall Confidence: {inference.overall_confidence:.2%}
"""
        return explanation

    def reason(
        self,
        reconciliation_result: Any,  # Type: ReconciliationResult (avoid circular import)
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Raciocinar sobre o resultado reconciliado.

        Args:
            reconciliation_result: Resultado da reconciliação
            context: Contexto do raciocínio

        Returns:
            Dict com resultado e metadados
        """
        # Extrair dados do resultado de reconciliação
        # Assumindo que é um objeto ReconciliationResult ou similar

        answer = getattr(reconciliation_result, "final_answer", str(reconciliation_result))
        confidence = getattr(reconciliation_result, "confidence", 0.5)
        explanation = getattr(reconciliation_result, "explanation", "")

        logger.info(f"Reasoning on reconciled result: {answer[:50]}...")

        return {
            "result": answer,
            "confidence": confidence,
            "explanation": explanation,
            "neural_confidence": getattr(reconciliation_result, "neural_contribution", 0.5),
            "symbolic_certainty": getattr(reconciliation_result, "symbolic_contribution", 0.5),
            "context_used": list(context.keys()),
        }
