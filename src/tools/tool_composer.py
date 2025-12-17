"""
Tool Composer - Composição de Ferramentas em Pipeline

Permite compor múltiplas ferramentas em pipeline, otimizar ordem de execução
e validar composições antes de executar.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .omnimind_tools import ToolsFramework
from .tool_base import ToolCategory

logger = logging.getLogger(__name__)


class CompositionType(Enum):
    """Tipos de composição de ferramentas."""

    SEQUENTIAL = "sequential"  # Execução sequencial (pipeline)
    PARALLEL = "parallel"  # Execução paralela
    CONDITIONAL = "conditional"  # Execução condicional
    LOOP = "loop"  # Execução em loop


@dataclass
class ToolComposition:
    """Composição de ferramentas."""

    composition_id: str
    tool_names: List[str]
    composition_type: CompositionType
    dependencies: Dict[str, List[str]]  # tool_name -> [dependencies]
    execution_order: List[str]  # Ordem otimizada de execução
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionResult:
    """Resultado da execução de uma composição."""

    composition_id: str
    success: bool
    results: Dict[str, Any]  # tool_name -> result
    execution_order: List[str]
    total_time: float
    errors: List[Dict[str, Any]] = field(default_factory=list)


class ToolComposer:
    """
    Compõe ferramentas em pipelines e otimiza execução.

    Características:
    - Composição sequencial (pipeline)
    - Composição paralela
    - Otimização de ordem de execução
    - Validação de dependências
    - Detecção de ciclos
    """

    def __init__(self, tools_framework: ToolsFramework):
        """
        Inicializa ToolComposer.

        Args:
            tools_framework: Instância de ToolsFramework
        """
        self.tools_framework = tools_framework
        self.compositions: Dict[str, ToolComposition] = {}

        logger.info("ToolComposer inicializado")

    def compose_tools(
        self,
        tool_names: List[str],
        composition_type: CompositionType = CompositionType.SEQUENTIAL,
        dependencies: Optional[Dict[str, List[str]]] = None,
        composition_id: Optional[str] = None,
    ) -> ToolComposition:
        """
        Compõe ferramentas em pipeline.

        Args:
            tool_names: Lista de nomes de ferramentas
            composition_type: Tipo de composição
            dependencies: Dependências entre ferramentas (opcional)
            composition_id: ID da composição (gerado se não fornecido)

        Returns:
            ToolComposition
        """
        # Validar ferramentas
        invalid_tools = [name for name in tool_names if name not in self.tools_framework.tools]
        if invalid_tools:
            raise ValueError(f"Ferramentas inválidas: {invalid_tools}")

        # Gerar ID se não fornecido
        if composition_id is None:
            composition_id = f"composition_{len(self.compositions)}"

        # Detectar dependências automaticamente se não fornecidas
        if dependencies is None:
            dependencies = self._detect_dependencies(tool_names)

        # Otimizar ordem de execução
        execution_order = self.optimize_composition(tool_names, dependencies)

        composition = ToolComposition(
            composition_id=composition_id,
            tool_names=tool_names,
            composition_type=composition_type,
            dependencies=dependencies,
            execution_order=execution_order,
        )

        self.compositions[composition_id] = composition

        logger.info(
            f"Composição criada: {composition_id} "
            f"({len(tool_names)} ferramentas, tipo: {composition_type.value})"
        )

        return composition

    def _detect_dependencies(self, tool_names: List[str]) -> Dict[str, List[str]]:
        """
        Detecta dependências entre ferramentas automaticamente.

        Args:
            tool_names: Lista de nomes de ferramentas

        Returns:
            Dict de dependências
        """
        dependencies: Dict[str, List[str]] = {}

        # Heurísticas simples baseadas em categorias e nomes
        for tool_name in tool_names:
            tool = self.tools_framework.tools[tool_name]
            deps: List[str] = []

            # Ferramentas de ação geralmente dependem de percepção
            if tool.category == ToolCategory.ACTION:
                # Buscar ferramentas de percepção que podem ser pré-requisito
                for other_name in tool_names:
                    if other_name != tool_name:
                        other_tool = self.tools_framework.tools[other_name]
                        if other_tool.category == ToolCategory.PERCEPTION:
                            # Heurística: read_file geralmente precede write_to_file
                            if "read" in other_name.lower() and "write" in tool_name.lower():
                                deps.append(other_name)

            dependencies[tool_name] = deps

        return dependencies

    def optimize_composition(
        self, tool_names: List[str], dependencies: Dict[str, List[str]]
    ) -> List[str]:
        """
        Otimiza ordem de execução baseado em dependências.

        Args:
            tool_names: Lista de ferramentas
            dependencies: Dependências entre ferramentas

        Returns:
            Lista ordenada de nomes de ferramentas
        """
        # Topological sort
        in_degree: Dict[str, int] = {name: 0 for name in tool_names}
        graph: Dict[str, List[str]] = {name: [] for name in tool_names}

        # Construir grafo
        for tool_name in tool_names:
            for dep in dependencies.get(tool_name, []):
                if dep in tool_names:
                    graph[dep].append(tool_name)
                    in_degree[tool_name] += 1

        # Detectar ciclos
        if self._has_cycle(graph, tool_names):
            logger.warning("Ciclo detectado nas dependências. Usando ordem original.")
            return tool_names.copy()

        # Topological sort
        queue: List[str] = [name for name in tool_names if in_degree[name] == 0]
        result: List[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Adicionar ferramentas não processadas (sem dependências)
        for tool_name in tool_names:
            if tool_name not in result:
                result.append(tool_name)

        return result

    def _has_cycle(self, graph: Dict[str, List[str]], nodes: List[str]) -> bool:
        """
        Detecta se há ciclo no grafo de dependências.

        Args:
            graph: Grafo de dependências
            nodes: Lista de nós

        Returns:
            True se há ciclo
        """
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in nodes:
            if node not in visited:
                if dfs(node):
                    return True

        return False

    def validate_composition(self, composition: ToolComposition) -> Tuple[bool, List[str]]:
        """
        Valida uma composição antes de executar.

        Args:
            composition: Composição a validar

        Returns:
            Tupla (is_valid, errors)
        """
        errors: List[str] = []

        # Verificar se todas as ferramentas existem
        for tool_name in composition.tool_names:
            if tool_name not in self.tools_framework.tools:
                errors.append(f"Ferramenta não encontrada: {tool_name}")

        # Verificar dependências
        for tool_name, deps in composition.dependencies.items():
            if tool_name not in composition.tool_names:
                continue
            for dep in deps:
                if dep not in composition.tool_names:
                    errors.append(f"Dependência '{dep}' de '{tool_name}' não está na composição")

        # Verificar se ordem de execução está correta
        if len(composition.execution_order) != len(composition.tool_names):
            errors.append("Ordem de execução não contém todas as ferramentas")

        # Verificar se não há duplicatas
        if len(composition.execution_order) != len(set(composition.execution_order)):
            errors.append("Ordem de execução contém duplicatas")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"Composição {composition.composition_id} validada com sucesso")
        else:
            logger.warning(f"Composição {composition.composition_id} inválida: {errors}")

        return is_valid, errors

    def execute_composition(
        self,
        composition_id: str,
        inputs: Optional[Dict[str, Dict[str, Any]]] = None,
        timeout: float = 300.0,
    ) -> CompositionResult:
        """
        Executa uma composição de ferramentas.

        Args:
            composition_id: ID da composição
            inputs: Inputs para cada ferramenta {tool_name: {args}}
            timeout: Timeout total em segundos

        Returns:
            CompositionResult
        """
        if composition_id not in self.compositions:
            raise ValueError(f"Composição não encontrada: {composition_id}")

        composition = self.compositions[composition_id]

        # Validar antes de executar
        is_valid, errors = self.validate_composition(composition)
        if not is_valid:
            return CompositionResult(
                composition_id=composition_id,
                success=False,
                results={},
                execution_order=composition.execution_order,
                total_time=0.0,
                errors=[{"validation": errors}],
            )

        import time

        start_time = time.time()
        results: Dict[str, Any] = {}
        execution_errors: List[Dict[str, Any]] = []

        # Executar na ordem otimizada
        for tool_name in composition.execution_order:
            try:
                # Obter inputs para esta ferramenta
                tool_inputs = inputs.get(tool_name, {}) if inputs else {}

                # Executar ferramenta
                result = self.tools_framework.execute_tool(tool_name, **tool_inputs)
                results[tool_name] = result

                logger.debug(f"Ferramenta {tool_name} executada com sucesso")

            except Exception as e:
                error_info = {
                    "tool": tool_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
                execution_errors.append(error_info)
                results[tool_name] = {"error": str(e)}

                logger.error(f"Erro ao executar {tool_name}: {e}")

                # Se composição é sequencial e há erro, pode parar
                if composition.composition_type == CompositionType.SEQUENTIAL:
                    break

        total_time = time.time() - start_time
        success = len(execution_errors) == 0

        logger.info(
            f"Composição {composition_id} executada: "
            f"success={success}, time={total_time:.2f}s, errors={len(execution_errors)}"
        )

        return CompositionResult(
            composition_id=composition_id,
            success=success,
            results=results,
            execution_order=composition.execution_order,
            total_time=total_time,
            errors=execution_errors,
        )

    def get_composition(self, composition_id: str) -> Optional[ToolComposition]:
        """Retorna composição por ID."""
        return self.compositions.get(composition_id)

    def list_compositions(self) -> List[str]:
        """Lista IDs de todas as composições."""
        return list(self.compositions.keys())
