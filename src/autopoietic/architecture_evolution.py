from __future__ import annotations

import logging
from typing import List, Mapping
from .meta_architect import ComponentSpec, MetaArchitect


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

# src/autopoietic/architecture_evolution.py
"""Architecture Evolution module.

Provides a lightweight *architecture evolution* engine that analyses existing
component specifications and proposes evolved components. The implementation is
deterministic and does not rely on external AI services, satisfying OmniMind’s
production constraints.

All functions include full type hints and Google‑style docstrings.
"""


logger = logging.getLogger(__name__)


class ArchitectureEvolution:
    """Propose evolved component specifications based on existing ones.

    The evolution strategy is simple: for each existing component, create a new
    component with the prefix ``"evolved_"`` and the same type. In a real system
    this could involve performance metrics, usage statistics, etc.
    """

    def __init__(self, meta_architect: MetaArchitect) -> None:
        """Create an ``ArchitectureEvolution`` instance.

        Args:
            meta_architect: Instance of ``MetaArchitect`` used to validate the
                generated specifications.
        """
        self._meta_architect = meta_architect
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("ArchitectureEvolution initialized")

    def propose_evolution(self, existing_specs: Mapping[str, ComponentSpec]) -> List[ComponentSpec]:
        """Generate evolved specifications from existing ones.

        Args:
            existing_specs: Mapping from component name to its ``ComponentSpec``.

        Returns:
            List of new ``ComponentSpec`` objects representing evolved
            components.
        """
        evolved: List[ComponentSpec] = []
        for name, spec in existing_specs.items():
            evolved_name = f"evolved_{name}"
            # Preserve type, add a flag in config indicating evolution
            config = dict(spec.config)
            config["evolved"] = "true"
            new_spec = ComponentSpec(name=evolved_name, type=spec.type, config=config)
            evolved.append(new_spec)
            self._logger.debug("Evolved spec created: %s from %s", evolved_name, name)
        # Validate before returning
        if not self._meta_architect.validate_specifications(evolved):
            self._logger.error("Validation of evolved specs failed")
            raise ValueError("Evolved specifications validation failed")
        return evolved
