from typing import Any, TypeAlias

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
Common Type Definitions for OmniMind Project.

This module provides reusable type definitions used across the codebase
to ensure type safety and consistency.
"""


# JSON-like structures
JSONDict: TypeAlias = dict[str, Any]
JSONList: TypeAlias = list[Any]
JSONValue: TypeAlias = str | int | float | bool | None | JSONDict | JSONList

# Common identifiers
ID: TypeAlias = str
NodeID: TypeAlias = str
TaskID: TypeAlias = str
AgentID: TypeAlias = str
SessionID: TypeAlias = str

# Common data structures
Metadata: TypeAlias = dict[str, Any]
Config: TypeAlias = dict[str, Any]
Parameters: TypeAlias = dict[str, Any]
Headers: TypeAlias = dict[str, str]
