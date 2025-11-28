#!/usr/bin/env python3
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

sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.agents.orchestrator_agent import OrchestratorAgent

    print("Import successful")
    orch = OrchestratorAgent("config/agent_config.yaml")
    print("Orchestrator created")
    # Test with a task that should definitely fail
    result = orch.run_orchestrated_task(
        "Execute a command that does not exist: nonexistent_command_xyz",
        max_iterations_per_subtask=1,
    )
    print(
        f'Task completed with success: {result.get("success", False) if isinstance(result, dict) else False}'
    )
    print(
        f'Execution details: {len(result.get("execution", {}).get("subtask_results", [])) if isinstance(result, dict) else 0} subtasks'
    )

    # Print detailed results
    execution = result.get("execution", {}) if isinstance(result, dict) else {}
    for i, subtask_result in enumerate(
        execution.get("subtask_results", []) if isinstance(execution, dict) else []
    ):
        print(
            f'Subtask {i+1}: {subtask_result.get("description", "Unknown") if isinstance(subtask_result, dict) else "Invalid result"}'
        )
        print(
            f'  Completed: {subtask_result.get("completed", False) if isinstance(subtask_result, dict) else False}'
        )
        print(
            f'  Summary: {subtask_result.get("summary", "No summary")[:100] if isinstance(subtask_result, dict) else "Invalid result"}...'
        )

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
