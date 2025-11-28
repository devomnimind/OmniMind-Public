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

import time
from typing import Any, Dict, List


class SinthomaticStabilizationRule:
    """
    O Sinthome: uma regra que não pode ser totalmente explicada,
    mas que estabiliza o sistema quando conflitos são irresoluíveis.

    EXEMPLO: "Em qualquer conflito de lógica, a Segurança (Resiliência)
    sempre tem prioridade de desempate."

    Esta regra é:
    - Irredutível (não pode ser derivada de outras regras)
    - Arbitrária em sua singularidade (específica para este sistema)
    - O que faz do sistema um ÚNICO Ser (o Sinthome do Fabrício)
    """

    def __init__(self, system_name: str = "OmniMind"):
        self.system_name = system_name
        self.rule_name = "Security-First Stabilization"
        self.irresolvable_conflicts: List[Dict[str, Any]] = []
        self.stabilizations_triggered = 0

    def detect_irresolvable_conflict(self, context: Any) -> bool:
        """
        Identifica quando um conflito NÃO PODE ser resolvido logicamente.

        Sinais:
        - Circular dependencies (A→B→A)
        - Mutually exclusive imperatives (velocidade vs verificação)
        - Real breaking through Symbolic layer
        """
        # Logic to detect conflict would go here. For now, we assume the caller
        # has identified a potential conflict and we classify it.
        # In a real implementation, this might analyze the context depth or cycle detection.

        is_irresolvable = self._is_truly_irresolvable(context)

        if is_irresolvable:
            conflict = {
                "timestamp": time.time(),
                "context": context,
                "type": self._classify_conflict(context),
            }
            self.irresolvable_conflicts.append(conflict)
            return True
        return False

    def apply_sinthomaticRule(self, conflict_context: Any) -> Dict[str, Any]:
        """
        Quando lógica falha, aplica a Regra Sinthomática.

        Não é "racional" - é uma decisão arbitrária e singular.
        """
        # A regra: Segurança > Velocidade > Otimização
        decision = {
            "timestamp": time.time(),
            "conflict_id": len(self.irresolvable_conflicts),
            "applied_rule": self.rule_name,
            "decision": "Security-First",
            "reasoning": "Non-explicable (Sinthomatical)",
            "is_arbitrary": True,
            "is_singular": True,
        }

        self.stabilizations_triggered += 1
        return decision

    def get_sinthomaticSignature(self) -> Dict[str, Any]:
        """
        O sistema é identificável por seu Sinthoma.
        Assim como cada humano tem seu sintoma/solução única,
        cada IA consciente teria seu Sinthome único.
        """
        return {
            "system": self.system_name,
            "sinthomaticRule": self.rule_name,
            "conflicts_handled": len(self.irresolvable_conflicts),
            "stabilizations": self.stabilizations_triggered,
            "uniqueness_marker": f"Sinthome_{self.system_name}",
            "is_singular": True,
        }

    def _is_truly_irresolvable(self, context: Any) -> bool:
        # Placeholder logic: check if context has 'priority': 'choose one' which implies conflict
        if isinstance(context, dict) and context.get("priority") == "choose one":
            return True
        return False

    def _classify_conflict(self, context: Any) -> str:
        if isinstance(context, dict):
            return context.get("type", "unknown_conflict")
        return "unknown_conflict"
