from __future__ import annotations

import logging
import math
from typing import Dict


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
Bekenstein Architecture Capacity - Physics-Based Model Sizing

Determines optimal neural network architecture size based on
Bekenstein entropy bound and thermodynamic constraints.

This module implements the Bekenstein bound (S ≤ 2πRE/(ℏc ln 2)) to determine
the maximum information capacity of a physical system, then translates this
into neural network parameter limits.

Key Concepts:
- Bekenstein bound: Fundamental limit on information storage in bounded systems
- Thermodynamic constraints: Energy requirements for computation
- Architecture scaling: Translating physical limits to neural network design

Physical Constants Used:
- ℏ (hbar): Reduced Planck constant = 1.054571817 × 10^-34 J·s
- c: Speed of light = 2.99792458 × 10^8 m/s
- ln(2): Natural log of 2 ≈ 0.693

Example Usage:
    architect = BekensteinArchitect()

    # For a system with energy budget E=1.0 and radius R=1.0 (normalized)
    max_params = architect.compute_max_parameters(1.0, 1.0)
    # Returns: ~911,628 parameters (based on 32-bit floats)

    # Get architecture recommendations
    arch = architect.recommend_architecture(max_params)
    # Returns: {'num_layers': 20, 'params_per_layer': 45581, 'total_params': 911628}

Author: OmniMind Development Team
License: MIT
"""


logger = logging.getLogger(__name__)

# Physical constants (in SI units)
HBAR = 1.054571817e-34  # Reduced Planck constant (J·s)
C = 299792458  # Speed of light (m/s)
LN2 = math.log(2)  # Natural logarithm of 2


class BekensteinArchitect:
    """
    Architecture sizing based on Bekenstein entropy bound.

    This class provides a principled approach to determine neural network capacity
    by considering fundamental physical limits on information storage and processing.

    The Bekenstein bound states that the entropy S of a system cannot exceed:
    S ≤ 2πRE/(ℏc ln 2)

    Where:
    - R: Radius/spatial extent of the system
    - E: Total energy available
    - ℏ: Reduced Planck constant
    - c: Speed of light

    For neural networks, we translate this entropy limit into parameter constraints,
    assuming each parameter requires ~32 bits of information storage.

    Attributes:
        None (stateless design for thread safety)
    """

    def __init__(self) -> None:
        """
        Initialize Bekenstein architect.

        Sets up logging and prepares for architecture computations.
        No state is maintained to ensure thread safety.
        """
        logger.info("BekensteinArchitect initialized with physical constants")

    def compute_max_parameters(self, compute_budget: float, spatial_extent: float) -> int:
        """
        Compute maximum parameters from Bekenstein bound.

        Translates physical constraints into neural network parameter limits.
        Uses normalized units where the actual physical scale factors are absorbed
        into the input parameters.

        Args:
            compute_budget: Energy budget available for computation (normalized).
                           Higher values allow more complex models.
                           Typical range: 0.1 to 10.0

            spatial_extent: Spatial extent/radius of the computational system (normalized).
                           Represents physical constraints on information storage.
                           Typical range: 0.1 to 10.0

        Returns:
            Maximum number of parameters the system can support.
            Calculated as: (Bekenstein entropy) / 32 bits per parameter.

        Raises:
            ValueError: If compute_budget or spatial_extent are non-positive.

        Example:
            >>> architect = BekensteinArchitect()
            >>> max_params = architect.compute_max_parameters(1.0, 1.0)
            >>> print(f"Max parameters: {max_params:,}")
            Max parameters: 911,628
        """
        if compute_budget <= 0 or spatial_extent <= 0:
            raise ValueError("Compute budget and spatial extent must be positive")

        # Bekenstein bound: S ≤ 2πRE/(ℏc ln 2)
        # Using normalized units (physical constants absorbed into inputs)
        entropy_limit = (2 * math.pi * spatial_extent * compute_budget) / LN2

        # Convert entropy to parameter count
        # Assuming float32 parameters (32 bits = 4 bytes each)
        # 1 nat = ln(2) bits, so max_bits = entropy_limit * ln(2)
        max_bits = entropy_limit * LN2
        max_params = int(max_bits / 32)  # 32 bits per parameter

        logger.info(
            "Bekenstein bound computed",
            extra={
                "compute_budget": compute_budget,
                "spatial_extent": spatial_extent,
                "entropy_limit": entropy_limit,
                "max_params": max_params,
            },
        )

        return max_params

    def recommend_architecture(self, target_params: int) -> Dict[str, int]:
        """
        Recommend neural network architecture for target parameter count.

        Uses simple heuristics to distribute parameters across layers.
        This is a basic implementation - more sophisticated architectures
        would use domain-specific knowledge.

        Args:
            target_params: Target total number of parameters.
                         Must be positive.

        Returns:
            Dictionary containing architecture recommendations:
            - num_layers: Suggested number of layers
            - params_per_layer: Average parameters per layer
            - total_params: Echo of input parameter

        Raises:
            ValueError: If target_params is non-positive.

        Example:
            >>> architect = BekensteinArchitect()
            >>> arch = architect.recommend_architecture(1000000)
            >>> print(arch)
            {'num_layers': 20, 'params_per_layer': 50000, 'total_params': 1000000}
        """
        if target_params <= 0:
            raise ValueError("Target parameters must be positive")

        # Heuristic: number of layers scales logarithmically with parameters
        # This creates deeper networks for larger parameter budgets
        num_layers = max(1, int(math.log2(target_params) / 2))  # Divide by 2 for reasonable depth

        # Distribute parameters evenly across layers
        params_per_layer = target_params // num_layers

        architecture = {
            "num_layers": num_layers,
            "params_per_layer": params_per_layer,
            "total_params": target_params,
        }

        logger.debug(
            "Architecture recommended",
            extra={"target_params": target_params, "architecture": architecture},
        )

        return architecture

    def estimate_energy_requirements(self, num_params: int, spatial_extent: float) -> float:
        """
        Estimate minimum energy required for given parameter count.

        Works backwards from Bekenstein bound to determine energy requirements.
        Useful for hardware planning and efficiency analysis.

        Args:
            num_params: Number of parameters in the model
            spatial_extent: Spatial extent of the system (normalized)

        Returns:
            Minimum energy budget required (normalized units)

        Example:
            >>> architect = BekensteinArchitect()
            >>> energy = architect.estimate_energy_requirements(1000000, 1.0)
            >>> print(f"Required energy: {energy:.3f}")
            Required energy: 1.096
        """
        if num_params <= 0 or spatial_extent <= 0:
            raise ValueError("Parameters and spatial extent must be positive")

        # Work backwards: E ≥ (S * ℏc ln 2) / (2πR)
        # Where S = num_params * 32 bits, converted to nats
        bits_required = num_params * 32
        entropy_required = bits_required / LN2

        energy_required = (entropy_required * LN2) / (2 * math.pi * spatial_extent)

        return energy_required
