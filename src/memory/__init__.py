        from .episodic_memory import EpisodicMemory
        from .holographic_memory import EventHorizonMemory
        from .holographic_memory import HolographicProjection
        from .holographic_memory import HolographicSurface
        from .soft_hair_encoding import SoftHair
        from .soft_hair_encoding import SoftHairEncoder
        from .soft_hair_encoding import SoftHairMemory

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

"""Memory module for OmniMind agent system."""

# Lazy imports to avoid dependency issues
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .episodic_memory import EpisodicMemory
from .holographic_memory import (
        EventHorizonMemory,
        HolographicProjection,
        HolographicSurface,
    )
    from .soft_hair_encoding import SoftHair, SoftHairEncoder, SoftHairMemory


def __getattr__(name: str):  # type: ignore
    """Lazy import to avoid loading all dependencies."""
    if name == "EpisodicMemory":

        return EpisodicMemory
    elif name == "EventHorizonMemory":

        return EventHorizonMemory
    elif name == "HolographicProjection":

        return HolographicProjection
    elif name == "HolographicSurface":

        return HolographicSurface
    elif name == "SoftHair":

        return SoftHair
    elif name == "SoftHairEncoder":

        return SoftHairEncoder
    elif name == "SoftHairMemory":

        return SoftHairMemory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "EpisodicMemory",
    "EventHorizonMemory",
    "HolographicProjection",
    "HolographicSurface",
    "SoftHair",
    "SoftHairEncoder",
    "SoftHairMemory",
]
