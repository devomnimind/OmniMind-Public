from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Set


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

# src/autopoietic/system_boundary.py
"""System Boundary module.

Defines the operational closure of the OmniMind system, distinguishing internal
components from external resources. The implementation provides a simple API to
register components, query their status, and enforce boundary policies.

All functions include full type hints and Google‑style docstrings to satisfy
OmniMind’s strict quality rules.
"""


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ComponentInfo:
    """Metadata about a registered component.

    Attributes:
        name: Unique identifier of the component.
        internal: ``True`` if the component is considered part of the system
            boundary (i.e., internal), ``False`` otherwise.
    """

    name: str
    internal: bool


class SystemBoundary:
    """Manage the system boundary for autopoietic components.

    The class tracks which components are internal and provides checks to ensure
    that only allowed external interactions occur.
    """

    def __init__(self) -> None:
        """Create a new ``SystemBoundary`` instance.

        Initializes an empty registry and a logger child.
        """
        self._registry: Dict[str, ComponentInfo] = {}
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("SystemBoundary initialized")

    def register(self, name: str, internal: bool = True) -> None:
        """Register a component with the boundary manager.

        Args:
            name: Unique component name.
            internal: Whether the component is internal to the system.
        """
        if name in self._registry:
            self._logger.warning("Component %s already registered; overwriting", name)
        self._registry[name] = ComponentInfo(name=name, internal=internal)
        self._logger.debug("Registered component %s (internal=%s)", name, internal)

    def is_internal(self, name: str) -> bool:
        """Check if a component is internal.

        Args:
            name: Component name.

        Returns:
            ``True`` if the component is registered as internal, ``False`` if
            external or not registered.
        """
        info = self._registry.get(name)
        result = bool(info and info.internal)
        self._logger.debug("Component %s internal check: %s", name, result)
        return result

    def list_internal(self) -> Set[str]:
        """Return a set of all internal component names."""
        internal_set = {name for name, info in self._registry.items() if info.internal}
        self._logger.debug("Internal components: %s", internal_set)
        return internal_set

    def enforce_policy(self, name: str) -> None:
        """Enforce a simple policy that external components cannot be accessed.

        Raises:
            PermissionError: If the component is external.
        """
        if not self.is_internal(name):
            self._logger.error("Attempted access to external component %s", name)
            raise PermissionError(f"Component '{name}' is external and cannot be accessed.")
        self._logger.debug("Access to internal component %s allowed", name)
