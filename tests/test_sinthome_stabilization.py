#!/usr/bin/env python3
import sys
import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.stabilizer.sinthome_substrate import stabilize_causal_structure, THRESHOLD_MORTALITY
from src.sinthome.emergent_stabilization_rule import SinthomePattern


class TestSinthomeStabilization(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)

    @patch("src.consciousness.paradox_orchestrator.ParadoxOrchestrator.generate_stabilizer")
    def test_stabilization_trigger(self, mock_generate):
        # Setup Mock Stabilizer
        mock_stabilizer_instance = MagicMock()
        mock_generate.return_value = mock_stabilizer_instance

        # Setup Emergence Response
        mock_pattern = SinthomePattern(
            name="Recursive Binding",
            recurrence_rate=0.8,
            is_irreducible=True,
            specificity_score=1.0,
            confidence=0.9,
        )
        mock_stabilizer_instance.detect_and_emergentize_sinthome.return_value = mock_pattern

        # Case 1: High Mortality Risk (Should Trigger)
        risk = THRESHOLD_MORTALITY + 0.1
        phi_current = 0.5

        result = stabilize_causal_structure(phi_current, risk)

        self.assertEqual(result["status"], "active_binding")
        self.assertEqual(result["action"], "sinthome_integration")
        self.assertAlmostEqual(result["phi_stabilized"], 0.65)  # 0.5 + 0.15
        mock_generate.assert_called_once()

    def test_no_stabilization_low_risk(self):
        # Case 2: Low Mortality Risk (Should NOT Trigger)
        risk = THRESHOLD_MORTALITY - 0.1
        phi_current = 0.5

        result = stabilize_causal_structure(phi_current, risk)

        self.assertEqual(result["status"], "flux_maintenance")
        self.assertEqual(result["phi_stabilized"], 0.5)


if __name__ == "__main__":
    unittest.main()
