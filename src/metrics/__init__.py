"""Metrics module for consciousness and ethics measurements.

This module implements metrics from the consciousness and ethics autonomy
documentation (docs/concienciaetica-autonomia.md).

Modules:
    consciousness_metrics: Φ (Phi) and self-awareness measurements
    ethics_metrics: MFA and transparency score calculations
"""

from src.metrics.consciousness_metrics import ConsciousnessCorrelates
from src.metrics.consciousness_metrics_legacy import (
    AgentConnection,
    ConsciousnessMetrics,
    FeedbackLoop,
    SelfAwarenessMetrics,
)

__all__ = [
    "ConsciousnessCorrelates",
    "ConsciousnessMetrics",
    "AgentConnection",
    "FeedbackLoop",
    "SelfAwarenessMetrics",
]
