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
Elastic Weight Consolidation (EWC) Module.

This module implements EWC to allow the OmniMind system to learn from new experiences
(adjusting weights) without forgetting previous important knowledge (catastrophic forgetting).
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ElasticWeightConsolidation:
    """
    Implements Elastic Weight Consolidation.

    Maintains a Fisher Information Matrix to estimate the importance of each parameter
    (weight) for previous tasks. When training on a new task (or adjusting weights
    via ICAC), it adds a penalty for changing important parameters.
    """

    def __init__(self, lambda_ewc: float = 0.4):
        """
        Args:
            lambda_ewc: Hyperparameter that controls how much to penalize changes
                        to important weights. Higher = more stability (less forgetting),
                        Lower = more plasticity (faster learning).
        """
        self.lambda_ewc = lambda_ewc
        self.fisher_matrix: Dict[str, float] = {}  # Importance of each weight
        self.optimal_weights: Dict[str, float] = {}  # Weights after previous task
        logger.info(f"EWC initialized with lambda={lambda_ewc}")

    def compute_fisher_information(
        self, agent_weights: Dict[str, float], audit_history: List[Dict[str, Any]]
    ) -> None:
        """
        Computes (or approximates) the Fisher Information Matrix for the current weights.

        In a full neural network, this uses gradients. For our agent weight system,
        we approximate importance based on how often an agent was part of a successful
        high-confidence decision.

        Args:
            agent_weights: Current weights of the agents (e.g., {'Id': 0.3, 'Ego': 0.5}).
            audit_history: History of decisions to analyze importance.
        """
        # Save current weights as optimal for the "previous task"
        self.optimal_weights = agent_weights.copy()

        # Reset Fisher Matrix
        self.fisher_matrix = {k: 0.0 for k in agent_weights}

        # Approximate Fisher Information
        # If an agent contributed to a high-confidence decision, its weight is "important".
        for event in audit_history:
            if event.get("type") == "decision" and event.get("success", False):
                confidence = event.get("confidence", 0.5)
                agents = event.get("contributing_agents", [])

                for agent_name in agents:
                    if agent_name in self.fisher_matrix:
                        # Add to importance (simplified approximation)
                        self.fisher_matrix[agent_name] += confidence

        # Normalize Fisher Matrix
        total_importance = sum(self.fisher_matrix.values())
        if total_importance > 0:
            for k in self.fisher_matrix:
                self.fisher_matrix[k] /= total_importance

        logger.info(f"Fisher Information computed: {self.fisher_matrix}")

    def penalty_loss(self, new_weights: Dict[str, float]) -> float:
        """
        Calculates the EWC penalty loss for a proposed set of new weights.

        Loss = (lambda / 2) * sum(F_i * (theta_i - theta_i*)^2)

        Args:
            new_weights: The proposed new weights.

        Returns:
            The penalty value (float).
        """
        loss = 0.0
        for name, new_w in new_weights.items():
            if name in self.optimal_weights and name in self.fisher_matrix:
                old_w = self.optimal_weights[name]
                fisher = self.fisher_matrix[name]
                loss += fisher * (new_w - old_w) ** 2

        return (self.lambda_ewc / 2.0) * loss

    def adjust_weights_with_protection(
        self, current_weights: Dict[str, float], proposed_changes: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Adjusts weights based on proposed changes, but mitigates changes to
        important weights using EWC logic.

        Args:
            current_weights: Current agent weights.
            proposed_changes: Desired delta for each weight (e.g. {'Id': +0.1}).

        Returns:
            New adjusted weights.
        """
        new_weights = current_weights.copy()

        for name, delta in proposed_changes.items():
            if name not in new_weights:
                continue

            # Calculate resistance based on Fisher Information
            # High Fisher = High Resistance = Low effective delta
            importance = self.fisher_matrix.get(name, 0.0)

            # Damping factor: 1.0 means no resistance (importance 0)
            # As importance approaches 1.0, resistance increases
            resistance = 1.0 + (importance * self.lambda_ewc * 10.0)

            effective_delta = delta / resistance

            new_weights[name] += effective_delta

            # Ensure bounds [0, 1]
            new_weights[name] = max(0.0, min(1.0, new_weights[name]))

        return new_weights
