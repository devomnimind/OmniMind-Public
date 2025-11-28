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

# tests/autopoietic/test_system_boundary.py
"""Tests for the SystemBoundary module.

Ensures registration, internal checks, and policy enforcement work as expected.
"""

import pytest

from src.autopoietic.system_boundary import SystemBoundary


def test_register_and_is_internal() -> None:
    sb = SystemBoundary()
    sb.register("comp_internal", internal=True)
    sb.register("comp_external", internal=False)
    assert sb.is_internal("comp_internal") is True
    assert sb.is_internal("comp_external") is False
    # Unregistered component defaults to False
    assert sb.is_internal("unknown") is False


def test_list_internal() -> None:
    sb = SystemBoundary()
    sb.register("a", internal=True)
    sb.register("b", internal=False)
    sb.register("c", internal=True)
    internal_set = sb.list_internal()
    assert internal_set == {"a", "c"}


def test_enforce_policy_allows_internal() -> None:
    sb = SystemBoundary()
    sb.register("good", internal=True)
    # Should not raise
    sb.enforce_policy("good")


def test_enforce_policy_blocks_external() -> None:
    sb = SystemBoundary()
    sb.register("bad", internal=False)
    with pytest.raises(PermissionError):
        sb.enforce_policy("bad")
