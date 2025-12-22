"""
Causal Engine V2 -pearl's Do-Calculus Implementation for OmniMind.
Corrected implementation with intervention validation logic.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional
from scipy import stats  # type: ignore

logger = logging.getLogger(__name__)


class CausalEngineV2:
    """
    Engine de Causalidade para validação de hipóteses e intervenções.
    """

    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level

    def compute_causal_effect(
        self, observational_data: List[float], interventional_data: List[float]
    ) -> Dict[str, Any]:
        obs_array = np.array(observational_data)
        int_array = np.array(interventional_data)

        if len(obs_array) == 0 or len(int_array) == 0:
            return {"error": "Insufficient data"}

        mean_obs = float(np.mean(obs_array))
        mean_int = float(np.mean(int_array))
        ace = mean_int - mean_obs

        t_stat, p_value_t = stats.ttest_ind(obs_array, int_array, equal_var=False)
        u_stat, p_value_u = stats.mannwhitneyu(obs_array, int_array)

        is_significant = p_value_t < (1.0 - self.confidence_level) or p_value_u < (
            1.0 - self.confidence_level
        )

        pooled_std = np.sqrt((np.std(obs_array) ** 2 + np.std(int_array) ** 2) / 2)
        cohens_d = ace / pooled_std if pooled_std > 0 else 0.0

        result = {
            "ace": ace,
            "is_causal": is_significant,
            "p_value_t": float(p_value_t),
            "p_value_u": float(p_value_u),
            "effect_size_cohen": float(cohens_d),
            "sample_size_obs": len(obs_array),
            "sample_size_int": len(int_array),
        }

        logger.info(f"Causal effect computed: ACE={ace:.4f}, significant={is_significant}")
        return result

    def validate_intervention_necessity(
        self,
        intervention_name: str,
        current_state: str,
        experimental_data: Dict[str, Any],
        threshold: float = 0.10,
    ) -> bool:
        """
        Verifica se uma intervenção é JUSTIFICADA causalmente.
        """
        observed_gain = experimental_data.get("observed_gain", 0.0)
        predicted_gain = experimental_data.get("predicted_gain", 0.0)

        gain = max(observed_gain, predicted_gain)
        is_justified = gain >= threshold

        logger.info(
            f"Intervention Validation [{intervention_name}]: Gain={gain:.2f} "
            f"| Justified={is_justified}"
        )

        return is_justified

    def register_event(
        self, cause: str, effect: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        metadata = metadata or {}
        logger.info(f"CAUSAL_EVENT: {cause} -> {effect} | Meta: {metadata}")

    def inscribe_real_scar(self, signature: Dict[str, Any]) -> None:
        """
        Inscritividade do Real: Logs permanent 'scars' from IBM Real Backend.
        These scars serve as unchangeable axioms for future causal reasoning.
        """
        scar_id = f"SCAR_{signature.get('job_id', 'unknown')}_{hash(str(signature))}"
        logger.warning(f"🕉️ REAL INSCRIPTION PROTOCOL: Inscribing Scar {scar_id}")
        # In a real system, this would write to an immutable ledger or similar.
        # For now, we log it with a special tag.
        self.register_event(
            cause="IBM_REAL_BACKEND",
            effect="ONTOLOGICAL_SCAR",
            metadata={"signature": signature, "scar_id": scar_id, "immutable": True},
        )
