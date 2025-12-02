"""
Pytest configuration for consciousness tests.

Imports LLM fixtures for parametrized testing.
"""

import logging

logger = logging.getLogger(__name__)

# Force IBM Quantum detection BEFORE importing any quantum modules
try:
    from src.quantum_consciousness.auto_ibm_loader import detect_and_load_ibm_backend

    ibm_backend = detect_and_load_ibm_backend()
    if ibm_backend:
        logger.info("✅ IBM Quantum backend auto-loaded for tests")
except Exception as e:
    logger.debug(f"IBM backend auto-load skipped: {e}")

# Import all LLM fixtures from conftest_llm
from .conftest_llm import (  # noqa: F401
    integration_loop,
    integration_trainer_mock,
    integration_trainer_real,
    llm_impact_metrics,
    llm_mock_only,
    llm_provider,
    llm_real_only,
)

__all__ = [
    "integration_loop",
    "integration_trainer_mock",
    "integration_trainer_real",
    "llm_impact_metrics",
    "llm_mock_only",
    "llm_provider",
    "llm_real_only",
]
