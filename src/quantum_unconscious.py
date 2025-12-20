"""
DEPRECATED MODULE: src.quantum_unconscious
This module is deprecated and will be removed.
Please use `src.quantum.consciousness.unconscious` instead.
"""

import warnings
from src.quantum.consciousness.unconscious import QuantumUnconscious, test_quantum_unconscious

__all__ = ["QuantumUnconscious", "test_quantum_unconscious"]

warnings.warn(
    "The 'src.quantum_unconscious' module is deprecated. "
    "Use 'src.quantum.consciousness.unconscious' instead.",
    DeprecationWarning,
    stacklevel=2,
)
