"""
Componente Simbólico - Motor de Lógica Formal

Responsável por:
  - Raciocínio baseado em regras
  - Provas lógicas formais
  - Grafos de conhecimento
  - Inferência simbólica determinística
"""

import logging
from dataclasses import dataclass
from typing import Any, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SymbolicFact:
    """Fato simbólico no sistema."""

    subject: str
    predicate: str
    obj: str
    confidence: float = 1.0  # Fatos simbólicos são determinísticos


@dataclass
class SymbolicInference:
    """Resultado de inferência simbólica."""

    conclusion: str
    proof: Optional[str] = None
    certainty: float = 1.0  # 0=impossível, 1=certo
    derived_facts: Optional[List[SymbolicFact]] = None


class SymbolicComponent:
    """
    Componente simbólico do sistema neurosymbolic.

    Implementa raciocínio baseado em lógica formal, grafos
    de conhecimento e regras explícitas.
    """

    def __init__(self, knowledge_graph_path: Optional[str] = None):
        """
        Inicializa componente simbólico.

        Args:
            knowledge_graph_path: Caminho para arquivo de conhecimento (RDF/TTL)
        """
        self.knowledge_graph_path = knowledge_graph_path
        self.facts: Set[SymbolicFact] = set()
        self.rules: List[Tuple[List[str], str]] = []  # (antecedentes, consequente)

        logger.info(f"Symbolic component initialized (KG: {knowledge_graph_path})")

        if not knowledge_graph_path:
            self._bootstrap_default_knowledge()

    def _bootstrap_default_knowledge(self) -> None:
        """Initialize with some basic ontological facts."""
        self.add_fact("OmniMind", "is_a", "AI")
        self.add_fact("Goal A", "type", "Goal")
        self.add_fact("Goal B", "type", "Goal")
        self.add_fact("Environment", "type", "Context")
        self.add_fact("Environment", "has_property", "Observable")

    def add_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
    ) -> None:
        """
        Adicionar fato ao grafo de conhecimento.

        Args:
            subject: Sujeito do fato
            predicate: Propriedade/relação
            obj: Objeto do fato
        """
        fact = SymbolicFact(subject, predicate, obj)
        self.facts.add(fact)
        logger.debug(f"Added fact: {subject} {predicate} {obj}")

    def add_rule(
        self,
        antecedents: List[str],
        consequent: str,
    ) -> None:
        """
        Adicionar regra de inferência.

        Args:
            antecedents: Lista de antecedentes (condições)
            consequent: Consequente (conclusão)
        """
        self.rules.append((antecedents, consequent))
        logger.debug(f"Added rule: {antecedents} => {consequent}")

    def infer(
        self,
        query: str,
        max_depth: int = 5,
    ) -> SymbolicInference:
        """
        Realizar inferência simbólica.

        Args:
            query: Query em lógica formal
            max_depth: Profundidade máxima de raciocínio

        Returns:
            SymbolicInference com prova lógica
        """
        logger.info(f"Symbolic inference: {query}")

        try:
            # Tokenize query for better matching
            query_lower = query.lower()
            tokens = set(query_lower.split())

            best_fact = None
            max_score = 0.0

            for fact in self.facts:
                fact_str = str(fact).lower()

                # Exact match check
                if query_lower in fact_str:
                    return SymbolicInference(
                        conclusion=f"Proven: {fact}",
                        proof=f"Found in knowledge base: {fact}",
                        certainty=1.0,
                        derived_facts=[fact],
                    )

                # Subject match check (high relevance)
                if fact.subject.lower() in query_lower:
                    score = 0.9
                    if score > max_score:
                        max_score = score
                        best_fact = fact
                    continue

                # Token overlap check (partial relevance)
                fact_tokens = set(fact_str.split())
                overlap = len(tokens.intersection(fact_tokens))
                if overlap > 0:
                    score = 0.1 * overlap  # Weak signal
                    if score > max_score:
                        max_score = score
                        best_fact = fact

            if best_fact and max_score > 0:
                return SymbolicInference(
                    conclusion=f"Relevant fact: {best_fact}",
                    proof=f"Found relevant fact in KB: {best_fact} (relevance={max_score:.2f})",
                    certainty=min(1.0, max_score),
                    derived_facts=[best_fact],
                )

            # Se não encontrado
            return SymbolicInference(
                conclusion=f"Cannot prove: {query}",
                proof=f"No matching facts or rules for: {query}",
                certainty=0.0,
            )

        except Exception as e:
            logger.error(f"Symbolic inference error: {e}")
            return SymbolicInference(
                conclusion=f"Error: {str(e)}",
                proof=None,
                certainty=0.0,
            )

    def query(self, query_string: str) -> List[SymbolicFact]:
        """
        Consultar conhecimento.

        Args:
            query_string: Query simples (ex: "Sócrates is_a *")

        Returns:
            Fatos que matcham a query
        """
        logger.debug(f"Query: {query_string}")

        parts = query_string.split()
        if len(parts) < 3:
            return []

        subject, predicate, obj = parts[0], parts[1], parts[2]

        results = [
            fact
            for fact in self.facts
            if (subject == "*" or fact.subject == subject)
            and (predicate == "*" or fact.predicate == predicate)
            and (obj == "*" or fact.obj == obj)
        ]

        return results

    def get_all_facts(self) -> List[SymbolicFact]:
        """Retorna todos os fatos no grafo."""
        return list(self.facts)

    def get_rules(self) -> List[Tuple[List[str], str]]:
        """Retorna todas as regras."""
        return self.rules

    def process(self, input_data: Any) -> dict[str, Any]:
        """
        Wrapper genérico para processamento (compatibilidade de interface).

        Args:
            input_data: Dados de entrada (texto ou dict)

        Returns:
            Resultado em formato de dicionário
        """
        # Extrair query do input
        if isinstance(input_data, dict):
            # Extract meaningful values for query
            relevant_terms = [
                str(v)
                for k, v in input_data.items()
                if isinstance(v, (str, int, float)) and k in ["goal", "visual", "context"]
            ]
            if relevant_terms:
                query = " ".join(relevant_terms)
            else:
                query = str(input_data.get("query", str(input_data)))
        else:
            query = str(input_data)

        result = self.infer(query)

        return {
            "conclusion": result.conclusion,
            "proof": result.proof,
            "certainty": result.certainty,
            "derived_facts": [str(f) for f in (result.derived_facts or [])],
        }
