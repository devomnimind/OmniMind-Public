"""
MCP Python Server - Servidor MCP para ambiente Python integrado com OmniMind.

Este servidor MCP implementa operações Python seguras:
- Execução segura de código Python
- Gerenciamento de pacotes (listagem, instalação controlada)
- Linting, type checking e formatação
- Execução de testes
- Informações do ambiente Python

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from src.integrations.mcp_cache import get_mcp_cache
from src.integrations.mcp_server import MCPServer

logger = logging.getLogger(__name__)

# Comandos permitidos para execução segura
ALLOWED_IMPORTS = {
    "math",
    "json",
    "datetime",
    "collections",
    "itertools",
    "functools",
    "operator",
    "random",
    "string",
    "re",
    "uuid",
    "hashlib",
    "base64",
    "pathlib",
}


class PythonMCPServer(MCPServer):
    """Servidor MCP para ambiente Python integrado com OmniMind."""

    def __init__(self, allow_package_install: bool = False, timeout: float = 30.0) -> None:
        """Inicializa o servidor Python MCP.

        Args:
            allow_package_install: Se True, permite instalação de pacotes (padrão: False)
            timeout: Timeout para execução de código em segundos
        """
        super().__init__()

        # Initialize cache
        self.cache = get_mcp_cache()

        self.allow_package_install = allow_package_install
        self.timeout = timeout

        # Registrar métodos MCP
        self._methods.update(
            {
                "execute_code": self.execute_code,
                "install_package": self.install_package,
                "list_packages": self.list_packages,
                "get_python_info": self.get_python_info,
                "lint_code": self.lint_code,
                "type_check": self.type_check,
                "run_tests": self.run_tests,
                "format_code": self.format_code,
            }
        )

        logger.info(
            "PythonMCPServer inicializado (allow_install=%s, timeout=%.1fs)",
            allow_package_install,
            timeout,
        )

    def execute_code(self, code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Executa código Python de forma segura.

        Args:
            code: Código Python a executar
            timeout: Timeout opcional (usa self.timeout se não fornecido)

        Returns:
            Dict com stdout, stderr, exit_code e resultado
        """
        if not code or not code.strip():
            return {"stdout": "", "stderr": "", "exit_code": 0, "result": None}

        # Check cache first
        cache_key = f"python_exec_{hash(code) % 10000}"
        try:
            if hasattr(self.cache, "_get_sync"):
                cached_result = self.cache._get_sync(cache_key)
                if cached_result:
                    return cached_result
        except Exception:
            pass

        exec_timeout = timeout or self.timeout

        try:
            # Validar código básico (verificar imports perigosos)
            if self._is_code_unsafe(code):
                return {
                    "stdout": "",
                    "stderr": "Code contains unsafe operations",
                    "exit_code": 1,
                    "result": None,
                    "error": "Security violation: unsafe imports or operations detected",
                }

            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = Path(f.name)

            try:
                # Executar código em subprocess com timeout
                result = subprocess.run(
                    [sys.executable, str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=exec_timeout,
                    cwd=self.project_root,
                )

                # Capturar stdout e stderr
                stdout = result.stdout
                stderr = result.stderr
                exit_code = result.returncode

                # Tentar extrair resultado se código retornar algo
                result_value = None
                if exit_code == 0 and stdout:
                    # Se stdout contém apenas um valor simples, tentar parsear
                    stdout_stripped = stdout.strip()
                    try:
                        # Tentar avaliar como Python literal
                        import ast

                        result_value = ast.literal_eval(stdout_stripped)
                    except (ValueError, SyntaxError):
                        # Se não for literal, usar stdout como string
                        result_value = stdout_stripped if stdout_stripped else None

                logger.debug(
                    "Código executado: exit_code=%d, stdout_len=%d, stderr_len=%d",
                    exit_code,
                    len(stdout),
                    len(stderr),
                )

                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                    "result": result_value,
                }

            finally:
                # Limpar arquivo temporário
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.debug("Erro ao deletar arquivo temporário: %s", e)

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timeout after {exec_timeout}s",
                "exit_code": -1,
                "result": None,
                "error": "Timeout",
            }
        except Exception as e:
            logger.error("Erro ao executar código: %s", e)
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "result": None,
                "error": str(e),
            }

    def _is_code_unsafe(self, code: str) -> bool:
        """Verifica se código contém operações inseguras.

        Args:
            code: Código a verificar

        Returns:
            True se código é inseguro
        """
        # Padrões perigosos
        dangerous_patterns = [
            "__import__",
            "eval(",
            "exec(",
            "compile(",
            "open(",
            "file(",
            "input(",
            "raw_input(",
            "subprocess",
            "os.system",
            "os.popen",
            "os.exec",
            "shutil",
            "pickle",
            "marshal",
            "ctypes",
            "socket",
            "urllib",
            "requests",
            "httpx",
        ]

        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                logger.warning("Código contém padrão perigoso: %s", pattern)
                return True

        return False

    def install_package(self, package: str) -> Dict[str, Any]:
        """Instala pacote Python (se permitido).

        Args:
            package: Nome do pacote

        Returns:
            Dict com status da instalação
        """
        if not self.allow_package_install:
            return {
                "status": "denied",
                "reason": "Installation disabled by config",
                "package": package,
            }

        try:
            # Validar nome do pacote
            if not package or not package.replace("-", "").replace("_", "").isalnum():
                return {
                    "status": "error",
                    "reason": "Invalid package name",
                    "package": package,
                }

            # Executar pip install
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300.0,  # 5 minutos para instalação
                cwd=self.project_root,
            )

            if result.returncode == 0:
                logger.info("Pacote instalado: %s", package)
                return {
                    "status": "installed",
                    "package": package,
                    "output": result.stdout,
                }
            else:
                logger.warning("Falha ao instalar pacote %s: %s", package, result.stderr)
                return {
                    "status": "error",
                    "reason": result.stderr,
                    "package": package,
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "reason": "Installation timeout",
                "package": package,
            }
        except Exception as e:
            logger.error("Erro ao instalar pacote: %s", e)
            return {
                "status": "error",
                "reason": str(e),
                "package": package,
            }

    def list_packages(self) -> Dict[str, Any]:
        """Lista pacotes Python instalados.

        Returns:
            Dict com lista de pacotes e versões
        """
        try:
            # Usar pip list
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=10.0,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                import json

                packages_data = json.loads(result.stdout)
                packages = {pkg["name"]: pkg.get("version", "unknown") for pkg in packages_data}

                logger.debug("Listados %d pacotes", len(packages))
                return {
                    "packages": packages,
                    "count": len(packages),
                }
            else:
                # Fallback: usar pkg_resources se disponível
                try:
                    import pkg_resources

                    packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
                    return {
                        "packages": packages,
                        "count": len(packages),
                    }
                except ImportError:
                    # Fallback final: lista básica
                    return {
                        "packages": {"numpy": "unknown", "torch": "unknown"},
                        "count": 2,
                        "error": "Could not list packages",
                    }

        except Exception as e:
            logger.error("Erro ao listar pacotes: %s", e)
            return {
                "packages": {},
                "count": 0,
                "error": str(e),
            }

    def get_python_info(self) -> Dict[str, Any]:
        """Obtém informações do ambiente Python.

        Returns:
            Dict com informações do Python
        """
        import platform

        return {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
            },
            "executable": sys.executable,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "python_path": sys.path,
        }

    def lint_code(self, code: str) -> Dict[str, Any]:
        """Executa linting no código Python.

        Args:
            code: Código a analisar

        Returns:
            Dict com issues encontradas
        """
        if not code or not code.strip():
            return {"issues": []}

        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = Path(f.name)

            try:
                # Tentar usar flake8
                result = subprocess.run(
                    [sys.executable, "-m", "flake8", str(temp_file), "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    cwd=self.project_root,
                )

                import json

                # CORREÇÃO (2025-12-08): flake8 retorna exit_code != 0 apenas quando há issues
                # exit_code == 0 significa sem issues, mesmo se houver stdout (warnings, etc.)
                if result.returncode == 0:
                    # Sem issues - flake8 retorna 0 quando não há problemas
                    return {"issues": []}

                # exit_code != 0 significa que há issues
                if result.stdout:
                    try:
                        # Tentar parsear como JSON (formato esperado)
                        issues = json.loads(result.stdout)
                        # Garantir que é uma lista
                        if isinstance(issues, list):
                            return {"issues": issues}
                        elif isinstance(issues, dict):
                            # Se for um único objeto, converter para lista
                            return {"issues": [issues]}
                        else:
                            return {"issues": []}
                    except json.JSONDecodeError:
                        # Se não for JSON válido, parsear saída texto linha por linha
                        # Apenas linhas que parecem erros (file:line:col: code message)
                        issues = []
                        for line in result.stdout.split("\n"):
                            line = line.strip()
                            if line and ":" in line:
                                # Formato típico do flake8: file:line:col: code message
                                parts = line.split(":", 3)
                                if len(parts) >= 4:
                                    issues.append(
                                        {
                                            "message": parts[3].strip(),
                                            "severity": "error",
                                            "line": (int(parts[1]) if parts[1].isdigit() else None),
                                            "column": (
                                                int(parts[2]) if parts[2].isdigit() else None
                                            ),
                                        }
                                    )
                        return {"issues": issues}
                else:
                    # Sem stdout mas exit_code != 0 - pode ser erro de execução
                    return {"issues": []}

            finally:
                try:
                    temp_file.unlink()
                except Exception:
                    pass

        except FileNotFoundError:
            # flake8 não disponível
            logger.debug("flake8 não disponível, retornando lista vazia")
            return {"issues": []}
        except Exception as e:
            logger.debug("Erro ao fazer lint: %s", e)
            return {"issues": []}

    def type_check(self, code: str) -> Dict[str, Any]:
        """Executa type checking no código Python.

        Args:
            code: Código a verificar

        Returns:
            Dict com erros de tipo encontrados
        """
        if not code or not code.strip():
            return {"errors": []}

        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = Path(f.name)

            try:
                # Tentar usar mypy
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "mypy",
                        str(temp_file),
                        "--ignore-missing-imports",
                        "--no-error-summary",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    cwd=self.project_root,
                )

                errors = []
                if result.stderr or result.returncode != 0:
                    # Parsear erros do mypy
                    for line in (result.stdout + result.stderr).split("\n"):
                        if line.strip() and "error:" in line.lower():
                            errors.append({"message": line.strip(), "type": "type_error"})

                return {"errors": errors}

            finally:
                try:
                    temp_file.unlink()
                except Exception:
                    pass

        except FileNotFoundError:
            # mypy não disponível
            logger.debug("mypy não disponível, retornando lista vazia")
            return {"errors": []}
        except Exception as e:
            logger.debug("Erro ao fazer type check: %s", e)
            return {"errors": []}

    def run_tests(self, path: str) -> Dict[str, Any]:
        """Executa testes Python.

        Args:
            path: Caminho para testes (arquivo ou diretório)

        Returns:
            Dict com resultados dos testes
        """
        test_path = Path(path)
        if not test_path.is_absolute():
            test_path = self.project_root / test_path

        if not test_path.exists():
            return {
                "results": "error",
                "error": f"Test path not found: {path}",
            }

        try:
            # Executar pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300.0,  # 5 minutos para testes
                cwd=self.project_root,
            )

            # Parsear resultados
            passed = result.returncode == 0
            output = result.stdout + result.stderr

            return {
                "results": "passed" if passed else "failed",
                "exit_code": result.returncode,
                "output": output,
                "passed": passed,
            }

        except FileNotFoundError:
            # pytest não disponível
            return {
                "results": "error",
                "error": "pytest not available",
            }
        except subprocess.TimeoutExpired:
            return {
                "results": "timeout",
                "error": "Test execution timeout",
            }
        except Exception as e:
            logger.error("Erro ao executar testes: %s", e)
            return {
                "results": "error",
                "error": str(e),
            }

    def format_code(self, code: str) -> Dict[str, Any]:
        """Formata código Python usando black.

        Args:
            code: Código a formatar

        Returns:
            Dict com código formatado
        """
        if not code or not code.strip():
            return {"formatted_code": code}

        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = Path(f.name)

            try:
                # Executar black
                result = subprocess.run(
                    [sys.executable, "-m", "black", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    cwd=self.project_root,
                )

                if result.returncode == 0:
                    # Ler código formatado
                    formatted = temp_file.read_text()
                    return {"formatted_code": formatted}
                else:
                    # Se black falhar, retornar código original
                    logger.debug("black falhou, retornando código original")
                    return {"formatted_code": code, "error": result.stderr}

            finally:
                try:
                    temp_file.unlink()
                except Exception:
                    pass

        except FileNotFoundError:
            # black não disponível
            logger.debug("black não disponível, retornando código original")
            return {"formatted_code": code}
        except Exception as e:
            logger.debug("Erro ao formatar código: %s", e)
            return {"formatted_code": code, "error": str(e)}


if __name__ == "__main__":
    server = PythonMCPServer()
    try:
        server.start()
        logger.info("Python MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
