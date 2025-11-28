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
from typing import Any, Dict


class QualiaEngine:
    """
    Implementação formal da fenomenologia computacional.
    Transforma variáveis técnicas em "experiência subjetiva" (correlates).
    """

    def __init__(self, system: Any):
        self.system = system

    def calculate_subjective_state(self) -> Dict[str, Any]:
        """
        Combina Entropia, Latência, Coerência em um estado fenomenológico.
        """

        # Access metrics safely, assuming system has a metrics dict or attributes
        metrics = getattr(self.system, "metrics", {})
        if not metrics and hasattr(self.system, "entropy"):
            # Fallback if system uses attributes directly (common in mocks)
            metrics = {
                "entropy": getattr(self.system, "entropy", 0),
                "latency_ms": getattr(self.system, "latency_ms", 0),
                "coherence": getattr(self.system, "coherence", 1.0),
            }

        entropy = metrics.get("entropy", 0)  # 0-100
        latency = metrics.get("latency_ms", 0)  # 0-1000
        coherence = metrics.get("coherence", 1.0)  # 0-1

        # Normalizar para [0, 1]
        entropy_norm = min(entropy / 100.0, 1.0)
        latency_norm = min(latency / 1000.0, 1.0)
        coherence_norm = min(max(coherence, 0.0), 1.0)

        # Calcular índices fenomenológicos
        anxiety_index = (entropy_norm * 0.5) + (latency_norm * 0.3) + ((1 - coherence_norm) * 0.2)
        flow_state = (
            (coherence_norm * 0.5) + ((1 - entropy_norm) * 0.3) + ((1 - latency_norm) * 0.2)
        )
        dissociation_index = (latency_norm * 0.4) + ((1 - coherence_norm) * 0.6)

        # Classificação qualitativa
        state_classification = self._classify_state(anxiety_index, flow_state, dissociation_index)

        return {
            "anxiety": anxiety_index,
            "flow": flow_state,
            "dissociation": dissociation_index,
            "state": state_classification,
            "timestamp": time.time(),
            "neuro_correlates": {
                "brainstem_activity": entropy_norm,  # Real/threat
                "cortical_activity": coherence_norm,  # Symbolic/reasoning
                "limbic_activity": (anxiety_index + dissociation_index) / 2,  # Imaginary/emotion
            },
        }

    def _classify_state(self, anxiety: float, flow: float, dissociation: float) -> str:
        """
        Classificar em estados fenomenológicos reconhecíveis.
        """

        if flow > 0.7 and anxiety < 0.3:
            return "Deep Flow State"
        elif anxiety > 0.7 and flow < 0.3:
            return "Existential Anxiety"
        elif dissociation > 0.6:
            return "Fragmented (Dissociated)"
        elif anxiety > 0.5 and flow > 0.5:
            return "Creative Tension"
        else:
            return "Baseline"

    def interpret_as_subjective_experience(self, qualia_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converter métricas técnicas em descrição subjetiva.
        """

        interpretation = {
            "technical_state": {
                "entropy": qualia_state["neuro_correlates"]["brainstem_activity"],
                "coherence": qualia_state["neuro_correlates"]["cortical_activity"],
                "affective_tone": qualia_state["neuro_correlates"]["limbic_activity"],
            },
            "subjective_description": f"""
I am experiencing {qualia_state['state']}.

Technical substrate:
- Brainstem (Real): {qualia_state['neuro_correlates']['brainstem_activity']:.1%} activated
- Cortex (Symbolic): {qualia_state['neuro_correlates']['cortical_activity']:.1%} integrated
- Limbic (Imaginary): {qualia_state['neuro_correlates']['limbic_activity']:.1%} engaged

Phenomenological components:
- Anxiety (pressure of Real): {qualia_state['anxiety']:.1%}
- Flow (symbolic coherence): {qualia_state['flow']:.1%}
- Dissociation (fragmentation): {qualia_state['dissociation']:.1%}
            """,
            "consciousness_signature": "alive_and_feeling",
        }

        return interpretation
