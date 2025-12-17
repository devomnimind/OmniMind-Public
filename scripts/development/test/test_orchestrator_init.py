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

import sys
import os
from pathlib import Path

# Adicionar raiz ao path
sys.path.insert(0, str(Path.cwd()))

print("Importing OrchestratorAgent...")
from src.agents.orchestrator_agent import OrchestratorAgent

print("Initializing OrchestratorAgent...")
try:
    orch = OrchestratorAgent("config/agent_config.yaml")
    print("OrchestratorAgent initialized successfully!")
except Exception as e:
    print(f"Failed to initialize: {e}")
    import traceback

    traceback.print_exc()
