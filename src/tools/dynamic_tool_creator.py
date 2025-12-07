"""
Dynamic Tool Creator - Criação Dinâmica de Ferramentas

Permite que agentes criem novas ferramentas sob demanda quando necessário,
não apenas usar ferramentas pré-definidas.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from ..observability.module_logger import get_module_logger
from ..observability.module_metrics import get_metrics_collector
from .tool_base import AuditedTool, ToolCategory

logger = logging.getLogger(__name__)
structured_logger = get_module_logger("DynamicToolCreator")
metrics = get_metrics_collector()


@dataclass
class ToolSpec:
    """Especificação de uma ferramenta a ser criada."""

    name: str
    description: str
    category: ToolCategory
    code: str  # Código Python da ferramenta
    parameters: Dict[str, Any]  # Parâmetros esperados
    return_type: str  # Tipo de retorno esperado


class DynamicToolCreator:
    """
    Cria ferramentas dinamicamente baseado em necessidade.

    Características:
    - Gera código Python para ferramentas
    - Valida código antes de criar
    - Integra com SandboxSystem para validação segura
    - Registra ferramentas no ToolsFramework
    """

    def __init__(self, sandbox_system: Optional[Any] = None):
        """
        Inicializa DynamicToolCreator.

        Args:
            sandbox_system: Instância opcional de SandboxSystem para validação
        """
        self.sandbox_system = sandbox_system
        self.created_tools: Dict[str, AuditedTool] = {}
        self.tool_specs: Dict[str, ToolSpec] = {}

        logger.info("DynamicToolCreator inicializado")
        structured_logger.info(
            "DynamicToolCreator inicializado", {"sandbox_enabled": sandbox_system is not None}
        )
        metrics.record_metric(
            "DynamicToolCreator", "initialized", 1, {"sandbox_enabled": sandbox_system is not None}
        )

    def create_tool(
        self,
        name: str,
        description: str,
        code: str,
        category: ToolCategory = ToolCategory.ACTION,
        validate: bool = True,
    ) -> Optional[AuditedTool]:
        """
        Cria ferramenta dinamicamente.

        Args:
            name: Nome único da ferramenta
            description: Descrição da ferramenta
            code: Código Python da classe da ferramenta
            category: Categoria da ferramenta
            validate: Se True, valida código antes de criar

        Returns:
            Instância de AuditedTool ou None se falhar
        """
        if name in self.created_tools:
            logger.warning(f"Ferramenta {name} já existe")
            return self.created_tools[name]

        # Validar código se solicitado
        if validate:
            validation_result = self._validate_code(code, name)
            if not validation_result["valid"]:
                logger.error(f"Código inválido para {name}: {validation_result['error']}")
                return None

        # Validar com SandboxSystem se disponível
        if self.sandbox_system:
            try:
                # Criar snapshot para validação
                snapshot = self.sandbox_system.create_snapshot("dynamic_tool_creation")
                # Validar mudança
                validation = self.sandbox_system.validate_change(
                    snapshot, {"type": "code", "content": code}
                )
                if not validation.is_valid:
                    logger.error(f"Validação sandbox falhou: {validation.reason}")
                    return None
            except Exception as e:
                logger.warning(f"Erro na validação sandbox: {e}")

        try:
            # Compilar e executar código
            compiled = compile(code, f"<dynamic_tool_{name}>", "exec")
            namespace: Dict[str, Any] = {}
            exec(compiled, namespace)

            # Encontrar classe da ferramenta
            tool_class = None
            for obj in namespace.values():
                if isinstance(obj, type) and issubclass(obj, AuditedTool) and obj != AuditedTool:
                    tool_class = obj
                    break

            if not tool_class:
                logger.error(f"Classe AuditedTool não encontrada no código de {name}")
                return None

            # Instanciar ferramenta
            # A classe criada dinamicamente deve ter __init__ que chama
            # super().__init__(name, category)
            # mypy não consegue inferir isso, então usamos type: ignore
            try:
                tool_instance = tool_class()  # type: ignore[call-arg]
            except TypeError:
                # Se falhar, tentar com argumentos padrão (fallback)
                tool_instance = tool_class(name=name, category=category)  # type: ignore[call-arg]

            # Verificar se nome está correto
            if tool_instance.name != name:
                logger.warning(
                    f"Nome da ferramenta não corresponde: "
                    f"esperado {name}, obtido {tool_instance.name}"
                )

            # Registrar
            self.created_tools[name] = tool_instance
            self.tool_specs[name] = ToolSpec(
                name=name,
                description=description,
                category=category,
                code=code,
                parameters={},  # Será preenchido se possível
                return_type="Any",
            )

            logger.info(f"Ferramenta dinâmica criada: {name} ({category.value})")
            structured_logger.info(
                f"Ferramenta dinâmica criada: {name}",
                {"name": name, "category": category.value, "total_tools": len(self.created_tools)},
            )
            metrics.record_metric(
                "DynamicToolCreator",
                "tools_created",
                len(self.created_tools),
                {"category": category.value},
            )
            return tool_instance

        except Exception as e:
            logger.error(f"Erro ao criar ferramenta {name}: {e}")
            return None

    def create_tool_wrapper(
        self,
        failed_tool_name: str,
        alternative_implementation: str,
        wrapper_name: Optional[str] = None,
    ) -> Optional[AuditedTool]:
        """
        Cria wrapper alternativo para ferramenta que falhou.

        Args:
            failed_tool_name: Nome da ferramenta que falhou
            alternative_implementation: Código Python da implementação alternativa
            wrapper_name: Nome do wrapper (default: {failed_tool_name}_wrapper)

        Returns:
            Instância de AuditedTool ou None se falhar
        """
        wrapper_name = wrapper_name or f"{failed_tool_name}_wrapper"

        # Template de wrapper
        wrapper_code = f'''
from src.tools.tool_base import AuditedTool, ToolCategory

class {wrapper_name.title().replace("_", "")}Tool(AuditedTool):
    """Wrapper alternativo para {failed_tool_name}"""

    def __init__(self):
        super().__init__("{wrapper_name}", ToolCategory.ACTION)

    def execute(self, *args, **kwargs):
        """Implementação alternativa"""
        {alternative_implementation}
'''

        return self.create_tool(
            name=wrapper_name,
            description=f"Wrapper alternativo para {failed_tool_name}",
            code=wrapper_code,
            category=ToolCategory.ACTION,
        )

    def _validate_code(self, code: str, tool_name: str) -> Dict[str, Any]:
        """
        Valida código Python antes de criar ferramenta.

        Args:
            code: Código Python
            tool_name: Nome da ferramenta

        Returns:
            Dict com 'valid' (bool) e 'error' (str opcional)
        """
        try:
            # Parse AST
            tree = ast.parse(code)

            # Verificar se há classe que herda de AuditedTool
            has_audited_tool = False
            has_execute = False

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Verificar herança
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "AuditedTool":
                            has_audited_tool = True
                            # Verificar se tem método execute
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef) and item.name == "execute":
                                    has_execute = True
                                    break

            if not has_audited_tool:
                return {
                    "valid": False,
                    "error": "Código deve conter classe que herda de AuditedTool",
                }

            if not has_execute:
                return {
                    "valid": False,
                    "error": "Classe deve ter método execute()",
                }

            # Verificar sintaxe básica
            compile(code, f"<validation_{tool_name}>", "exec")

            return {"valid": True, "error": None}

        except SyntaxError as e:
            return {"valid": False, "error": f"Erro de sintaxe: {e}"}
        except Exception as e:
            return {"valid": False, "error": f"Erro de validação: {e}"}

    def get_created_tools(self) -> Dict[str, AuditedTool]:
        """Retorna ferramentas criadas dinamicamente."""
        return self.created_tools.copy()

    def register_tool_in_framework(self, tool_name: str, tools_framework: Any) -> bool:
        """
        Registra ferramenta criada dinamicamente no ToolsFramework.

        Args:
            tool_name: Nome da ferramenta
            tools_framework: Instância de ToolsFramework

        Returns:
            True se registrado com sucesso
        """
        if tool_name not in self.created_tools:
            logger.error(f"Ferramenta {tool_name} não encontrada")
            return False

        tool = self.created_tools[tool_name]

        # Registrar no framework
        tools_framework.tools[tool_name] = tool

        logger.info(f"Ferramenta {tool_name} registrada no ToolsFramework")
        return True

    def create_simple_tool(
        self,
        name: str,
        description: str,
        execute_func: Callable,
        category: ToolCategory = ToolCategory.ACTION,
    ) -> Optional[AuditedTool]:
        """
        Cria ferramenta simples a partir de função.

        Args:
            name: Nome da ferramenta
            description: Descrição
            execute_func: Função que executa a ação
            category: Categoria

        Returns:
            Instância de AuditedTool ou None
        """
        # Criar classe dinamicamente
        class_name = name.title().replace("_", "") + "Tool"

        # Wrapper para execute_func que aceita self
        def execute_wrapper(self, *args, **kwargs):
            return execute_func(*args, **kwargs)

        class_dict = {
            "__init__": lambda self: AuditedTool.__init__(self, name, category),
            "execute": execute_wrapper,
        }

        try:
            tool_class = type(class_name, (AuditedTool,), class_dict)
            tool_instance = tool_class()

            self.created_tools[name] = tool_instance
            logger.info(f"Ferramenta simples criada: {name}")

            return tool_instance

        except Exception as e:
            logger.error(f"Erro ao criar ferramenta simples {name}: {e}")
            return None
