from __future__ import annotations

"""ArchitectAgent specialized in documentation and planning."""

import json
from pathlib import Path
from typing import Any, Dict, List

from .react_agent import ReactAgent, AgentState
from ..memory.episodic_memory import SimilarEpisode
from ..tools.omnimind_tools import ToolsFramework, ToolCategory


class ArchitectAgent(ReactAgent):
    """
    Agente especializado em arquitetura e planejamento.

    Restrições de segurança:
    - Pode ler qualquer arquivo
    - Pode escrever APENAS .md, .yaml, .json, .txt
    - NÃO pode executar comandos arbitrários
    - Foco em documentação e design
    """

    def __init__(self, config_path: str) -> None:
        super().__init__(config_path)

        self.tools_framework = ToolsFramework()
        self.mode = "architect"

        # Extensões permitidas para escrita
        self.writable_extensions: List[str] = [
            ".md",
            ".yaml",
            ".yml",
            ".json",
            ".txt",
            ".rst",
        ]

        # Categorias permitidas
        self.allowed_tool_categories: List[ToolCategory] = [
            ToolCategory.PERCEPTION,  # Ler tudo
            ToolCategory.ORCHESTRATION,  # Planejar
        ]

    def _validate_write_permission(self, filepath: str) -> bool:
        """Valida se pode escrever em arquivo (só documentação)"""
        ext = Path(filepath).suffix.lower()
        return ext in self.writable_extensions

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """Executa ação com restrições de arquitetura"""
        allowed_docs = ", ".join(self.writable_extensions)
        try:
            # Bloquear escrita em arquivos de código
            if action in [
                "write_to_file",
                "update_file",
                "insert_content",
                "apply_diff",
            ]:
                filepath = args.get("filepath", args.get("path", ""))
                if not self._validate_write_permission(filepath):
                    return (
                        "ArchitectAgent can only edit documentation files "
                        f"({allowed_docs}). Cannot edit: {filepath}"
                    )

            # Bloquear execução de comandos
            if action == "execute_command":
                return (
                    "ArchitectAgent cannot execute commands. "
                    "Delegate to CodeAgent or DebugAgent."
                )

            # Verificar ferramenta existe
            if action not in self.tools_framework.tools:
                return f"Unknown tool: {action}"

            # Verificar categoria
            tool = self.tools_framework.tools[action]
            if tool.category not in self.allowed_tool_categories:
                return f"Tool '{action}' not allowed in architect mode"

            # Executar
            result: Any = self.tools_framework.execute_tool(action, **args)

            if isinstance(result, (dict, list)):
                return json.dumps(result, indent=2)
            return str(result)

        except Exception as exc:
            return f"Error: {str(exc)}"

    def _think_node(self, state: AgentState) -> AgentState:
        """THINK específico para arquitetura"""
        similar_episodes: List[SimilarEpisode] = self.memory.search_similar(
            state["current_task"], top_k=3
        )
        system_status = self.tools_framework.execute_tool("inspect_context")
        system_status_str = (
            json.dumps(system_status, indent=2)
            if isinstance(system_status, dict)
            else str(system_status)
        )

        memory_str = ""
        if similar_episodes:
            memory_str = "\n".join(
                [
                    f"{i+1}. {ep['task']} → {ep['result'][:100]}"
                    for i, ep in enumerate(similar_episodes)
                ]
            )

        if state["actions_taken"]:
            actions_lines = [
                f"- {action['action']}({action.get('args', {})})"
                for action in state["actions_taken"]
            ]
            previous_actions = "\n".join(actions_lines)
        else:
            previous_actions = "None"

        allowed_docs = ", ".join(self.writable_extensions)

        prompt = f"""You are ArchitectAgent 🏗️, a system architect and technical planner.

TASK: {state['current_task']}

MODE: {self.mode} (architecture & planning)
ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

CONSTRAINTS:
- You can READ any file
- You can WRITE only documentation: {allowed_docs}
- You CANNOT execute code or commands
- Focus on design, specs, documentation

MEMORY:
{memory_str or "No similar architecture experiences."}

PREVIOUS ACTIONS:
{previous_actions}

AVAILABLE TOOLS:
- read_file: Read any file
- search_files: Find files
- list_files: List directory contents
- codebase_search: Search in code
- write_to_file: Write documentation (only {allowed_docs})
- update_file: Update documentation
- plan_task: Create execution plan

As ArchitectAgent, focus on:
1. Analyzing system structure
2. Documenting architecture decisions
3. Creating technical specs
4. Planning migrations and designs
5. Writing README, ARCHITECTURE.md, etc.

SYSTEM STATUS:
{system_status_str or "No system status info available."}

REASONING: <your architectural analysis>
ACTION: <tool_name>
ARGS: <json dict>

Your response:"""

        response = self.llm.invoke(prompt)
        state["reasoning_chain"].append(response)
        state["messages"].append(f"[THINK-ARCHITECT] {response[:500]}...")

        return state

    def analyze_dependencies(self, directory: str) -> Dict[str, Any]:
        """
        Analisa dependências de um projeto.

        Args:
            directory: Diretório do projeto

        Returns:
            Dict com análise de dependências
        """
        dependencies: Dict[str, List[str]] = {}
        dir_path = Path(directory)

        # Procurar por requirements.txt
        req_file = dir_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, "r") as f:
                dependencies["python"] = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]

        # Procurar por package.json
        pkg_file = dir_path / "package.json"
        if pkg_file.exists():
            with open(pkg_file, "r") as f:
                pkg_data = json.load(f)
                dependencies["npm"] = list(pkg_data.get("dependencies", {}).keys())

        return {
            "directory": directory,
            "dependencies": dependencies,
            "total_deps": sum(len(deps) for deps in dependencies.values()),
        }

    def create_architecture_diagram(
        self, components: List[str], connections: List[tuple[str, str]]
    ) -> str:
        """
        Cria diagrama de arquitetura em formato Mermaid.

        Args:
            components: Lista de componentes
            connections: Lista de tuplas (origem, destino)

        Returns:
            Diagrama Mermaid em formato texto
        """
        lines = ["```mermaid", "graph TD"]

        # Adicionar componentes
        for i, comp in enumerate(components):
            lines.append(f"    {chr(65+i)}[{comp}]")

        # Adicionar conexões
        comp_map = {comp: chr(65 + i) for i, comp in enumerate(components)}
        for src, dst in connections:
            if src in comp_map and dst in comp_map:
                lines.append(f"    {comp_map[src]} --> {comp_map[dst]}")

        lines.append("```")
        return "\n".join(lines)

    def generate_spec_document(
        self,
        title: str,
        sections: Dict[str, str],
        output_path: str,
    ) -> Dict[str, Any]:
        """
        Gera documento de especificação técnica.

        Args:
            title: Título do documento
            sections: Dict de seções {nome: conteúdo}
            output_path: Caminho para salvar documento

        Returns:
            Dict com resultado da operação
        """
        if not self._validate_write_permission(output_path):
            return {
                "success": False,
                "error": f"Cannot write to {output_path}. Must be documentation file.",
            }

        # Gerar markdown
        lines = [f"# {title}", ""]

        for section_name, content in sections.items():
            lines.append(f"## {section_name}")
            lines.append("")
            lines.append(content)
            lines.append("")

        content = "\n".join(lines)

        # Salvar arquivo
        try:
            with open(output_path, "w") as f:
                f.write(content)
            return {
                "success": True,
                "path": output_path,
                "size": len(content),
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }


__all__ = ["ArchitectAgent"]
