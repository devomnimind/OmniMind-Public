#!/usr/bin/env python3
"""
CodeAgent - Agente especializado em desenvolvimento de código
Modo: code (💻)

Função: Desenvolver, editar, refatorar código com total liberdade
Ferramentas: read, edit, browser, command, mcp (todas)
Quando usar: Implementar features, rodar testes, corrigir bugs, instalar dependências

Integração: Recebe comandos do Orchestrator e resultados de Debug/Ask
"""

import json
from typing import Any, Dict, List

from .react_agent import ReactAgent, AgentState
from ..memory.episodic_memory import SimilarEpisode
from ..tools.omnimind_tools import ToolsFramework, ToolCategory
from ..tools.ast_parser import ASTParser, CodeStructure


class CodeAgent(ReactAgent):
    """
    Agente especializado em desenvolvimento de código.

    Tem acesso completo a todas as ferramentas de:
    - Percepção: read, search, list, inspect, codebase_search
    - Ação: write, update, execute, apply_diff, insert
    - Integração MCP: use_mcp_tool, access_mcp_resource
    - Raciocínio: analyze_code
    """

    def __init__(self, config_path: str) -> None:
        """Inicializa CodeAgent com framework de ferramentas expandido"""
        super().__init__(config_path)

        # Inicializar framework de ferramentas
        self.tools_framework = ToolsFramework()

        # Inicializar AST parser para análise avançada de código
        self.ast_parser = ASTParser()

        # Modo de operação
        self.mode = "code"

        # Ferramentas permitidas para CodeAgent (todas)
        self.allowed_tool_categories: List[ToolCategory] = [
            ToolCategory.PERCEPTION,
            ToolCategory.ACTION,
            ToolCategory.INTEGRATION,
            ToolCategory.REASONING,
        ]

        # Histórico de operações de código
        self.code_history: List[Dict[str, Any]] = []
        
        # Cache de análises AST
        self._ast_cache: Dict[str, CodeStructure] = {}

    def _get_available_tools_description(self) -> str:
        """Retorna descrição de ferramentas disponíveis"""
        tools_by_category: Dict[str, List[str]] = {}

        for (
            tool_name,
            tool_category,
        ) in self.tools_framework.get_available_tools().items():
            if tool_category not in tools_by_category:
                tools_by_category[tool_category] = []
            tools_by_category[tool_category].append(tool_name)

        description = "AVAILABLE TOOLS:\n\n"

        for category in self.allowed_tool_categories:
            cat_name = category.value
            if cat_name in tools_by_category:
                description += f"[{cat_name.upper()}]\n"
                for tool in tools_by_category[cat_name]:
                    description += f"  - {tool}\n"
                description += "\n"

        description += """
TOOL USAGE EXAMPLES:
  read_file(filepath="src/main.py")
  write_to_file(filepath="output.py", content="code here")
  execute_command(command="python test.py")
  codebase_search(query="def main", directory=".")
  analyze_code(filepath="src/app.py")
  update_file(filepath="file.py", old_content="old", new_content="new")
  list_code_definitions(filepath="module.py")
"""

        return description

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """
        Executa ação usando ToolsFramework.
        Sobrescreve método da classe base para usar novas ferramentas.
        """
        try:
            # Verificar se ferramenta existe
            if action not in self.tools_framework.tools:
                available = ", ".join(self.tools_framework.tools.keys())
                return f"Unknown tool: {action}. Available: {available}"

            # Verificar categoria permitida
            tool = self.tools_framework.tools[action]
            if tool.category not in self.allowed_tool_categories:
                return f"Tool '{action}' not allowed in {self.mode} mode"

            # Executar ferramenta
            result: Any = self.tools_framework.execute_tool(action, **args)

            # Registrar operação
            self.code_history.append(
                {
                    "action": action,
                    "args": args,
                    "result": str(result)[:200],
                    "timestamp": self._timestamp(),
                }
            )

            # Formatar resultado
            if isinstance(result, dict):
                return json.dumps(result, indent=2)
            elif isinstance(result, list):
                return json.dumps(result, indent=2)
            elif isinstance(result, bool):
                return f"{'Success' if result else 'Failed'}"
            else:
                return str(result)

        except Exception as exc:
            return f"Error executing {action}: {str(exc)}"

    def _think_node(self, state: AgentState) -> AgentState:
        """
        THINK: Geração de raciocínio específica para código.
        Sobrescreve para adicionar contexto de CodeAgent.
        """
        # Buscar experiências similares
        similar_episodes: List[SimilarEpisode] = self.memory.search_similar(
            state["current_task"], top_k=3, min_reward=0.5
        )

        # Obter status do sistema
        system_status = self.tools_framework.execute_tool("inspect_context")
        state["system_status"] = system_status

        # Formatar contexto de memória
        memory_str = ""
        if similar_episodes:
            memory_str = "\n".join(
                [
                    f"{i+1}. Task: {ep['task']}\n"
                    f"   Action: {ep['action']}\n"
                    f"   Result: {ep['result'][:200]}..."
                    for i, ep in enumerate(similar_episodes)
                ]
            )

        # Construir prompt específico para código
        prompt = f"""You are CodeAgent 💻, an expert software developer with full access to code tools.

CURRENT TASK: {state['current_task']}

MODE: {self.mode} (code development)
ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

MEMORY (Similar past coding experiences):
{memory_str if memory_str else "No similar experiences found."}

SYSTEM STATUS:
CPU: {system_status.get('cpu_percent', 'N/A')}%
RAM: {system_status.get('memory_percent', 'N/A')}%
CWD: {system_status.get('cwd', 'N/A')}

PREVIOUS ACTIONS:
{chr(10).join([f"- {a['action']}({a.get('args', {})})" for a in state['actions_taken']]) if state['actions_taken'] else "None"}

PREVIOUS OBSERVATIONS:
{chr(10).join([f"- {o[:150]}" for o in state['observations']]) if state['observations'] else "None"}

{self._get_available_tools_description()}

INSTRUCTIONS:
As CodeAgent, you can:
1. Read and analyze code files
2. Write and update code
3. Execute tests and commands
4. Search codebase
5. Analyze code quality
6. Apply diffs and patches

Think step-by-step about the coding task. Then specify:

REASONING: <your detailed thinking process>
ACTION: <tool_name>
ARGS: <json dict of arguments>

Your response:"""

        # Gerar raciocínio via LLM
        response = self.llm.invoke(prompt)
        state["reasoning_chain"].append(response)
        state["messages"].append(f"[THINK-CODE] {response[:500]}...")

        return state

    def run_code_task(self, task: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Executa tarefa de código com rastreamento específico.
        Wrapper sobre run() da classe base.
        """
        result = self.run(task, max_iterations)

        # Adicionar estatísticas de código
        result["mode"] = self.mode
        result["code_operations"] = len(self.code_history)
        result["tools_used"] = list(set([op["action"] for op in self.code_history]))

        return result

    def get_code_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de operações de código"""
        return {
            "total_operations": len(self.code_history),
            "by_action": self._count_actions(),
            "recent": self.code_history[-5:] if self.code_history else [],
        }

    def _count_actions(self) -> Dict[str, int]:
        """Conta ações por tipo"""
        counts: Dict[str, int] = {}
        for op in self.code_history:
            action = op["action"]
            counts[action] = counts.get(action, 0) + 1
        return counts

    def analyze_code_structure(self, filepath: str) -> Dict[str, Any]:
        """
        Analisa estrutura de código Python usando AST.

        Args:
            filepath: Caminho para arquivo Python

        Returns:
            Dict com análise completa (classes, funções, imports, complexidade)
        """
        # Verificar cache
        if filepath in self._ast_cache:
            structure = self._ast_cache[filepath]
        else:
            structure = self.ast_parser.parse_file(filepath)
            if structure:
                self._ast_cache[filepath] = structure

        if not structure:
            return {"error": f"Failed to parse {filepath}"}

        return {
            "filepath": structure.filepath,
            "classes": [
                {
                    "name": c.name,
                    "lines": f"{c.line_start}-{c.line_end}",
                    "docstring": c.docstring,
                    "bases": c.bases,
                }
                for c in structure.classes
            ],
            "functions": [
                {
                    "name": f.name,
                    "lines": f"{f.line_start}-{f.line_end}",
                    "parameters": f.parameters,
                    "return_type": f.return_type,
                    "docstring": f.docstring,
                }
                for f in structure.functions
            ],
            "imports": [i.name for i in structure.imports],
            "dependencies": list(structure.dependencies),
            "complexity": structure.complexity,
            "lines_of_code": structure.lines_of_code,
        }

    def validate_code_syntax(self, code: str) -> Dict[str, Any]:
        """
        Valida sintaxe de código Python.

        Args:
            code: Código-fonte Python

        Returns:
            Dict com resultado da validação
        """
        is_valid, error = self.ast_parser.validate_syntax(code)
        return {
            "valid": is_valid,
            "error": error,
            "timestamp": self._timestamp(),
        }

    def analyze_code_security(self, code: str) -> Dict[str, Any]:
        """
        Analisa código para problemas de segurança.

        Args:
            code: Código-fonte Python

        Returns:
            Dict com avisos de segurança
        """
        warnings = self.ast_parser.analyze_security_issues(code)
        return {
            "warnings": warnings,
            "safe": len(warnings) == 0,
            "severity": "high" if any("eval" in w or "exec" in w for w in warnings) else "medium",
            "timestamp": self._timestamp(),
        }

    def generate_code_skeleton(
        self,
        class_name: str,
        methods: List[tuple[str, List[str], str]],
        docstring: str = "",
    ) -> str:
        """
        Gera esqueleto de classe Python.

        Args:
            class_name: Nome da classe
            methods: Lista de (nome, parâmetros, tipo_retorno)
            docstring: Docstring da classe

        Returns:
            Código-fonte da classe gerada
        """
        return self.ast_parser.generate_skeleton(class_name, methods, docstring)


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["CodeAgent"]
