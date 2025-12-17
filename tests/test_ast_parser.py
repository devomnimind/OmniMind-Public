#!/usr/bin/env python3
"""
Tests for AST Parser Tool

Testa funcionalidades de parsing e análise de código Python.
"""

import pytest

from src.tools.ast_parser import ASTParser


class TestASTParser:
    """Testes para ASTParser"""

    @pytest.fixture
    def parser(self) -> ASTParser:
        """Fixture para criar parser"""
        return ASTParser()

    def test_validate_syntax_valid_code(self, parser: ASTParser) -> None:
        """Testa validação de código válido"""
        code = """
def hello_world():
    print("Hello, World!")
"""
        is_valid, error = parser.validate_syntax(code)
        assert is_valid is True
        assert error is None

    def test_validate_syntax_invalid_code(self, parser: ASTParser) -> None:
        """Testa validação de código inválido"""
        code = """
def hello_world(
    print("Missing closing paren")
"""
        is_valid, error = parser.validate_syntax(code)
        assert is_valid is False
        assert error is not None
        assert "Syntax error" in error

    def test_parse_source_simple(self, parser: ASTParser) -> None:
        """Testa parsing de código simples"""
        code = """
import os
from typing import Any

def calculate(x: int, y: int) -> int:
    '''Calculate sum'''
    return x + y

class MyClass:
    '''My class'''
    def method(self) -> None:
        pass
"""
        structure = parser.parse_source(code, "test.py")

        assert structure.filepath == "test.py"
        assert len(structure.imports) >= 2
        assert len(structure.functions) >= 1
        assert len(structure.classes) >= 1

        # Verificar função
        calc_func = next(f for f in structure.functions if f.name == "calculate")
        assert calc_func.type == "function"
        assert "x: int" in calc_func.parameters
        assert calc_func.return_type == "int"
        assert calc_func.docstring == "Calculate sum"

        # Verificar classe
        my_class = next(c for c in structure.classes if c.name == "MyClass")
        assert my_class.type == "class"
        assert my_class.docstring == "My class"

    def test_extract_imports(self, parser: ASTParser) -> None:
        """Testa extração de imports"""
        code = """
import os
import sys
from pathlib import Path
from typing import Any, Dict
"""
        imports = parser.extract_imports(code)

        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "typing" in imports

    def test_find_function_calls(self, parser: ASTParser) -> None:
        """Testa localização de chamadas de função"""
        code = """
def main():
    print("Hello")
    calculate(1, 2)
    obj.method()
"""
        calls = parser.find_function_calls(code)

        assert "print" in calls
        assert "calculate" in calls
        assert "method" in calls

    def test_generate_skeleton(self, parser: ASTParser) -> None:
        """Testa geração de esqueleto de classe"""
        methods: list[tuple[str, list[str], str | None]] = [
            ("__init__", ["name: str", "age: int"], "None"),
            ("get_name", [], "str"),
            ("set_age", ["age: int"], "None"),
        ]

        skeleton = parser.generate_skeleton("Person", methods, "Person class")

        assert "class Person:" in skeleton
        assert "Person class" in skeleton
        assert "def __init__(self, name: str, age: int) -> None:" in skeleton
        assert "def get_name(self) -> str:" in skeleton
        assert "def set_age(self, age: int) -> None:" in skeleton

    def test_analyze_security_issues_eval(self, parser: ASTParser) -> None:
        """Testa detecção de uso de eval"""
        code = """
def dangerous():
    result = eval(user_input)
    return result
"""
        warnings = parser.analyze_security_issues(code)

        assert len(warnings) > 0
        assert any("eval" in w for w in warnings)

    def test_analyze_security_issues_safe(self, parser: ASTParser) -> None:
        """Testa código seguro"""
        code = """
def safe_function():
    return "Hello, World!"
"""
        warnings = parser.analyze_security_issues(code)
        assert len(warnings) == 0

    def test_calculate_complexity(self, parser: ASTParser) -> None:
        """Testa cálculo de complexidade"""
        # Código simples
        simple_code = """
def simple():
    return 1
"""
        simple_structure = parser.parse_source(simple_code)
        assert simple_structure.complexity == 1

        # Código com branches
        complex_code = """
def complex(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    for i in range(x):
        if i % 2 == 0:
            print(i)
    return "done"
"""
        complex_structure = parser.parse_source(complex_code)
        assert complex_structure.complexity > 3

    def test_parse_file_nonexistent(self, parser: ASTParser) -> None:
        """Testa parsing de arquivo inexistente"""
        result = parser.parse_file("/nonexistent/file.py")
        assert result is None

    def test_dependencies_extraction(self, parser: ASTParser) -> None:
        """Testa extração de dependências"""
        code = """
import os
import sys
from pathlib import Path
from typing import Any
"""
        structure = parser.parse_source(code)

        assert "os" in structure.dependencies
        assert "sys" in structure.dependencies
        assert "pathlib" in structure.dependencies
        assert "typing" in structure.dependencies

    def test_decorators_extraction(self, parser: ASTParser) -> None:
        """Testa extração de decoradores"""
        code = """
@property
def value(self):
    return self._value

@staticmethod
def static_method():
    pass
"""
        structure = parser.parse_source(code)

        assert any("property" in f.decorators for f in structure.functions)
        assert any("staticmethod" in f.decorators for f in structure.functions)


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["TestASTParser"]
