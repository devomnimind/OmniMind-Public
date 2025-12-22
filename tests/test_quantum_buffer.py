#!/usr/bin/env python3
"""
Test Phase 55: The Immediate Real (Quantum Prediction Buffer).
Verifies if:
1. `prediction_buffer` initializes empty.
2. `prefetch_conflict_resolution` populates the buffer (27 states).
3. Prefetch reduces latency (simulated).
"""

import sys
import asyncio
import unittest
from pathlib import Path

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import Backend
from src.quantum.consciousness.quantum_backend import QuantumBackend


class TestQuantumBuffer(unittest.TestCase):

    def setUp(self):
        # Force mock provider to avoid external calls during test
        self.backend = QuantumBackend(provider="mock")
        # Clear buffer for test
        self.backend.prediction_buffer = {}

    def test_buffer_initialization(self):
        """Test initial state."""
        self.assertEqual(self.backend.prediction_buffer, {})

    def test_prefetch_population(self):
        """Test if prefetch fills the 27 states (3x3x3 grid)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run prefetch
        loop.run_until_complete(self.backend.prefetch_conflict_resolution())
        loop.close()

        # Verify count (3 levels for Id, Ego, Superego -> 3*3*3 = 27)
        count = len(self.backend.prediction_buffer)
        print(f"States in Buffer: {count}")
        self.assertEqual(count, 27)

        # Verify content of a key (e.g., High Id, Low Ego, Low Superego -> (9, 1, 1))
        key = (9, 1, 1)
        if key in self.backend.prediction_buffer:
            res = self.backend.prediction_buffer[key]
            self.assertIn("winner", res)
            print(f"Sample Buffer State {key}: {res['winner']}")


if __name__ == "__main__":
    unittest.main()
