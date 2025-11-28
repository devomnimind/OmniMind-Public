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

"""
Tests for Elastic Weight Consolidation (EWC).
"""

import pytest

from src.learning.ewc import ElasticWeightConsolidation


def test_fisher_information_computation():
    ewc = ElasticWeightConsolidation()
    weights = {"Id": 0.5, "Ego": 0.5}
    history = [
        {
            "type": "decision",
            "success": True,
            "confidence": 0.9,
            "contributing_agents": ["Id"],
        },
        {
            "type": "decision",
            "success": True,
            "confidence": 0.1,
            "contributing_agents": ["Ego"],
        },
    ]

    ewc.compute_fisher_information(weights, history)

    # Id contributed 0.9, Ego 0.1.
    # Normalized: Id=0.9, Ego=0.1
    assert ewc.fisher_matrix["Id"] == 0.9
    assert ewc.fisher_matrix["Ego"] == 0.1


def test_penalty_loss():
    ewc = ElasticWeightConsolidation(lambda_ewc=1.0)
    ewc.optimal_weights = {"A": 0.5}
    ewc.fisher_matrix = {"A": 1.0}

    # Change weight from 0.5 to 0.6
    # Loss = (1.0 / 2) * 1.0 * (0.6 - 0.5)^2 = 0.5 * 0.01 = 0.005
    loss = ewc.penalty_loss({"A": 0.6})
    assert abs(loss - 0.005) < 1e-6


def test_weight_protection():
    ewc = ElasticWeightConsolidation(lambda_ewc=1.0)
    ewc.fisher_matrix = {"Important": 1.0, "Unimportant": 0.0}

    current = {"Important": 0.5, "Unimportant": 0.5}
    proposed_delta = {"Important": 0.1, "Unimportant": 0.1}

    new_weights = ewc.adjust_weights_with_protection(current, proposed_delta)

    # Important should change LESS than Unimportant
    delta_important = new_weights["Important"] - current["Important"]
    delta_unimportant = new_weights["Unimportant"] - current["Unimportant"]

    assert delta_important < delta_unimportant
    assert delta_unimportant == pytest.approx(0.1)  # No resistance
