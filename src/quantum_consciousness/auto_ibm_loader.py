"""
Automatic IBM Quantum backend loader.

Detects IBM Quantum credentials in .env and automatically loads real backend.
Falls back to simulator if credentials unavailable or connection fails.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def get_least_busy_backend() -> Optional[Any]:
    """
    Get the least busy IBM Quantum backend (menor fila).

    Returns:
        Backend with minimum queue size, or None if no backends available
    """
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService()
        backends = service.backends()

        if not backends:
            logger.warning("⚠️ No IBM backends available")
            return None

        # Find backend with minimum pending jobs (least busy)
        least_busy = min(backends, key=lambda b: b.status().pending_jobs)
        queue_size = least_busy.status().pending_jobs
        qubits = least_busy.num_qubits

        logger.info(f"✅ Selected IBM backend: {least_busy.name}")
        logger.info(f"   Qubits: {qubits} | Queue: {queue_size} jobs")

        return least_busy

    except Exception as e:
        logger.error(f"❌ Error selecting least busy backend: {e}")
        return None


def detect_and_load_ibm_backend() -> Optional[Any]:
    """
    Detect IBM Quantum credentials and automatically load REAL backend.
    Selects backend com menor fila (least busy).

    Checks for:
    - QISKIT_IBM_TOKEN environment variable
    - IBM_QUANTUM_API_KEY environment variable
    - IBMQ_TOKEN environment variable (legacy)

    Returns:
        Real IBM backend (least busy) if credentials found and loaded,
        None if no credentials or load failed
    """
    # Check for credentials in environment
    token = (
        os.getenv("QISKIT_IBM_TOKEN") or os.getenv("IBM_QUANTUM_API_KEY") or os.getenv("IBMQ_TOKEN")
    )

    if not token:
        logger.debug("ℹ️ No IBM Quantum credentials found in environment")
        return None

    logger.info("🔴 IBM Quantum credentials detected - selecting least busy backend...")

    try:
        # Import Qiskit IBM Runtime
        from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: F401

        logger.info("✓ Qiskit IBM Runtime loaded")

        # Use get_least_busy_backend() for selection
        backend = get_least_busy_backend()

        if backend:
            logger.info("✅ IBM Quantum backend READY (real hardware selected)")
            return backend
        else:
            logger.warning("⚠️ No IBM backend available")
            return None

    except ImportError as e:
        logger.warning(f"⚠️ Qiskit IBM Runtime not installed: {e}")
        logger.info("   Install with: pip install qiskit-ibm-runtime")
        return None

    except Exception as e:
        logger.error(f"❌ IBM backend initialization failed: {e}")
        logger.info("   Falling back to simulator")
        return None


def get_quantum_backend() -> str:
    """
    Get current quantum backend status.

    Returns:
        String describing which backend is active
    """
    backend = detect_and_load_ibm_backend()

    if backend:
        return f"IBM Quantum Cloud ({backend.backend_type.value})"
    else:
        return "Qiskit Aer Simulator (local)"


if __name__ == "__main__":
    # Test the detector
    logging.basicConfig(level=logging.INFO)
    backend = detect_and_load_ibm_backend()
    status = get_quantum_backend()
    print(f"\n🎯 Quantum backend: {status}")
