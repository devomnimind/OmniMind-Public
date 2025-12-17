"""
Testes para ToolComposer.

Autor: Fabrício da Silva + assistência de IA
"""

from src.tools.omnimind_tools import ToolsFramework
from src.tools.tool_composer import CompositionType, ToolComposer


class TestToolComposer:
    """Testes para ToolComposer."""

    def test_init(self):
        """Testa inicialização."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)
        assert composer.tools_framework == tools_framework
        assert composer.compositions == {}

    def test_compose_tools_sequential(self):
        """Testa composição sequencial."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        composition = composer.compose_tools(
            tool_names=["read_file", "write_to_file"],
            composition_type=CompositionType.SEQUENTIAL,
        )

        assert composition.composition_id is not None
        assert len(composition.tool_names) == 2
        assert composition.composition_type == CompositionType.SEQUENTIAL
        assert len(composition.execution_order) == 2

    def test_optimize_composition(self):
        """Testa otimização de ordem de execução."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        # Criar dependências: write depende de read
        dependencies = {"write_to_file": ["read_file"]}

        execution_order = composer.optimize_composition(
            tool_names=["read_file", "write_to_file"], dependencies=dependencies
        )

        # read_file deve vir antes de write_to_file
        assert execution_order.index("read_file") < execution_order.index("write_to_file")

    def test_detect_dependencies(self):
        """Testa detecção automática de dependências."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        dependencies = composer._detect_dependencies(["read_file", "write_to_file"])

        # write_to_file pode depender de read_file
        assert "write_to_file" in dependencies
        # Pode ter dependência ou não (heurística)

    def test_validate_composition_valid(self):
        """Testa validação de composição válida."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        composition = composer.compose_tools(tool_names=["read_file", "write_to_file"])

        is_valid, errors = composer.validate_composition(composition)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_composition_invalid_tool(self):
        """Testa validação de composição com ferramenta inválida."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        # Criar composição manualmente com ferramenta inválida
        from src.tools.tool_composer import ToolComposition

        composition = ToolComposition(
            composition_id="test",
            tool_names=["invalid_tool"],
            composition_type=CompositionType.SEQUENTIAL,
            dependencies={},
            execution_order=["invalid_tool"],
        )

        is_valid, errors = composer.validate_composition(composition)

        assert is_valid is False
        assert len(errors) > 0
        assert any("invalid_tool" in error for error in errors)

    def test_has_cycle(self):
        """Testa detecção de ciclo."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        # Grafo com ciclo: A -> B -> C -> A
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        nodes = ["A", "B", "C"]

        has_cycle = composer._has_cycle(graph, nodes)

        assert has_cycle is True

    def test_execute_composition(self):
        """Testa execução de composição."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        composer.compose_tools(
            tool_names=["read_file", "list_files"], composition_id="test_composition"
        )

        # Mock inputs
        inputs = {
            "read_file": {"filepath": "test.txt"},
            "list_files": {"directory": "."},
        }

        result = composer.execute_composition("test_composition", inputs=inputs)

        assert result.composition_id == "test_composition"
        assert len(result.results) == 2
        assert "read_file" in result.results
        assert "list_files" in result.results

    def test_list_compositions(self):
        """Testa listagem de composições."""
        tools_framework = ToolsFramework()
        composer = ToolComposer(tools_framework)

        composer.compose_tools(["read_file"], composition_id="comp1")
        composer.compose_tools(["write_to_file"], composition_id="comp2")

        compositions = composer.list_compositions()

        assert len(compositions) == 2
        assert "comp1" in compositions
        assert "comp2" in compositions
