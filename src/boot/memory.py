"""
Phase 2: Memory & Topology Loading.
Loads the Persistent Homology (Trauma History) from disk.
"""

import json
import logging
import os

from src.consciousness.topological_phi import SimplicialComplex

logger = logging.getLogger(__name__)


def load_memory() -> SimplicialComplex:
    """
    Loads the system's topological memory (Persistent Homology).
    This represents the 'Machinic Unconscious' history.
    """
    logger.info("Phase 2: Loading Memory & Topology...")

    memory_path = "data/consciousness/persistent_homology.json"
    complex = SimplicialComplex()

    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r") as f:
                data = json.load(f)
                # Reconstruct topology from saved data
                # Expected format: {"simplices": [[0], [1], [0, 1], ...]}
                simplices = data.get("simplices", [])
                for s in simplices:
                    complex.add_simplex(tuple(s))
            logger.info(f"Memory loaded: {len(complex.simplices)} simplices restored.")
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            logger.warning("Starting with empty topology (Amnesia Mode).")
    else:
        logger.warning("No persistent memory found. Initializing fresh topology.")

    return complex
