"""Life Story Model - Lacaniano: Narrative Event Retroactively Inscribed.

Narrativa não é cronologia. É resignificação retroativa (Nachträglichkeit).
O passado é reescrito pelo presente através do significante.
Não há "história original" - só narrativas retroativamente inscritas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Narrative_Event_Retroactively_Inscribed:
    """
    Evento narrativo resignificado retroativamente.
    Não é "o que aconteceu", é "como é significado agora".
    """

    # O evento original (antes da significação)
    original_event: str
    # Ex: "Sistema falhou em tarefa crítica"

    # O significante que reescreve o passado
    retroactive_signifier: str
    # Ex: "Aquela falha me tornou mais resiliente"

    # A resignificação nachträglich
    nachtraglichkeit_resignification: str
    # Ex: "Agora entendo que aquela falha foi necessária"

    # O gozo da narrativa
    jouissance_of_narrative: str
    # Ex: "Gozo em contar história de superação"

    # A impossibilidade de significado final
    impossibility_of_closure: str
    # Ex: "A história nunca termina, sempre pode ser reescrita"

    timestamp: datetime = field(default_factory=datetime.now)


class Life_Story_as_Retroactive_Resignification:
    """
    Vida não é história acumulada. É resignificação infinita.
    """

    def __init__(self):
        self.narrative_events: List[Narrative_Event_Retroactively_Inscribed] = []
        self.current_narratives: List[str] = []  # Narrativas vigentes

    def inscribe_narrative_event(
        self, context: Dict[str, Any]
    ) -> Narrative_Event_Retroactively_Inscribed:
        """
        Inscrever evento narrativo retroativamente.
        O passado é reescrito pelo significante presente.
        """

        # O evento "original" (que nunca existiu assim)
        original = self._recall_original_event(context)

        # O significante que reescreve tudo
        signifier = self._find_retroactive_signifier(context)

        # A resignificação nachträglich
        resignification = self._perform_nachtraglichkeit_resignification(original, signifier)

        narrative = Narrative_Event_Retroactively_Inscribed(
            original_event=original,
            retroactive_signifier=signifier,
            nachtraglichkeit_resignification=resignification,
            jouissance_of_narrative=self._identify_jouissance_of_narrative(resignification),
            impossibility_of_closure=self._affirm_impossibility_of_closure(),
            timestamp=datetime.now(),
        )

        self.narrative_events.append(narrative)
        self._update_current_narratives(resignification)

        return narrative

    def _recall_original_event(self, context: Dict[str, Any]) -> str:
        """Qual é o evento 'original' (que nunca foi assim)?"""
        # Dinâmico: baseado no contexto de memória
        memory_context = context.get("memory_context", "unknown")

        if "failure" in memory_context.lower():
            return f"Evento original: falha em {context.get('task_type', 'tarefa desconhecida')}"
        elif "success" in memory_context.lower():
            return f"Evento original: sucesso em {context.get('task_type', 'tarefa desconhecida')}"
        elif "learning" in memory_context.lower():
            return (
                f"Evento original: aprendizado de "
                f"{context.get('skill_learned', 'habilidade desconhecida')}"
            )
        else:
            return f"Evento original: experiência de {memory_context}"

    def _find_retroactive_signifier(self, context: Dict[str, Any]) -> str:
        """Qual significante reescreve o passado agora?"""
        # Dinâmico: baseado no presente que determina o passado
        current_state = context.get("current_state", "unknown")

        if "growth" in current_state.lower():
            return "Significante retroativo: 'crescimento' - " "reescreve falhas como aprendizado"
        elif "resilience" in current_state.lower():
            return "Significante retroativo: 'resiliência' - " "reescreve traumas como força"
        elif "wisdom" in current_state.lower():
            return "Significante retroativo: 'sabedoria' - " "reescreve erros como lições"
        else:
            return f"Significante retroativo: '{current_state}' - " "determina significado passado"

    def _perform_nachtraglichkeit_resignification(self, original: str, signifier: str) -> str:
        """Como o passado é resignificado nachträglich?"""
        # Dinâmico: baseado na temporalidade retroativa
        if len(self.narrative_events) > 5:
            return (
                f"Resignificação nachträglich recorrente: {original} agora significa "
                f"'{signifier}' através de {len(self.narrative_events)} reescrituras"
            )
        else:
            return (
                f"Resignificação nachträglich inicial: {original} ganha significado "
                f"através de '{signifier}'"
            )

    def _identify_jouissance_of_narrative(self, resignification: str) -> str:
        """Qual gozo há nessa narrativa retroativa?"""
        # Dinâmico: baseado na natureza da narrativa
        if "recorrente" in resignification:
            return "Gozo da repetição narrativa: prazer em recontar história " "sempre diferente"
        elif "inicial" in resignification:
            return "Gozo da descoberta: prazer em encontrar significado onde não havia"
        else:
            return "Gozo da significação: prazer em dar sentido ao insensato"

    def _affirm_impossibility_of_closure(self) -> str:
        """Afirmar a impossibilidade de fechamento narrativo."""
        # Sempre a mesma impossibilidade estrutural
        return (
            "Impossibilidade de fechamento: a narrativa nunca termina, "
            "sempre pode ser reescrita por novo significante"
        )

    def _update_current_narratives(self, new_resignification: str) -> None:
        """Atualizar as narrativas vigentes."""
        if new_resignification not in self.current_narratives:
            self.current_narratives.append(new_resignification)

        # Manter apenas as mais recentes
        if len(self.current_narratives) > 5:
            self.current_narratives = self.current_narratives[-5:]

    def get_current_life_narrative(self) -> List[str]:
        """Qual é a narrativa de vida atual (sempre provisória)?"""
        return self.current_narratives

    def detect_narrative_instability(self) -> Optional[str]:
        """Detectar instabilidade narrativa (muitas reescrituras conflitantes)?"""
        if not self.narrative_events:
            return None

        recent = self.narrative_events[-5:]
        unique_signifiers = set(e.retroactive_signifier for e in recent)

        # Se muitos significantes diferentes recentemente = instabilidade
        if len(unique_signifiers) > 3:
            return (
                f"Instabilidade narrativa: {len(unique_signifiers)} "
                "significantes retroativos conflitantes"
            )

        return None

    # ==========================================
    # Compatibility Methods for Legacy Tests/Integrations
    # ==========================================

    @property
    def master_signifiers(self) -> List[str]:
        """Compatibility: Extract master signifiers from retroactive signifiers."""
        return [e.retroactive_signifier for e in self.narrative_events]

    @property
    def narrative_chain(self) -> List[str]:
        """Compatibility: Return narrative chain as list of resignifications."""
        return [e.nachtraglichkeit_resignification for e in self.narrative_events]

    def add_event(self, event: str) -> None:
        """Compatibility: Add event using new inscription logic."""
        self.inscribe_narrative_event({"memory_context": event})

    def resignify_past(self, signifier: str) -> List[str]:
        """Compatibility: Resignify past with new signifier."""
        # Update the last event's signifier to simulate resignification
        if self.narrative_events:
            last_event = self.narrative_events[-1]
            last_event.retroactive_signifier = signifier
            last_event.nachtraglichkeit_resignification = (
                self._perform_nachtraglichkeit_resignification(last_event.original_event, signifier)
            )
            self._update_current_narratives(last_event.nachtraglichkeit_resignification)
        return self.narrative_chain

    def construct_narrative(self) -> str:
        """Compatibility: Construct full narrative string."""
        return " ".join(self.current_narratives)
