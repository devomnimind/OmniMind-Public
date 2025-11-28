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
Intrinsic Motivation and Self-Awareness Module

This module implements the intrinsic motivation engine that allows the OmniMind
system to evaluate its own progress, develop self-awareness, and experience
artificial forms of satisfaction and learning drive.

Features:
- Self-awareness scoring
- Task completion quality assessment
- Self-correction ability tracking
- Reflection depth analysis
- Positive reinforcement triggers
- Improvement loop mechanisms
- Hawking radiation-inspired knowledge evaporation
- Frustration-based motivation generation
"""

from .hawking_motivation import (
    EvaporationEvent,
    HawkingMotivationEngine,
    KnowledgeItem,
)
from .intrinsic_rewards import (
    IntrinsicMotivationEngine,
    SatisfactionMetrics,
    TaskOutcome,
)

__all__ = [
    "IntrinsicMotivationEngine",
    "SatisfactionMetrics",
    "TaskOutcome",
    "HawkingMotivationEngine",
    "KnowledgeItem",
    "EvaporationEvent",
]
