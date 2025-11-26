#!/usr/bin/env python3
"""
AST Parser Tool - Análise e Geração de Código Python usando AST

Fornece funcionalidades avançadas de:
- Parsing de código Python em AST
- Análise de estrutura de código
- Validação de sintaxe
- Extração de definições (classes, funções, variáveis)
- Análise de dependências
- Geração de código seguro
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class CodeElement:
    """Representa um elemento de código (classe, função, etc.)"""

    name: str
    type: str  # "class", "function", "variable", "import"
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)  # Para classes


@dataclass
class CodeStructure:
    """Estrutura completa de um arquivo Python"""

    filepath: str
    imports: List[CodeElement]
    classes: List[CodeElement]
    functions: List[CodeElement]
    variables: List[CodeElement]
    dependencies: Set[str]
    complexity: int
    lines_of_code: int


class ASTParser:
    """Parser de código Python usando AST (Abstract Syntax Tree)"""

    def __init__(self) -> None:
        self.logger = logger

    def parse_file(self, filepath: str) -> Optional[CodeStructure]:
        """
        Analisa arquivo Python e retorna estrutura completa.

        Args:
            filepath: Caminho para arquivo Python

        Returns:
            CodeStructure com análise completa ou None se falhar
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            return self.parse_source(source, filepath)
        except Exception as exc:
            self.logger.error(f"Failed to parse file {filepath}: {exc}")
            return None

    def parse_source(self, source: str, filepath: str = "<string>") -> CodeStructure:
        """
        Analisa código-fonte Python.

        Args:
            source: Código-fonte Python
            filepath: Nome do arquivo (para referência)

        Returns:
            CodeStructure com análise completa
        """
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise ValueError(f"Syntax error in {filepath}: {exc}")

        structure = CodeStructure(
            filepath=filepath,
            imports=[],
            classes=[],
            functions=[],
            variables=[],
            dependencies=set(),
            complexity=0,
            lines_of_code=len(source.splitlines()),
        )

        # Analisar nós da árvore
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    structure.imports.append(
                        CodeElement(
                            name=alias.name,
                            type="import",
                            line_start=node.lineno,
                            line_end=node.lineno,
                        )
                    )
                    structure.dependencies.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    structure.dependencies.add(node.module.split(".")[0])
                for alias in node.names:
                    structure.imports.append(
                        CodeElement(
                            name=(f"{node.module}.{alias.name}" if node.module else alias.name),
                            type="import",
                            line_start=node.lineno,
                            line_end=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                structure.classes.append(self._extract_class(node))

            elif isinstance(node, ast.FunctionDef):
                structure.functions.append(self._extract_function(node))

            elif isinstance(node, ast.Assign):
                # Variáveis de nível de módulo
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        structure.variables.append(
                            CodeElement(
                                name=target.id,
                                type="variable",
                                line_start=node.lineno,
                                line_end=node.lineno,
                            )
                        )

        # Calcular complexidade ciclomática
        structure.complexity = self._calculate_complexity(tree)

        return structure

    def _extract_class(self, node: ast.ClassDef) -> CodeElement:
        """Extrai informações de uma classe"""
        return CodeElement(
            name=node.name,
            type="class",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            bases=[self._get_base_name(b) for b in node.bases],
        )

    def _extract_function(self, node: ast.FunctionDef) -> CodeElement:
        """Extrai informações de uma função"""
        parameters = []
        for arg in node.args.args:
            param_str = arg.arg
            if arg.annotation:
                param_str += f": {ast.unparse(arg.annotation)}"
            parameters.append(param_str)

        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        return CodeElement(
            name=node.name,
            type="function",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            parameters=parameters,
            return_type=return_type,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
        )

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Obtém nome de um decorador"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return ast.unparse(decorator)

    def _get_base_name(self, base: ast.expr) -> str:
        """Obtém nome de uma classe base"""
        if isinstance(base, ast.Name):
            return base.id
        return ast.unparse(base)

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calcula complexidade ciclomática aproximada"""
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def validate_syntax(self, source: str) -> tuple[bool, Optional[str]]:
        """
        Valida sintaxe de código Python.

        Args:
            source: Código-fonte Python

        Returns:
            Tupla (is_valid, error_message)
        """
        try:
            ast.parse(source)
            return True, None
        except SyntaxError as exc:
            return False, f"Syntax error at line {exc.lineno}: {exc.msg}"

    def extract_imports(self, source: str) -> List[str]:
        """
        Extrai todos os imports de código Python.

        Args:
            source: Código-fonte Python

        Returns:
            Lista de módulos importados
        """
        try:
            tree = ast.parse(source)
            imports: List[str] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            return imports
        except Exception as exc:
            self.logger.error(f"Failed to extract imports: {exc}")
            return []

    def find_function_calls(self, source: str) -> List[str]:
        """
        Encontra todas as chamadas de função no código.

        Args:
            source: Código-fonte Python

        Returns:
            Lista de nomes de funções chamadas
        """
        try:
            tree = ast.parse(source)
            calls: List[str] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls.append(node.func.attr)

            return calls
        except Exception as exc:
            self.logger.error(f"Failed to find function calls: {exc}")
            return []

    def generate_skeleton(
        self,
        class_name: str,
        methods: List[tuple[str, List[str], Optional[str]]],
        docstring: Optional[str] = None,
    ) -> str:
        """
        Gera esqueleto de classe Python.

        Args:
            class_name: Nome da classe
            methods: Lista de tuplas (nome_método, parâmetros, tipo_retorno)
            docstring: Docstring da classe

        Returns:
            Código-fonte da classe gerada
        """
        lines = [f"class {class_name}:"]

        if docstring:
            lines.append(f'    """{docstring}"""')
            lines.append("")

        for method_name, params, return_type in methods:
            params_str = ", ".join(params)
            return_annotation = f" -> {return_type}" if return_type else ""

            # Only add comma separator if there are params
            if params_str:
                signature = f"self, {params_str}"
            else:
                signature = "self"

            lines.append(f"    def {method_name}({signature}){return_annotation}:")
            lines.append(f'        """TODO: Implement {method_name}"""')
            lines.append("        pass")
            lines.append("")

        return "\n".join(lines)

    def analyze_security_issues(self, source: str) -> List[str]:
        """
        Analisa potenciais problemas de segurança no código.

        Args:
            source: Código-fonte Python

        Returns:
            Lista de avisos de segurança
        """
        warnings: List[str] = []

        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):
                # Detectar uso de eval/exec
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec"]:
                            warnings.append(
                                f"Line {node.lineno}: Dangerous use of {node.func.id}()"
                            )

                # Detectar imports perigosos
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    dangerous_modules = ["pickle", "subprocess", "os"]
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in dangerous_modules:
                                warnings.append(
                                    f"Line {node.lineno}: "
                                    f"Potentially dangerous import: {alias.name}"
                                )

        except Exception as exc:
            self.logger.error(f"Failed to analyze security: {exc}")

        return warnings


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["ASTParser", "CodeElement", "CodeStructure"]
