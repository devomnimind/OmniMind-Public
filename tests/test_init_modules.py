#!/usr/bin/env python3
"""
Testes unitários para módulos __init__.py
Grupo 4 - Phase 1: autopoietic e kernel_ai
"""

import pytest


class TestAutopoieticInit:
    """Testes para o módulo src/autopoietic/__init__.py"""

    def test_module_importable(self) -> None:
        """Testa que o módulo pode ser importado."""
        import src.autopoietic

        assert src.autopoietic is not None

    def test_version_defined(self) -> None:
        """Testa que __version__ está definido."""
        from src.autopoietic import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self) -> None:
        """Testa que __version__ segue formato semântico."""
        from src.autopoietic import __version__

        # Deve ser algo como "1.0.0"
        parts = __version__.split(".")
        assert len(parts) >= 2  # Pelo menos X.Y
        assert all(part.isdigit() for part in parts)

    def test_author_defined(self) -> None:
        """Testa que __author__ está definido."""
        from src.autopoietic import __author__

        assert __author__ is not None
        assert isinstance(__author__, str)
        assert len(__author__) > 0

    def test_all_defined(self) -> None:
        """Testa que __all__ está definido."""
        from src.autopoietic import __all__

        assert __all__ is not None
        assert isinstance(__all__, list)

    def test_all_contains_expected_exports(self) -> None:
        """Testa que __all__ contém as exportações esperadas."""
        from src.autopoietic import __all__

        expected_exports = [
            "AutopoieticSystem",
            "DesireEngine",
            "EvolutionaryArchitecture",
            "HybridInfrastructure",
        ]

        for export in expected_exports:
            assert export in __all__, f"{export} não encontrado em __all__"

    def test_all_list_not_empty(self) -> None:
        """Testa que __all__ não está vazio."""
        from src.autopoietic import __all__

        assert len(__all__) > 0

    def test_module_docstring(self) -> None:
        """Testa que o módulo tem docstring."""
        import src.autopoietic

        assert src.autopoietic.__doc__ is not None
        assert len(src.autopoietic.__doc__) > 0
        assert "Autopoietic" in src.autopoietic.__doc__

    def test_module_attributes(self) -> None:
        """Testa que o módulo tem os atributos esperados."""
        import src.autopoietic

        assert hasattr(src.autopoietic, "__version__")
        assert hasattr(src.autopoietic, "__author__")
        assert hasattr(src.autopoietic, "__all__")

    def test_version_is_string(self) -> None:
        """Testa que version é uma string."""
        from src.autopoietic import __version__

        assert isinstance(__version__, str)

    def test_author_is_string(self) -> None:
        """Testa que author é uma string."""
        from src.autopoietic import __author__

        assert isinstance(__author__, str)

    def test_all_is_list(self) -> None:
        """Testa que __all__ é uma lista."""
        from src.autopoietic import __all__

        assert isinstance(__all__, list)

    def test_all_items_are_strings(self) -> None:
        """Testa que todos os itens de __all__ são strings."""
        from src.autopoietic import __all__

        assert all(isinstance(item, str) for item in __all__)


