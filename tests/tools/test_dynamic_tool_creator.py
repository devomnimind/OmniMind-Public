"""
Testes para DynamicToolCreator.

Autor: Fabrício da Silva + assistência de IA
"""

from src.tools.dynamic_tool_creator import DynamicToolCreator
from src.tools.omnimind_tools import ToolsFramework
from src.tools.tool_base import ToolCategory


class TestDynamicToolCreator:
    """Testes para DynamicToolCreator."""

    def test_init(self):
        """Testa inicialização."""
        creator = DynamicToolCreator()
        assert creator.created_tools == {}
        assert creator.tool_specs == {}

    def test_validate_code_valid(self):
        """Testa validação de código válido."""
        creator = DynamicToolCreator()
        code = """
from src.tools.tool_base import AuditedTool, ToolCategory

class TestTool(AuditedTool):
    def __init__(self):
        super().__init__("test_tool", ToolCategory.ACTION)

    def execute(self, arg1: str) -> str:
        return f"Result: {arg1}"
"""
        result = creator._validate_code(code, "test_tool")
        assert result["valid"] is True
        assert result["error"] is None

    def test_validate_code_invalid_syntax(self):
        """Testa validação de código com erro de sintaxe."""
        creator = DynamicToolCreator()
        code = "def invalid syntax"
        result = creator._validate_code(code, "test")
        assert result["valid"] is False
        assert "sintaxe" in result["error"].lower() or "syntax" in result["error"].lower()

    def test_validate_code_no_audited_tool(self):
        """Testa validação de código sem AuditedTool."""
        creator = DynamicToolCreator()
        code = """
class TestTool:
    def execute(self):
        pass
"""
        result = creator._validate_code(code, "test")
        assert result["valid"] is False
        assert "AuditedTool" in result["error"]

    def test_create_simple_tool(self):
        """Testa criação de ferramenta simples."""
        creator = DynamicToolCreator()

        def execute_func(arg1: str) -> str:
            return f"Result: {arg1}"

        tool = creator.create_simple_tool(
            name="simple_test",
            description="Test tool",
            execute_func=execute_func,
            category=ToolCategory.ACTION,
        )

        assert tool is not None
        assert tool.name == "simple_test"
        assert tool.category == ToolCategory.ACTION

        # Testar execução
        result = tool.execute("test")
        assert "Result: test" in result

    def test_create_tool_from_code(self):
        """Testa criação de ferramenta a partir de código."""
        creator = DynamicToolCreator()
        code = """
from src.tools.tool_base import AuditedTool, ToolCategory

class DynamicTestTool(AuditedTool):
    def __init__(self):
        super().__init__("dynamic_test", ToolCategory.ACTION)

    def execute(self, value: str) -> str:
        return f"Dynamic result: {value}"
"""

        tool = creator.create_tool(
            name="dynamic_test",
            description="Dynamic test tool",
            code=code,
            category=ToolCategory.ACTION,
        )

        assert tool is not None
        assert tool.name == "dynamic_test"
        assert "dynamic_test" in creator.created_tools

        # Testar execução
        result = tool.execute("test_value")
        assert "Dynamic result: test_value" in result

    def test_create_tool_wrapper(self):
        """Testa criação de wrapper para ferramenta falhando."""
        creator = DynamicToolCreator()
        alternative_code = """
        # Implementação alternativa
        return {"status": "success", "message": "Alternative implementation"}
"""

        tool = creator.create_tool_wrapper(
            failed_tool_name="failed_tool",
            alternative_implementation=alternative_code,
        )

        assert tool is not None
        assert "wrapper" in tool.name.lower()

    def test_register_tool_in_framework(self):
        """Testa registro de ferramenta no ToolsFramework."""
        creator = DynamicToolCreator()
        tools_framework = ToolsFramework()

        # Criar ferramenta simples
        def execute_func() -> str:
            return "test"

        tool = creator.create_simple_tool(
            name="framework_test",
            description="Test",
            execute_func=execute_func,
        )

        assert tool is not None

        # Registrar
        success = creator.register_tool_in_framework("framework_test", tools_framework)
        assert success is True
        assert "framework_test" in tools_framework.tools

    def test_get_created_tools(self):
        """Testa obtenção de ferramentas criadas."""
        creator = DynamicToolCreator()

        def execute_func() -> str:
            return "test"

        creator.create_simple_tool("tool1", "Test 1", execute_func)
        creator.create_simple_tool("tool2", "Test 2", execute_func)

        created = creator.get_created_tools()
        assert len(created) == 2
        assert "tool1" in created
        assert "tool2" in created
