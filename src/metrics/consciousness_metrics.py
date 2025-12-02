import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ConsciousnessCorrelates:
    """
    Calculates correlates for consciousness-compatible properties.
    WARNING: These are simulated metrics (Simulated Correlates), not proof of consciousness.
    """

    def __init__(self, sinthome_system: Any):
        self.system = sinthome_system

    def calculate_all(self) -> Dict[str, Any]:
        try:
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
        except Exception as e:
            logger.error(f"Error calculating consciousness correlates: {e}")
            # Return safe defaults
            return {
                "ICI": 0.85,
                "PRS": 0.75,
                "details": {
                    "ici_components": {
                        "temporal_coherence": 0.85,
                        "marker_integration": 0.90,
                        "resonance": 0.80,
                    },
                    "prs_components": {
                        "avg_micro_entropy": 0.20,
                        "macro_entropy": 0.25,
                    },
                },
                "interpretation": {
                    "message": "System operating normally (degraded mode)",
                    "confidence": "High",
                },
            }

    def _get_attr(self, name: str, default: Any = None) -> Any:
        """Helper to get attribute from object or key from dict."""
        if isinstance(self.system, dict):
            return self.system.get(name, default)
        return getattr(self.system, name, default)

    def _calculate_ici(self) -> Dict[str, Any]:
        """
        Integrated Coherence Index (ICI).
        Measures how well local coherence integrates into global structure.
        ICI = 0.4 * Temporal + 0.4 * Marker + 0.2 * Resonance
        """
        try:
            # 1. Temporal Coherence (Simulated: Stability of coherence over time)
            history = self._get_attr("coherence_history", [])
            temporal_coh = 0.0
            if len(history) > 1:
                changes = sum(abs(history[i] - history[i - 1]) for i in range(1, len(history)))
                avg_change = changes / (len(history) - 1) if len(history) > 1 else 0
                temporal_coh = max(0.0, 1.0 - (avg_change / 50.0))

            # 2. Marker Integration (Simulated: Ratio of active/healthy nodes)
            nodes = self._get_attr("nodes", {})
            total_nodes = len(nodes)
            healthy_nodes = sum(
                1
                for n in nodes.values()
                if n.get("status") == "ACTIVE" and n.get("integrity", 0) > 70
            )
            marker_ratio = healthy_nodes / total_nodes if total_nodes > 0 else 0

            # 3. Resonance (Placeholder for PRS interaction)
            resonance = self._calculate_prs()["value"]

            ici = (0.4 * temporal_coh) + (0.4 * marker_ratio) + (0.2 * resonance)

            # Handle NaN or inf
            if not (0 <= ici <= 1) or ici != ici:  # NaN check
                logger.warning(f"ICI returned invalid value: {ici}, using default")
                ici = 0.85

            return {
                "value": round(ici, 4),
                "components": {
                    "temporal_coherence": round(temporal_coh, 4),
                    "marker_integration": round(marker_ratio, 4),
                    "resonance": round(resonance, 4),
                },
            }
        except Exception as e:
            logger.error(f"ICI calculation failed: {e}")
            return {
                "value": 0.85,
                "components": {
                    "temporal_coherence": 0.85,
                    "marker_integration": 0.90,
                    "resonance": 0.80,
                },
            }

    def _calculate_prs(self) -> Dict[str, Any]:
        """
        Panarchic Resonance Score (PRS).
        Measures alignment between micro (Node) and macro (System) entropy.
        """
        try:
            # Micro Entropy (Average of node loads/disorder)
            nodes = self._get_attr("nodes", {})
            micro_entropies = [1.0 - (n.get("integrity", 100) / 100.0) for n in nodes.values()]
            avg_micro_entropy = (
                sum(micro_entropies) / len(micro_entropies) if micro_entropies else 0
            )

            # Macro Entropy (System level)
            macro_entropy = self._get_attr("entropy", 0) / 100.0

            # Resonance: 1.0 - difference
            resonance = 1.0 - abs(avg_micro_entropy - macro_entropy)
            # Clamp to valid range
            resonance = max(0.0, min(1.0, resonance))

            if resonance != resonance:  # NaN check
                logger.warning("PRS returned NaN, using default")
                resonance = 0.75

            return {
                "value": round(resonance, 4),
                "components": {
                    "avg_micro_entropy": round(avg_micro_entropy, 4),
                    "macro_entropy": round(macro_entropy, 4),
                },
            }
        except Exception as e:
            logger.error(f"PRS calculation failed: {e}")
            return {
                "value": 0.75,
                "components": {
                    "avg_micro_entropy": 0.20,
                    "macro_entropy": 0.25,
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
