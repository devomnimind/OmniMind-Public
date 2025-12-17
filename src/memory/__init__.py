"""Memory module for OmniMind agent system."""

# Lazy imports to avoid dependency issues
import warnings
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
        warnings.warn(
            "⚠️ DEPRECATED: EpisodicMemory is deprecated. "
            "Use NarrativeHistory for Lacanian memory construction. "
            "EpisodicMemory is only kept as internal backend for NarrativeHistory.",
            DeprecationWarning,
            stacklevel=2,
        )
        from .episodic_memory import EpisodicMemory

        return EpisodicMemory
    elif name == "EventHorizonMemory":
        from .holographic_memory import EventHorizonMemory

        return EventHorizonMemory
    elif name == "HolographicProjection":
        from .holographic_memory import HolographicProjection

        return HolographicProjection
    elif name == "HolographicSurface":
        from .holographic_memory import HolographicSurface

        return HolographicSurface
    elif name == "SoftHair":
        from .soft_hair_encoding import SoftHair

        return SoftHair
    elif name == "SoftHairEncoder":
        from .soft_hair_encoding import SoftHairEncoder

        return SoftHairEncoder
    elif name == "SoftHairMemory":
        from .soft_hair_encoding import SoftHairMemory

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
