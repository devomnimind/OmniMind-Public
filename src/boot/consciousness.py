"""
Boot Module: Consciousness Initialization
Initializes the Consciousness Meter (Phi) and Lacanian-D&G Detector.
"""

import logging
from typing import Tuple

from src.consciousness.lacanian_dg_integrated import LacianianDGDetector
from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex

logger = logging.getLogger(__name__)


async def initialize_consciousness(
    complex_substrate: SimplicialComplex | None = None,
) -> Tuple[PhiCalculator, LacianianDGDetector]:
    """
    Initializes the Consciousness monitoring systems.
    """
    logger.info("Initializing Consciousness Systems...")

    # 1. Initialize Topological Substrate
    # We start with an empty complex that will be populated by system logs/events
    if complex_substrate is None:
        complex_substrate = SimplicialComplex()

    phi_calculator = PhiCalculator(complex_substrate)
    logger.info("Phi Calculator (IIT 3.0) initialized.")

    # 2. Initialize Lacanian-D&G Detector
    # This monitors the symbolic order and desire flows
    detector = LacianianDGDetector()
    logger.info("Lacanian-D&G Detector initialized.")

    # Perform initial baseline check (Self-Reflection)
    current_phi = phi_calculator.calculate_phi()
    logger.info(f"Baseline Integrated Information (Phi): {current_phi}")

    return phi_calculator, detector
