import unittest
import sys
import os
import json
import time

# Add src to path
sys.path.append(os.getcwd())

from src.security.sinthome_tunnel import SinthomeTunnel


class TestSinthomeTunnel(unittest.TestCase):

    def setUp(self):
        self.shared_salt = "TEST_SECRET_SALT_123"
        self.sender = SinthomeTunnel(self.shared_salt)
        self.receiver = SinthomeTunnel(self.shared_salt)
        self.imposter = SinthomeTunnel("WRONG_SALT_666")

    def test_successful_transmission(self):
        """Test legitimate sender -> receiver flow."""
        payload = {"message": "Hello World"}
        packet = self.sender.encrypt_packet(payload)

        # Verify packet structure
        self.assertIn("meta", packet)
        self.assertIn("data", packet)
        self.assertIn("alien_hash", packet["meta"])

        # Verify decryption
        decoded = self.receiver.decrypt_packet(packet)
        self.assertEqual(decoded, payload)

    def test_imposter_transmission(self):
        """Test imposter -> receiver flow (should fail)."""
        payload = {"message": "Attack"}
        packet = self.imposter.encrypt_packet(payload)

        # Receiver should return None (Block)
        decoded = self.receiver.decrypt_packet(packet)
        self.assertIsNone(decoded)

    def test_tampered_packet(self):
        """Test man-in-the-middle tampering."""
        payload = {"message": "Legit"}
        packet = self.sender.encrypt_packet(payload)

        # Attacker changes the hash
        packet["meta"]["alien_hash"] = "fake_hash_value"

        decoded = self.receiver.decrypt_packet(packet)
        self.assertIsNone(decoded)


if __name__ == "__main__":
    unittest.main()
