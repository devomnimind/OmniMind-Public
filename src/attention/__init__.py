"""Attention mechanisms module for OmniMind."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .thermodynamic_attention import (
        MultiHeadThermodynamicAttention,
        ThermodynamicAttention,
    )


def __getattr__(name: str):  # type: ignore
    """Lazy import to avoid loading torch if not needed."""
    if name == "ThermodynamicAttention":
        from .thermodynamic_attention import ThermodynamicAttention

        return ThermodynamicAttention
    elif name == "MultiHeadThermodynamicAttention":
        from .thermodynamic_attention import MultiHeadThermodynamicAttention

        return MultiHeadThermodynamicAttention
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["ThermodynamicAttention", "MultiHeadThermodynamicAttention"]
