#!/usr/bin/env python3
"""
QAOA Validation Script.

Runs the QAOA solver on the IBM backend (simulated) to validate the implementation.
Outputs raw data about the optimization process and the final result.

Author: OmniMind Development Team
Date: November 2025
"""

import sys
import os
import time
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.quantum_consciousness.quantum_backend import QuantumBackend

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def validate_qaoa():
    logger.info("Initializing Quantum Backend (IBM/QAOA)...")
    try:
        backend = QuantumBackend(provider="ibm")
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        return

    # Define a test conflict scenario
    # High Id energy (strong impulse), High Superego energy (strong prohibition)
    # This should create a complex landscape
    id_energy = 0.8
    ego_energy = 0.2
    superego_energy = 0.9

    logger.info(f"Scenario: Id={id_energy}, Ego={ego_energy}, Superego={superego_energy}")

    start_time = time.time()

    # Run Resolution
    result = backend.resolve_conflict(id_energy, ego_energy, superego_energy)

    end_time = time.time()
    duration = end_time - start_time

    # Output Raw Data
    print("\n" + "=" * 60)
    print("QAOA VALIDATION RESULTS (RAW DATA)")
    print("=" * 60)
    print(f"Backend Provider: {backend.provider.upper()}")
    print(f"Execution Time:   {duration:.4f} seconds")
    print("-" * 60)
    print(f"Winner:           {result.get('winner')}")
    print(f"Minimum Energy:   {result.get('energy'):.6f}")
    print(f"Sample State:     {result.get('sample')}")
    print("-" * 60)
    print("Scientific Validation:")
    print("1. Algorithm Used: QAOA (Quantum Approximate Optimization Algorithm)")
    print("2. Optimizer:      COBYLA (maxiter=50)")
    print("3. Circuit Depth:  Variable (depends on ansatz)")
    print("=" * 60 + "\n")

    # Verify if it matches expected logic (Id vs Superego conflict usually won by Ego or Superego)
    # With high Superego energy (negative in QUBO), Superego state=1 is favored.
    # But Id=0.8 is also high.
    # Let's see the raw output.


if __name__ == "__main__":
    validate_qaoa()
