#!/usr/bin/env python3
"""
DebugAgent - Agente de diagnóstico e debug
Modo: debug (🪲)

Função: Diagnostico avançado, isolamento de bugs, identificação de causas
Ferramentas: read, search, inspect_context, execute_command (limitado), diagnose_error
Quando usar: Build quebrado, edge cases, race conditions
"""

import json
from typing import Any, Dict, List

from ..memory.episodic_memory import SimilarEpisode
from ..tools.omnimind_tools import ToolCategory, ToolsFramework
from .react_agent import AgentState, ReactAgent


class DebugAgent(ReactAgent):
    """Agente especializado em diagnóstico e debugging"""

    def __init__(self, config_path: str) -> None:
        super().__init__(config_path)
        self.tools_framework = ToolsFramework()
        self.mode = "debug"

        # Ferramentas permitidas
        self.allowed_tool_categories: List[ToolCategory] = [
            ToolCategory.PERCEPTION,
            ToolCategory.REASONING,  # analyze_code, diagnose_error
        ]

        # Comandos permitidos (read-only e diagnóstico)
        self.allowed_commands: List[str] = [
            "ls",
            "cat",
            "grep",
            "find",
            "python3 -m pytest",
            "git status",
        ]

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        try:
            # Bloquear escrita
            if action in ["write_to_file", "update_file", "insert_content"]:
                return "DebugAgent cannot modify files. Delegate to CodeAgent for fixes."

            # Comandos limitados
            if action == "execute_command":
                command = args.get("command", "")
                if not any(cmd in command for cmd in self.allowed_commands):
                    return f"Command not allowed. Debug commands: {self.allowed_commands}"

            if action not in self.tools_framework.tools:
                return f"Unknown tool: {action}"

            result: Any = self.tools_framework.execute_tool(action, **args)
            return json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
        except Exception as exc:
            return f"Error: {str(exc)}"

    def _think_node(self, state: AgentState) -> AgentState:
        similar_episodes: List[SimilarEpisode] = self.memory.search_similar(
            state["current_task"], top_k=3
        )
        system_status = self.tools_framework.execute_tool("inspect_context")
        system_status_str = (
            json.dumps(system_status, indent=2)
            if isinstance(system_status, dict)
            else str(system_status)
        )
        memory_str = "\n".join(
            [f"- {ep['task']}: {ep['result'][:120]}..." for ep in (similar_episodes or [])]
        )

        prompt = f"""You are DebugAgent 🪲, an expert debugger and diagnostician.

TASK: {state['current_task']}
MODE: {self.mode} (debugging & diagnosis)
ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

CAPABILITIES:
- Read and analyze code
- Search for patterns and errors
- Inspect system context
- Diagnose errors with suggestions
- Execute diagnostic commands (read-only)

CONSTRAINTS:
- Cannot modify files (delegate to CodeAgent)
- Limited command execution (diagnostic only)

AVAILABLE TOOLS:
- read_file, list_files, search_files, codebase_search
- inspect_context: System status
- analyze_code: Code quality analysis
- diagnose_error: Error diagnosis with suggestions
- execute_command: Limited to {self.allowed_commands}

PREVIOUS OBSERVATIONS:
{chr(10).join([f"- {o[:150]}" for o in state['observations']]) if state['observations'] else "None"}

SIMILAR EPISODES:
{memory_str or "No similar debug sessions recorded."}

SYSTEM STATUS SNAPSHOT:
{system_status_str or "Unavailable"}

Focus on:
1. Identifying root causes
2. Analyzing error patterns
3. Suggesting fixes
4. Locating edge cases

REASONING: <diagnostic analysis>
ACTION: <tool_name>
ARGS: <json dict>

Response:"""

        response = self.llm.invoke(prompt)
        state["reasoning_chain"].append(response)
        state["messages"].append(f"[THINK-DEBUG] {response[:500]}...")
        return state


__all__ = ["DebugAgent"]
