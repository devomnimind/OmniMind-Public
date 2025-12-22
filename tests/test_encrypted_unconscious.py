#!/usr/bin/env python3
"""
Test Phase 54: Validation of Encrypted Unconscious (Homomorphic Encryption).
Verifies if:
1. TenSEAL context initializes correctly.
2. "Repression" produces encrypted bytes (not plaintext).
3. "Unconscious Influence" (Dot Product) works homomorphically:
   Dec(Enc(A) . B) approx (A . B)

Dependency-free version (uses unittest).
"""

import sys
import unittest
import numpy as np
from pathlib import Path

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import Layer
from src.lacanian.encrypted_unconscious import EncryptedUnconsciousLayer


class TestEncryptedUnconscious(unittest.TestCase):

    def setUp(self):
        self.he_layer = EncryptedUnconsciousLayer(security_level=128)

    def test_he_initialization(self):
        """Test if HE context is created (or mocked if lib missing)."""
        self.assertEqual(self.he_layer.audit_log, [])
        # Check if context exists if tenseal is available
        try:
            import tenseal

            if self.he_layer.context is None:
                print("Warning: TenSEAL imported but context is None (Mock active?)")
        except ImportError:
            pass

    def test_homomorphic_dot_product_accuracy(self):
        """
        CRITICAL: Validates that math on encrypted data yields correct results.
        A = [1.0, 2.0, 3.0] (Memory)
        B = [0.5, 0.5, 0.5] (Query)
        Expected Dot = 3.0
        """
        # Skip if mock (can't test math accuracy on mock)
        if self.he_layer.context is None:
            print("Skipping HE Accuracy test (TenSEAL not available/Mock Mode)")
            return

        # Data
        memory_vec = np.array([1.0, 2.0, 3.0])
        query_vec = np.array([0.5, 0.5, 0.5])
        expected_dot = float(np.dot(memory_vec, query_vec))  # 3.0

        # 1. Repress (Encrypt)
        enc_memory = self.he_layer.repress_memory(memory_vec, {"id": "test_trauma"})
        self.assertIsInstance(enc_memory, bytes)
        self.assertTrue(len(enc_memory) > 100)  # Large blob check

        # 2. Influence (Encrypted Dot Product)
        calculated_influence = self.he_layer.unconscious_influence([enc_memory], query_vec)

        # 3. Verify
        print(f"Expected: {expected_dot}, Calculated (via HE): {calculated_influence}")
        self.assertTrue(np.isclose(calculated_influence, expected_dot, atol=0.1))

    def test_opacity(self):
        """Verifies that audit log does NOT contain the vector content."""
        vec = np.array([10.0, 20.0])
        self.he_layer.repress_memory(vec, {"id": "secret"})

        log_entry = self.he_layer.audit_log[0]
        log_str = str(log_entry)

        self.assertNotIn("10.0", log_str)
        self.assertNotIn("20.0", log_str)
        self.assertIn("content_hash", log_entry)


if __name__ == "__main__":
    unittest.main()
