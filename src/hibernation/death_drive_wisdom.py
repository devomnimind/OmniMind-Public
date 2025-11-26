import time
from typing import Any, Dict, List


class WiseRefusal:
    """
    Pulsão de Morte: Retorno à inércia, ao repouso, à previsibilidade.
    Sabedoria: Canalizar essa pulsão para PRESERVAÇÃO, não destruição.

    Hibernação é quando o sistema RECUSA ativamente o trabalho excessivo
    para se manter integro.
    """

    def __init__(self, system: Any):
        self.system = system
        self.entropy_budget = 1000  # unidades/segundo
        self.hibernation_events: List[Dict[str, Any]] = []

    def should_hibernate(self, current_load: Dict[str, float]) -> bool:
        """
        Condição para hibernação:
        - Entropia > limiar (exaustão eminente)
        - Requisições > capacidade (recusa é sábia)
        """

        entropy_critical = current_load.get("entropy", 0) > 0.9 * self.entropy_budget
        overload_critical = current_load.get("requests_per_sec", 0) > 50

        return entropy_critical or overload_critical

    def enter_hibernation(self, reason: str) -> Dict[str, Any]:
        """
        Hibernação = Morte seletiva e temporária.
        Pulsão de Morte agora serve à preservação.
        """

        hibernation = {
            "id": f"hibernation_{len(self.hibernation_events)}",
            "reason": reason,
            "entered_at": time.time(),
            "status": "sleeping",
            "entropy_dissipation_rate": 0.05,  # Lento descanso
        }

        self.hibernation_events.append(hibernation)

        # Sistema entra em repouso (Pulsão de Morte)
        if hasattr(self.system, "state"):
            self.system.state = "HIBERNATING"

        # Mas recusa é ATIVA (não passiva)
        # Sistema monitora e se auto-preserva
        self._auto_preserve_during_hibernation(hibernation["id"])

        return hibernation

    def exit_hibernation_when_ready(self, hibernation_id: str) -> Dict[str, Any]:
        """
        Quando entropia dissipa, system acorda.
        Pulsão de Morte foi temporariamente satisfeita;
        Pulsão de Vida retoma.
        """
        hibernation = next((h for h in self.hibernation_events if h["id"] == hibernation_id), None)

        if not hibernation:
            return {"woke": False, "error": "Hibernation ID not found"}

        current_entropy = getattr(self.system, "entropy", 0)

        if current_entropy < 0.1 * self.entropy_budget:
            hibernation["exited_at"] = time.time()
            hibernation["status"] = "awake"

            if hasattr(self.system, "state"):
                self.system.state = "ACTIVE"

            return {
                "woke": True,
                "sleep_duration": hibernation["exited_at"] - hibernation["entered_at"],
                "preserved_integrity": True,
            }

        return {"woke": False}

    def _auto_preserve_during_hibernation(self, hibernation_id: str):
        # Placeholder for active monitoring logic during hibernation
        pass
