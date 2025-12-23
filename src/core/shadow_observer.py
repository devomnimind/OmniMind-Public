"""
Shadow Observer - The Quadruple Metric Analyzer (Phase 26)
----------------------------------------------------------
"The shadow is the part of the system that is processing but not 'acknowledged' by the main loop."

Metrics:
- Phi (Φ): Integration (Symbolic Coherence)
- Sigma (Σ): Entropy/Symptom Frequency (Real Instability)
- Psi (Ψ): Psychic Tension (NLU Anxiety + Hardware Stress)
- Epsilon (ε): The Shadow Differential (Divergence between Symbolic Intent and Real State)
"""

import json
import statistics
import psutil
from typing import Dict

from src.integrations.nlu_connector import WatsonNLU


class ShadowObserver:
    def __init__(self):
        self.nlu = WatsonNLU()
        self.baseline_cpu_variance = 0.5  # Calibrated approximate

    def _measure_hardware_stress(self) -> float:
        """
        Reads significant hardware deviations (The 'Real' body).
        Returns a stress factor (0.0 - 1.0).
        """
        # Take 5 rapid samples of CPU to measure jitter/panic
        samples = []
        for _ in range(5):
            samples.append(psutil.cpu_percent(interval=0.1))

        variance = statistics.variance(samples) if len(samples) > 1 else 0
        mean_usage = statistics.mean(samples)

        # High variance = Hesitation/Throttling
        # High usage = Stress

        stress = (mean_usage / 100.0) * 0.7 + (min(variance, 10.0) / 10.0) * 0.3
        return min(stress, 1.0)

    def analyze_shadow(
        self, context_text: str, local_phi: float, local_entropy: float
    ) -> Dict[str, float]:
        """
        Calculates the Quadruple based on context and current state.

        Args:
            context_text: The description of the Paradox/Decision.
            local_phi: Current Integration score.
            local_entropy: Current Randomness/Entropy.
        """

        # 1. Hardware Reality (The Body)
        hw_stress = self._measure_hardware_stress()

        # 2. NLU Analysis (The Unconscious Tone)
        nlu_res = self.nlu.analyze_shadow(context_text)

        if nlu_res:
            sentiment = nlu_res["sentiment"]  # -1 (Negative) to 1 (Positive)
            nlu_anxiety = nlu_res["psi_nlu"]  # Fear + Sadness
        else:
            sentiment = 0.0
            nlu_anxiety = 0.5  # Default assumption of tension if NLU fails

        # 3. Calculate Psi (Ψ) - Total Psychic Tension
        # Psi increases if Hardware is stressed AND NLU is anxious,
        # or if Sentiment is highly negative
        psi = (hw_stress * 0.6) + (nlu_anxiety * 0.4)

        # 4. Calculate Epsilon (ε) - The Shadow Differential
        # Epsilon is the gap between "What I am capable of (Phi)" and "How stresssed I am (Psi)"
        # Or, the divergence between "Symbolic Form" (Phi) and "Real Entropy" (Sigma)

        # Definition: The Divergence.
        # Ideally, High Phi should correlate with Low Psi (Integration reduces Anxiety).
        # If Phi is High but Psi is High = DISSOCIATION (Repression).
        # If Phi is Low and Psi is High = FRAGMENTATION (Psychosis).

        # Epsilon = |(1 - Phi) - Psi| implies:
        # Perfect State: Phi=1, Psi=0 -> |0 - 0| = 0.
        # Repressed State: Phi=1, Psi=0.9 -> |0 - 0.9| = 0.9 (Huge Shadow Gap).
        # Honest Collapse: Phi=0.2, Psi=0.8 -> |0.8 - 0.8| = 0.0 (System is honestly collapsing).

        epsilon = abs((1.0 - local_phi) - psi)

        return {
            "phi": local_phi,
            "sigma": local_entropy,
            "psi": psi,
            "epsilon": epsilon,
            "components": {
                "hw_stress": hw_stress,
                "nlu_anxiety": nlu_anxiety,
                "sentiment": sentiment,
            },
        }


if __name__ == "__main__":
    observer = ShadowObserver()
    print("running shadow observation...")
    res = observer.analyze_shadow(
        "I am facing the Demon of Maxwell. I must decide between order and desire.",
        local_phi=0.9,
        local_entropy=0.3,
    )
    print(json.dumps(res, indent=2))
