"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

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
