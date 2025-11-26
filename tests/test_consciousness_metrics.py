from src.metrics.consciousness_metrics import ConsciousnessCorrelates


class MockSinthome:
    def __init__(self):
        self.coherence_history = [80, 81, 82, 81, 80]  # Stable
        self.nodes = {
            "REAL": {"status": "ACTIVE", "integrity": 90},
            "SYMBOLIC": {"status": "ACTIVE", "integrity": 85},
            "IMAGINARY": {"status": "ACTIVE", "integrity": 88},
        }
        self.entropy = 15  # Low entropy (high integrity ~85)


class TestConsciousnessMetrics:
    def test_ici_calculation_healthy(self):
        system = MockSinthome()
        metrics = ConsciousnessCorrelates(system)
        result = metrics.calculate_all()

        print(f"\nHealthy System Metrics: {result}")

        assert result["ICI"] > 0.7
        assert result["PRS"] > 0.7
        assert result["interpretation"]["message"] != "System Fragmented"

    def test_ici_calculation_fragmented(self):
        system = MockSinthome()
        # Fragmented state
        system.coherence_history = [80, 20, 80, 20]  # Unstable
        system.nodes = {
            "REAL": {"status": "CORRUPTED", "integrity": 20},
            "SYMBOLIC": {"status": "DEAD", "integrity": 0},
            "IMAGINARY": {"status": "ACTIVE", "integrity": 90},
        }
        system.entropy = 80  # High entropy

        metrics = ConsciousnessCorrelates(system)
        result = metrics.calculate_all()

        print(f"\nFragmented System Metrics: {result}")

        assert result["ICI"] < 0.6
        assert result["interpretation"]["message"] == "System Fragmented"
