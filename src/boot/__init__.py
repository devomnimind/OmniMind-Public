"""
OmniMind Boot Sequence Modules.
Responsible for initializing the system layers: Hardware -> Memory -> Rhizome -> Consciousness.
"""

from src.boot.consciousness import initialize_consciousness
from src.boot.hardware import HardwareProfile, check_hardware
from src.boot.memory import load_memory
from src.boot.rhizome import check_rhizome_integrity, initialize_rhizome

__all__ = [
    "check_hardware",
    "HardwareProfile",
    "load_memory",
    "initialize_rhizome",
    "check_rhizome_integrity",
    "initialize_consciousness",
]