class TestKernelAIInit:
    """Testes para o módulo src/kernel_ai/__init__.py"""

    def test_module_importable(self) -> None:
        """Testa que o módulo pode ser importado."""
        import src.kernel_ai

        assert src.kernel_ai is not None

    def test_version_defined(self) -> None:
        """Testa que __version__ está definido."""
        from src.kernel_ai import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self) -> None:
        """Testa que __version__ segue formato semântico."""
        from src.kernel_ai import __version__

        # Deve ser algo como "1.0.0"
        parts = __version__.split(".")
        assert len(parts) >= 2  # Pelo menos X.Y
        assert all(part.isdigit() for part in parts)

    def test_author_defined(self) -> None:
        """Testa que __author__ está definido."""
        from src.kernel_ai import __author__

        assert __author__ is not None
        assert isinstance(__author__, str)
        assert len(__author__) > 0

    def test_all_defined(self) -> None:
        """Testa que __all__ está definido."""
        from src.kernel_ai import __all__

        assert __all__ is not None
        assert isinstance(__all__, list)

    def test_all_contains_expected_exports(self) -> None:
        """Testa que __all__ contém as exportações esperadas."""
        from src.kernel_ai import __all__

        expected_exports = [
            "RLScheduler",
            "CognitiveOS",
            "ResourceOptimizer",
        ]

        for export in expected_exports:
            assert export in __all__, f"{export} não encontrado em __all__"

    def test_all_list_not_empty(self) -> None:
        """Testa que __all__ não está vazio."""
        from src.kernel_ai import __all__

        assert len(__all__) > 0

    def test_module_docstring(self) -> None:
        """Testa que o módulo tem docstring."""
        import src.kernel_ai

        assert src.kernel_ai.__doc__ is not None
        assert len(src.kernel_ai.__doc__) > 0
        assert "Kernel AI" in src.kernel_ai.__doc__

    def test_module_docstring_contains_warning(self) -> None:
        """Testa que o módulo contém aviso de segurança."""
        import src.kernel_ai

        assert "IMPORTANT" in src.kernel_ai.__doc__ or "safety" in src.kernel_ai.__doc__

    def test_module_attributes(self) -> None:
        """Testa que o módulo tem os atributos esperados."""
        import src.kernel_ai

        assert hasattr(src.kernel_ai, "__version__")
        assert hasattr(src.kernel_ai, "__author__")
        assert hasattr(src.kernel_ai, "__all__")

    def test_version_is_string(self) -> None:
        """Testa que version é uma string."""
        from src.kernel_ai import __version__

        assert isinstance(__version__, str)

    def test_author_is_string(self) -> None:
        """Testa que author é uma string."""
        from src.kernel_ai import __author__

        assert isinstance(__author__, str)

    def test_all_is_list(self) -> None:
        """Testa que __all__ é uma lista."""
        from src.kernel_ai import __all__

        assert isinstance(__all__, list)

    def test_all_items_are_strings(self) -> None:
        """Testa que todos os itens de __all__ são strings."""
        from src.kernel_ai import __all__

        assert all(isinstance(item, str) for item in __all__)


class TestInitModulesComparison:
    """Testes comparativos entre os módulos."""

    def test_both_modules_have_same_metadata_structure(self) -> None:
        """Testa que ambos os módulos seguem a mesma estrutura."""
        import src.autopoietic
        import src.kernel_ai

        # Ambos devem ter os mesmos atributos
        autopoietic_attrs = set(dir(src.autopoietic))
        kernel_ai_attrs = set(dir(src.kernel_ai))

        required_attrs = {"__version__", "__author__", "__all__", "__doc__"}

        assert required_attrs.issubset(autopoietic_attrs)
        assert required_attrs.issubset(kernel_ai_attrs)

    def test_version_numbers_are_valid(self) -> None:
        """Testa que os números de versão são válidos."""
        from src.autopoietic import __version__ as auto_version
        from src.kernel_ai import __version__ as kernel_version

        # Ambos devem ter formato X.Y.Z
        for version in [auto_version, kernel_version]:
            parts = version.split(".")
            assert len(parts) >= 2
            assert all(part.isdigit() for part in parts)

    def test_authors_are_consistent(self) -> None:
        """Testa que os autores são consistentes."""
        from src.autopoietic import __author__ as auto_author
        from src.kernel_ai import __author__ as kernel_author

        # Pode ou não ser o mesmo, mas deve ser válido
        assert len(auto_author) > 0
        assert len(kernel_author) > 0

    def test_all_exports_are_unique(self) -> None:
        """Testa que as exportações são únicas em cada módulo."""
        from src.autopoietic import __all__ as auto_all
        from src.kernel_ai import __all__ as kernel_all

        # Em cada módulo, não deve haver duplicatas
        assert len(auto_all) == len(set(auto_all))
        assert len(kernel_all) == len(set(kernel_all))


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configuração do pytest para este módulo."""
    config.addinivalue_line("markers", "init: testes de módulos __init__.py")


if __name__ == "__main__":
    # Executar testes com pytest
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=src.autopoietic",
            "--cov=src.kernel_ai",
            "--cov-report=term-missing",
        ]
    )
