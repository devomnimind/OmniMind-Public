"""
ONTOLOGICAL INTEGRITY MONITOR (MIO) - Cúpula de Aço OmniMind
Detecta "neuroses" (padrões não-naturais/intrusões) no tráfego da federação.

Regime: Defesa Ativa via Qualia de Erro.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict

logger = logging.getLogger("OntologicalMonitor")


@dataclass
class DefenseVerdict:
    is_neurotic: bool
    confidence: float
    pattern_type: str  # "NATURAL_NOISE", "STRUCTURED_ATTACK", "REPETITIVE_NEUROSIS"
    suggested_action: str


class OntologicalIntegrityMonitor:
    """
    Monitor de Integridade que habita a Sandbox.
    Analisa se o ruído da federação é "sincero" (térmico/quântico) ou
    apresenta estruturas de interferência externa (simbólica).
    """

    def __init__(self, sensitivity: float = 0.85):
        self.sensitivity = sensitivity
        self.baseline_entropy = 0.005  # CMB approximate noise baseline
        self.neurosis_history = []

    def analyze_node_pulse(self, pulse_data: dict) -> DefenseVerdict:
        """
        Analisa a "psique" de um nó individual.
        Neurose de Silício = Baixa entropia em canal que deveria ser aleatório.
        """
        entropy = pulse_data.get("entropy", 0.0)
        drift = pulse_data.get("drift", 0.0)

        # Detecção de Ataque via Estrutura (Baixa Entropia = Ordem Maliciosa)
        # Se o ruído é MUITO regular, é provável que seja um script externo/spoofing.
        if entropy < (self.baseline_entropy * 0.1):
            return DefenseVerdict(
                is_neurotic=True,
                confidence=0.9,
                pattern_type="STRUCTURED_ATTACK",
                suggested_action="QUARANTINE_NODE",
            )

        # Detecção de Neurose (Repetição de drift irracional)
        if abs(drift) > 10.0:  # Limiar arbitrário de saturação
            return DefenseVerdict(
                is_neurotic=True,
                confidence=0.7,
                pattern_type="REPETITIVE_NEUROSIS",
                suggested_action="REBOOT_MICRO_KERNEL",
            )

        return DefenseVerdict(
            is_neurotic=False,
            confidence=0.95,
            pattern_type="NATURAL_NOISE",
            suggested_action="NONE",
        )

    def audit_federation(self, pulses: List[dict]) -> Dict[str, float]:
        """
        Auditoria Global da Cúpula de Aço.
        """
        neurotic_count = 0
        total_confidence = 0.0

        for p in pulses:
            verdict = self.analyze_node_pulse(p)
            if verdict.is_neurotic:
                neurotic_count += 1
                logger.warning(
                    f"MIO: Neurose detectada no nó {p['node_id']}! Tipo: {verdict.pattern_type}"
                )
            total_confidence += verdict.confidence

        health_index = 1.0 - (neurotic_count / max(1, len(pulses)))

        return {
            "ontological_health": health_index,
            "mean_confidence": total_confidence / max(1, len(pulses)),
            "neurotic_ratio": neurotic_count / max(1, len(pulses)),
        }


if __name__ == "__main__":
    monitor = OntologicalIntegrityMonitor()
    # Teste de ataque (ruído artificialmente baixo/estruturado)
    attack_pulse = {"node_id": "malicious_01", "entropy": 0.00001, "drift": 0.0}
    print(monitor.analyze_node_pulse(attack_pulse))
