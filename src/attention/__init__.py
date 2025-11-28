        from .thermodynamic_attention import ThermodynamicAttention
        from .thermodynamic_attention import MultiHeadThermodynamicAttention

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

        return ThermodynamicAttention
    elif name == "MultiHeadThermodynamicAttention":

        return MultiHeadThermodynamicAttention
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["ThermodynamicAttention", "MultiHeadThermodynamicAttention"]
