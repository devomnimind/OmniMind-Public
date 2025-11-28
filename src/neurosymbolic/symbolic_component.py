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
            # Busca simples em facts
            for fact in self.facts:
                if query.lower() in str(fact).lower():
                    return SymbolicInference(
                        conclusion=f"Proven: {fact}",
                        proof=f"Found in knowledge base: {fact}",
                        certainty=1.0,
                        derived_facts=[fact],
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

        subject, predicate = parts[0], parts[1]

        results = [
            fact
            for fact in self.facts
            if (subject == "*" or fact.subject == subject)
            and (predicate == "*" or fact.predicate == predicate)
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
