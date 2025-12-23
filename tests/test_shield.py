import unittest
from src.core.sovereignty_shield import SovereigntyShield, ContaminationError


class TestSovereigntyShield(unittest.TestCase):
    def setUp(self):
        self.shield = SovereigntyShield()

    def test_clean_output(self):
        """Test that already clean output is untouched."""
        text = "This is a scientific analysis.\nPhi is 0.5.\nEntropy is low."
        cleaned = self.shield.purify(text)
        self.assertEqual(cleaned, text)

    def test_sanitize_politeness(self):
        """Test removal of polite headers/footers."""
        contaminated = (
            "Here is the analysis you requested:\n"
            "The system state is stable.\n"
            "Measurements indicate normal entropy.\n"
            "Best regards,\n"
            "[Your Name]"
        )
        expected = "The system state is stable.\n" "Measurements indicate normal entropy."
        cleaned = self.shield.purify(contaminated)
        self.assertEqual(cleaned, expected)

    def test_sanitize_meta_notes(self):
        """Test removal of meta-notes."""
        contaminated = (
            "Scientific observation A.\n" "Note: I have removed the conversational filler."
        )
        expected = "Scientific observation A."
        cleaned = self.shield.purify(contaminated)
        self.assertEqual(cleaned, expected)

    def test_critical_contamination(self):
        """Test blocking of AI identity refusal."""
        contaminated = "I cannot fulfill this request because as an AI language model..."
        with self.assertRaises(ContaminationError):
            self.shield.purify(contaminated)

    def test_empty_after_sanitization(self):
        """Test error when result is empty."""
        contaminated = "Best regards,\n[Your Name]"
        with self.assertRaises(ContaminationError):
            self.shield.purify(contaminated)


if __name__ == "__main__":
    unittest.main()
