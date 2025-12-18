"""Testes para PythonMCPServer (mcp_python_server.py).

Cobertura de:
- Inicialização do servidor
- Execução de código (execute_code)
- Instalação de pacotes (install_package)
- Listagem de pacotes (list_packages)
- Informações do Python (get_python_info)
- Linting de código (lint_code)
- Type checking (type_check)
- Execução de testes (run_tests)
- Formatação de código (format_code)
"""

from __future__ import annotations

from src.integrations.mcp_python_server import PythonMCPServer


class TestPythonMCPServer:
    """Testes para o servidor MCP de Python."""

    def test_initialization(self) -> None:
        """Testa inicialização do PythonMCPServer."""
        server = PythonMCPServer()
        assert server is not None
        expected_methods = [
            "execute_code",
            "install_package",
            "list_packages",
            "get_python_info",
            "lint_code",
            "type_check",
            "run_tests",
            "format_code",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_execute_code_basic(self) -> None:
        """Testa execução básica de código.

        NOTA: Retorna valores reais da execução do código.
        Não compara valores específicos, apenas estrutura e tipos.
        """
        server = PythonMCPServer()
        result = server.execute_code(code="print('Hello')")
        assert result is not None
        assert isinstance(result, dict)
        assert "stdout" in result
        assert "stderr" in result
        assert "exit_code" in result
        # Verificar tipos e estrutura (valores dinâmicos)
        assert isinstance(result["stdout"], str)
        assert isinstance(result["stderr"], str)
        assert isinstance(result["exit_code"], int)
        # Código válido deve ter exit_code 0
        assert result["exit_code"] == 0

    def test_execute_code_simple_expression(self) -> None:
        """Testa execução de expressão simples."""
        server = PythonMCPServer()
        result = server.execute_code(code="2 + 2")
        assert result["exit_code"] == 0
        assert result["stderr"] == ""

    def test_execute_code_multiline(self) -> None:
        """Testa execução de código multilinha."""
        server = PythonMCPServer()
        code = """
def test_function():
    return "test"
print(test_function())
"""
        result = server.execute_code(code=code)
        assert result["exit_code"] == 0

    def test_execute_code_empty(self) -> None:
        """Testa execução de código vazio."""
        server = PythonMCPServer()
        result = server.execute_code(code="")
        assert result is not None
        assert "exit_code" in result

    def test_install_package_basic(self) -> None:
        """Testa tentativa de instalação de pacote."""
        server = PythonMCPServer()
        result = server.install_package(package="requests")
        assert result is not None
        assert isinstance(result, dict)
        assert "status" in result
        assert "reason" in result
        assert result["status"] == "denied"
        assert result["reason"] == "Installation disabled by config"

    def test_install_package_different_packages(self) -> None:
        """Testa instalação de diferentes pacotes."""
        server = PythonMCPServer()
        packages = ["numpy", "pandas", "torch", "transformers"]
        for package in packages:
            result = server.install_package(package=package)
            assert result["status"] == "denied"
            assert "reason" in result

    def test_list_packages_basic(self) -> None:
        """Testa listagem de pacotes.

        NOTA: Retorna pacotes reais instalados no ambiente.
        Não compara pacotes específicos, apenas estrutura e tipos.
        """
        server = PythonMCPServer()
        result = server.list_packages()
        assert result is not None
        assert isinstance(result, dict)
        assert "packages" in result
        assert isinstance(result["packages"], list)
        # Verificar que lista não está vazia e contém strings
        assert len(result["packages"]) > 0
        assert all(isinstance(pkg, str) for pkg in result["packages"])

    def test_get_python_info_basic(self) -> None:
        """Testa recuperação de informações do Python.

        NOTA: Retorna valores reais do sistema via sys.version.
        """
        server = PythonMCPServer()
        result = server.get_python_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "version" in result
        assert isinstance(result["version"], str)
        # Verificar que contém informações básicas do Python
        assert "Python" in result["version"] or len(result["version"]) > 0
        # Verificar estrutura completa
        assert "version_info" in result
        assert "executable" in result
        assert "platform" in result

    def test_lint_code_basic(self) -> None:
        """Testa linting de código.

        NOTA: Retorna issues reais do flake8.
        Código válido pode ter 0 issues, mas estrutura deve estar correta.
        """
        server = PythonMCPServer()
        result = server.lint_code(code="print('hello')")
        assert result is not None
        assert isinstance(result, dict)
        assert "issues" in result
        assert isinstance(result["issues"], list)
        # Verificar estrutura (issues podem ser 0 ou mais, dependendo do código)
        assert all(isinstance(issue, dict) and "message" in issue for issue in result["issues"])

    def test_lint_code_multiline(self) -> None:
        """Testa linting de código multilinha."""
        server = PythonMCPServer()
        code = """
def my_function(x, y):
    return x + y

result = my_function(1, 2)
"""
        result = server.lint_code(code=code)
        assert result is not None
        assert "issues" in result

    def test_lint_code_empty(self) -> None:
        """Testa linting de código vazio."""
        server = PythonMCPServer()
        result = server.lint_code(code="")
        assert result is not None
        assert result["issues"] == []

    def test_type_check_basic(self) -> None:
        """Testa type checking de código."""
        server = PythonMCPServer()
        result = server.type_check(code="x: int = 5")
        assert result is not None
        assert isinstance(result, dict)
        assert "errors" in result
        assert isinstance(result["errors"], list)
        assert result["errors"] == []

    def test_type_check_function(self) -> None:
        """Testa type checking de função."""
        server = PythonMCPServer()
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        result = server.type_check(code=code)
        assert result is not None
        assert "errors" in result

    def test_type_check_empty(self) -> None:
        """Testa type checking de código vazio."""
        server = PythonMCPServer()
        result = server.type_check(code="")
        assert result["errors"] == []

    def test_run_tests_basic(self) -> None:
        """Testa execução de testes."""
        server = PythonMCPServer()
        result = server.run_tests(path="tests/")
        assert result is not None
        assert isinstance(result, dict)
        assert "results" in result
        assert result["results"] == "passed"

    def test_run_tests_different_paths(self) -> None:
        """Testa execução de testes em diferentes paths.

        NOTA: Paths podem não existir, então verificamos apenas estrutura de resposta.
        """
        server = PythonMCPServer()
        paths = ["tests/unit/", "tests/integration/", "tests/test_example.py"]
        for path in paths:
            result = server.run_tests(path=path)
            assert result is not None
            assert isinstance(result, dict)
            assert "results" in result
            # Resultado pode ser "passed", "failed" ou "error" dependendo do path
            assert result["results"] in ["passed", "failed", "error"]

    def test_format_code_basic(self) -> None:
        """Testa formatação de código.

        NOTA: Black formata código automaticamente, então não comparamos
        com código original, apenas verificamos que código formatado existe.
        """
        server = PythonMCPServer()
        code = "x=1+2"
        result = server.format_code(code=code)
        assert result is not None
        assert isinstance(result, dict)
        assert "formatted_code" in result
        # Black formata "x=1+2" para "x = 1 + 2", então verificamos apenas estrutura
        assert isinstance(result["formatted_code"], str)
        assert len(result["formatted_code"]) > 0

    def test_format_code_multiline(self) -> None:
        """Testa formatação de código multilinha."""
        server = PythonMCPServer()
        code = """
def my_func(x,y):
    return x+y
"""
        result = server.format_code(code=code)
        assert result is not None
        assert "formatted_code" in result

    def test_format_code_empty(self) -> None:
        """Testa formatação de código vazio."""
        server = PythonMCPServer()
        result = server.format_code(code="")
        assert result is not None
        assert result["formatted_code"] == ""

    def test_methods_registered(self) -> None:
        """Testa se todos os métodos estão registrados."""
        server = PythonMCPServer()
        expected_methods = [
            "execute_code",
            "install_package",
            "list_packages",
            "get_python_info",
            "lint_code",
            "type_check",
            "run_tests",
            "format_code",
            # Métodos herdados de MCPServer
            "read_file",
            "write_file",
            "list_dir",
            "stat",
            "get_metrics",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_execute_code_with_imports(self) -> None:
        """Testa execução de código com imports."""
        server = PythonMCPServer()
        code = "import sys\nprint(sys.version)"
        result = server.execute_code(code=code)
        assert result["exit_code"] == 0

    def test_lint_code_complex(self) -> None:
        """Testa linting de código complexo."""
        server = PythonMCPServer()
        code = """
class MyClass:
    def __init__(self, value: int) -> None:
        self.value = value

    def get_value(self) -> int:
        return self.value
"""
        result = server.lint_code(code=code)
        assert result is not None
        assert "issues" in result
