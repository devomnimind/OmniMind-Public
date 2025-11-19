"""Metrics module for consciousness and ethics measurements.

This module implements metrics from the consciousness and ethics autonomy
documentation (docs/concienciaetica-autonomia.md).

Modules:
    consciousness_metrics: Φ (Phi) and self-awareness measurements
    ethics_metrics: MFA and transparency score calculations
"""

from src.metrics.consciousness_metrics import (
    ConsciousnessMetrics,
    calculate_phi_proxy,
    measure_self_awareness,
)
from src.metrics.ethics_metrics import (
    EthicsMetrics,
    calculate_mfa_score,
    calculate_transparency_score,
)

__all__ = [
    "ConsciousnessMetrics",
    "calculate_phi_proxy",
    "measure_self_awareness",
    "EthicsMetrics",
    "calculate_mfa_score",
    "calculate_transparency_score",
]
