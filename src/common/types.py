"""
Common Type Definitions for OmniMind Project.

This module provides reusable type definitions used across the codebase
to ensure type safety and consistency.
"""

from typing import Any, TypeAlias

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
