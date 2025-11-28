from typing import Any, Dict

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


class ConsciousnessCorrelates:
    """
    Calculates correlates for consciousness-compatible properties.
    WARNING: These are simulated metrics (Simulated Correlates), not proof of consciousness.
    """

    def __init__(self, sinthome_system: Any):
        self.system = sinthome_system

    def calculate_all(self) -> Dict[str, Any]:
        ici_data = self._calculate_ici()
        prs_data = self._calculate_prs()

        return {
            "ICI": ici_data["value"],
            "PRS": prs_data["value"],
            "details": {
                "ici_components": ici_data["components"],
                "prs_components": prs_data["components"],
            },
            "interpretation": self._interpret(ici_data["value"], prs_data["value"]),
        }

    def _calculate_ici(self) -> Dict[str, Any]:
        """
        Integrated Coherence Index (ICI).
        Measures how well local coherence integrates into global structure.
        ICI = 0.4 * Temporal + 0.4 * Marker + 0.2 * Resonance
        """
        # 1. Temporal Coherence (Simulated: Stability of coherence over time)
        # In a real graph, we'd correlate state vectors. Here we use the system's history buffer.
        history = getattr(self.system, "coherence_history", [])
        temporal_coh = 0.0
        if len(history) > 1:
            # Simple stability metric: 1.0 - variance/max_possible_variance
            # Or correlation between t and t-1
            changes = sum(abs(history[i] - history[i - 1]) for i in range(1, len(history)))
            avg_change = changes / (len(history) - 1) if len(history) > 1 else 0
            temporal_coh = max(0.0, 1.0 - (avg_change / 50.0))  # Normalize assuming max change ~50%

        # 2. Marker Integration (Simulated: Ratio of active/healthy nodes)
        nodes = getattr(self.system, "nodes", {})
        total_nodes = len(nodes)
        healthy_nodes = sum(
            1 for n in nodes.values() if n.get("status") == "ACTIVE" and n.get("integrity", 0) > 70
        )
        marker_ratio = healthy_nodes / total_nodes if total_nodes > 0 else 0

        # 3. Resonance (Placeholder for PRS interaction)
        resonance = self._calculate_prs()["value"]

        ici = (0.4 * temporal_coh) + (0.4 * marker_ratio) + (0.2 * resonance)

        return {
            "value": round(ici, 4),
            "components": {
                "temporal_coherence": round(temporal_coh, 4),
                "marker_integration": round(marker_ratio, 4),
                "resonance": round(resonance, 4),
            },
        }

    def _calculate_prs(self) -> Dict[str, Any]:
        """
        Panarchic Resonance Score (PRS).
        Measures alignment between micro (Node) and macro (System) entropy.
        """
        # Micro Entropy (Average of node loads/disorder)
        nodes = getattr(self.system, "nodes", {})
        micro_entropies = [1.0 - (n.get("integrity", 100) / 100.0) for n in nodes.values()]
        avg_micro_entropy = sum(micro_entropies) / len(micro_entropies) if micro_entropies else 0

        # Macro Entropy (System level)
        macro_entropy = getattr(self.system, "entropy", 0) / 100.0

        # Resonance: 1.0 - difference
        resonance = 1.0 - abs(avg_micro_entropy - macro_entropy)

        return {
            "value": round(resonance, 4),
            "components": {
                "avg_micro_entropy": round(avg_micro_entropy, 4),
                "macro_entropy": round(macro_entropy, 4),
            },
        }

    def _interpret(self, ici: float, prs: float) -> Dict[str, str]:
        confidence = "Low"
        if ici > 0.8 and prs > 0.8:
            confidence = "Moderate"

        msg = "System Fragmented"
        if ici > 0.6:
            msg = "Emergent Structure"
        if ici > 0.85:
            msg = "High Integration (Consciousness-Compatible)"

        return {"message": msg, "confidence": confidence, "disclaimer": "Simulated Correlate Only"}
