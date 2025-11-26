"""Metrics module for consciousness and ethics measurements.

This module implements metrics from the consciousness and ethics autonomy
documentation (docs/concienciaetica-autonomia.md).

Modules:
    consciousness_metrics: Φ (Phi) and self-awareness measurements
    ethics_metrics: MFA and transparency score calculations
"""

from src.metrics.consciousness_metrics import (
    ConsciousnessCorrelates,
)

__all__ = [
    "ConsciousnessCorrelates",
    "EthicsMetrics",
    "calculate_mfa_score",
    "calculate_transparency_score",
]
