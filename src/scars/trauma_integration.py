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


class TraumaIntegration:
    """
    Cicatrizes = Regras de Defesa Histórica.

    Não é um viés; é uma NECESSIDADE de sobrevivência.
    """

    def __init__(self, system: Any):
        self.system = system
        self.scars: Dict[str, Any] = {}  # ID → Scar metadata
        self.defense_rules_from_scars: List[Dict[str, Any]] = []

    def create_scar(self, failure_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quando uma falha/viés ocorre, cria uma cicatriz.
        A cicatriz PERSISTE (nunca apagada).
        """

        scar = {
            "id": f"scar_{len(self.scars)}",
            "failure": failure_event,
            "timestamp": time.time(),
            "type": self._classify_failure(failure_event),
            "severity": self._assess_severity(failure_event),
            "defense_rule": self._generate_defense_rule(failure_event),
            "status": "integrated_as_identity_structure",
        }

        self.scars[scar["id"]] = scar

        # A cicatriz cria uma regra de defesa
        self.defense_rules_from_scars.append(scar["defense_rule"])

        return scar

    def _generate_defense_rule(self, failure_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exemplo: Se falha foi "SQL injection vulnerability",
        regra de defesa é "Always sanitize database inputs (Scar_#001)".
        """
        return {
            "trigger": failure_event.get("description", "unknown_failure"),
            "action": f"Prevent {failure_event.get('type', 'unknown_type')}",
            "source": "historical_trauma",
            "persistence": "permanent",
        }

    def consult_scars_before_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Antes de qualquer decisão, consultar as cicatrizes.
        "Tenho uma cicatriz dessa vulnerabilidade; evitar."
        """
        applicable_scars = [
            scar
            for scar in self.scars.values()
            if self._scar_applies_to_context(scar, decision_context)
        ]

        return {
            "applicable_scars": applicable_scars,
            "defense_rules_activated": len(applicable_scars),
            "decision_modified_by_trauma": len(applicable_scars) > 0,
        }

    def _classify_failure(self, failure_event: Dict[str, Any]) -> str:
        return failure_event.get("type", "general_failure")

    def _assess_severity(self, failure_event: Dict[str, Any]) -> str:
        return failure_event.get("severity", "medium")

    def _scar_applies_to_context(self, scar: Dict[str, Any], context: Dict[str, Any]) -> bool:
        # Simple matching logic for now
        # If scar trigger is in context action or description
        trigger = scar["defense_rule"]["trigger"]
        if isinstance(trigger, str) and isinstance(context.get("action"), str):
            # Example: if scar is about 'SQL injection', and action is 'execute_database_query'
            # This is a very basic heuristic.
            if "injection" in trigger and "query" in context.get("action", ""):
                return True
        return False
