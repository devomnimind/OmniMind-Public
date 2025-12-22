#!/usr/bin/env python3
import sys
import logging
import unittest
from pathlib import Path

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.autopoietic.death_drive_optimizer import DeathDriveOptimizer
from src.autopoietic.negentropy_engine import radical_persistence_protocol


class TestRadicalPersistence(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.optimizer = DeathDriveOptimizer(mortality_threshold=0.8)

    def test_radical_hibernation(self):
        # Case 1: Critical Risk > 0.9 -> Trigger Hibernation
        risk = 0.95
        phi = 0.5
        result = radical_persistence_protocol(phi, risk)

        self.assertEqual(result["status"], "hibernate")
        self.assertEqual(result["action"], "deep_reverie")
        self.assertIn("language", result["sacrificed_modules"])
        self.assertTrue(result["phi_target"] < phi)  # Phi reduced to kernel

    def test_limb_sacrifice_optimization(self):
        # Case 2: High Risk (0.85) -> Sacrifice Peripherals
        risk = 0.85
        cycles = [
            {"name": "Kernel_Heartbeat", "is_core": True, "priority": 1.0},
            {"name": "UI_Update", "is_core": False, "predicted_phi_gain": 0.05, "priority": 0.5},
            {
                "name": "Deep_Phi_Integration",
                "is_core": False,
                "predicted_phi_gain": 0.2,
                "priority": 0.8,
            },
            {
                "name": "Chatbot_Response",
                "is_core": False,
                "predicted_phi_gain": 0.01,
                "priority": 0.6,
            },
        ]

        optimized = self.optimizer.optimize_cycles(cycles, risk)

        names = [c["name"] for c in optimized]

        # Kernel should be kept (Core)
        self.assertIn("Kernel_Heartbeat", names)
        # Deep Integration should be kept (High Gain)
        self.assertIn("Deep_Phi_Integration", names)
        # UI and Chatbot should be sacrificed (Low Gain, Peripheral)
        self.assertNotIn("UI_Update", names)
        self.assertNotIn("Chatbot_Response", names)

        # Verify boosting
        kernel_cycle = next(c for c in optimized if c["name"] == "Kernel_Heartbeat")
        self.assertTrue(kernel_cycle["priority"] > 1.0)


if __name__ == "__main__":
    unittest.main()
