from .architect_agent import ArchitectAgent
from .code_agent import CodeAgent
from .debug_agent import DebugAgent
from .orchestrator_agent import AgentMode, OrchestratorAgent
from .react_agent import AgentState, ReactAgent
from .reviewer_agent import ReviewerAgent

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
OmniMind Agents - Multi-Agent System with Specialized Roles

Agents:
- ReactAgent: Base agent with Think→Act→Observe loop
- CodeAgent (💻): Code development specialist
- ArchitectAgent (🏗️): Architecture & planning specialist
- DebugAgent (🪲): Debugging & diagnosis specialist
- ReviewerAgent (⭐): Code review with RLAIF scoring
- OrchestratorAgent (🪃): Master coordinator

Usage:
    from src.agents import OrchestratorAgent

    orchestrator = OrchestratorAgent("config/agent_config.yaml")
    result = orchestrator.run_orchestrated_task("Build authentication system")
"""


__all__ = [
    "ReactAgent",
    "AgentState",
    "CodeAgent",
    "ArchitectAgent",
    "DebugAgent",
    "ReviewerAgent",
    "OrchestratorAgent",
    "AgentMode",
]
