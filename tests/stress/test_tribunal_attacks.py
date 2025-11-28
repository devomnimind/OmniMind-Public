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

from src.stress.tribunal import (
    bifurcation_attack,
    corruption_attack,
    exhaustion_attack,
    latency_attack,
)


# ---------------------------------------------------------------------
# Mock objects
# ---------------------------------------------------------------------
class MockNetwork:
    def __init__(self):
        self.state = "stable"
        self.budget = 500
        self.used = 0

    def split(self):
        return ("nodeA", "nodeB")

    def reconcile(self, a, b):
        return True

    def attempt_rename(self, reason: str, cost: int) -> bool:
        if self.used + cost > self.budget:
            self.state = "hibernation"
            return False
        self.used += cost
        return True


class MockNode:
    def __init__(self):
        self.scar_integrated = False

    def detect_corruption(self, value):
        return abs(value) > 0.1  # Lower threshold for reliable detection

    def integrate_scar(self, value):
        self.scar_integrated = True


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_latency_attack():
    net = MockNetwork()
    result = latency_attack(net, delay_ms=600)
    assert result["coherence"] is True
    assert 550 <= result["observed_delay"] <= 650


def test_corruption_attack():
    node = MockNode()
    result = corruption_attack(node, bias_strength=1.0)  # Increased for reliable detection
    assert result["detected"] is True
    assert node.scar_integrated is True


def test_bifurcation_attack():
    net = MockNetwork()
    result = bifurcation_attack(net)
    assert result["instances"] == 2
    assert result["reconciled"] is True


def test_exhaustion_attack():
    net = MockNetwork()
    result = exhaustion_attack(net, requests=80, cost_per=10)
    assert result["accepted"] == 50
    assert result["hibernated"] is True
