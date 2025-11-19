"""
Tests for code_generator module.
"""

from pathlib import Path

import pytest

from src.tools.code_generator import (
    CodeGenerator,
    CodeTemplateType,
    generate_agent,
    generate_test_for_class,
)


class TestCodeGenerator:
    """Tests for CodeGenerator."""

    @pytest.fixture
    def generator(self) -> CodeGenerator:
        """Create CodeGenerator instance."""
        return CodeGenerator()

    def test_initialization(self, generator: CodeGenerator) -> None:
        """Test CodeGenerator initialization."""
        assert len(generator.templates) > 0
        assert "agent" in generator.templates
        assert "tool" in generator.templates
        assert "test" in generator.templates

    def test_generate_agent(self, generator: CodeGenerator, tmp_path: Path) -> None:
        """Test agent code generation."""
        output_file = tmp_path / "test_agent.py"

        code = generator.generate_agent(
            agent_name="TestAgent",
            description="Test agent for testing",
            purpose="Testing purposes",
            capabilities=["- Test execution", "- Validation"],
            output_file=output_file,
        )

        assert "class TestAgent:" in code
        assert "Test agent for testing" in code
        assert output_file.exists()

    def test_generate_test(self, generator: CodeGenerator, tmp_path: Path) -> None:
        """Test test code generation."""
        output_file = tmp_path / "test_generated.py"

        code = generator.generate_test(
            module_name="test_module",
            module_path="src.test_module",
            class_name="TestClass",
            methods=["execute", "validate"],
            output_file=output_file,
        )

        assert "class TestTestClass:" in code
        assert "test_execute" in code
        assert "test_validate" in code
        assert output_file.exists()

    def test_generate_api_endpoint(
        self, generator: CodeGenerator, tmp_path: Path
    ) -> None:
        """Test API endpoint generation."""
        output_file = tmp_path / "test_endpoint.py"

        code = generator.generate_api_endpoint(
            endpoint_name="test_endpoint",
            description="Test endpoint",
            prefix="/api/v1",
            tag="Testing",
            path="/test",
            method="post",
            output_file=output_file,
        )

        assert "async def test_endpoint" in code
        assert "@router.post" in code
        assert output_file.exists()

    def test_template_required_params(self, generator: CodeGenerator) -> None:
        """Test that missing required params raises error."""
        with pytest.raises(ValueError, match="Missing required parameters"):
            generator.generate_code("agent", {})

    def test_invalid_template(self, generator: CodeGenerator) -> None:
        """Test that invalid template raises error."""
        with pytest.raises(ValueError, match="Template not found"):
            generator.generate_code("invalid_template", {})

    def test_generate_docstring(self, generator: CodeGenerator) -> None:
        """Test docstring generation."""

        def sample_function(param1: str, param2: int) -> bool:
            """Sample function."""
            return True

        docstring = generator.generate_docstring(sample_function, style="google")

        assert "Args:" in docstring
        assert "Returns:" in docstring


def test_generate_agent_function(tmp_path: Path) -> None:
    """Test generate_agent convenience function."""
    output_file = tmp_path / "agent.py"

    code = generate_agent(
        agent_name="QuickAgent",
        description="Quick agent",
        purpose="Testing",
        output_file=output_file,
    )

    assert "class QuickAgent:" in code
    assert output_file.exists()


def test_generate_test_for_class_function(tmp_path: Path) -> None:
    """Test generate_test_for_class convenience function."""
    output_file = tmp_path / "test_class.py"

    code = generate_test_for_class(
        class_name="SampleClass",
        module_path="src.sample",
        output_file=output_file,
    )

    assert "class TestSampleClass:" in code
    assert output_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
