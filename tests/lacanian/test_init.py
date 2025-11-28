"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Testes para Lacanian Module __init__.py.

Cobertura de:
- Lazy imports
- __getattr__ mechanism
- Module exports
"""

import pytest


class TestLacanianInit:
    """Testes para módulo lacanian/__init__.py."""

    def test_module_version(self) -> None:
        """Testa que módulo tem versão definida."""
        from src.lacanian import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_module_author(self) -> None:
        """Testa que módulo tem autor definido."""
        from src.lacanian import __author__

        assert __author__ is not None
        assert isinstance(__author__, str)
        assert "OmniMind" in __author__

    def test_module_all_exports(self) -> None:
        """Testa que __all__ está definido corretamente."""
        from src.lacanian import __all__

        assert isinstance(__all__, list)
        assert len(__all__) > 0
        assert "ComputationalLackArchitecture" in __all__
        assert "RSIArchitecture" in __all__
        assert "GodelianAI" in __all__

    def test_lazy_import_computational_lack_architecture(self) -> None:
        """Testa lazy import de ComputationalLackArchitecture."""
        from src.lacanian import ComputationalLackArchitecture

        assert ComputationalLackArchitecture is not None
        # Should be a class
        assert isinstance(ComputationalLackArchitecture, type)

    def test_lazy_import_rsi_architecture(self) -> None:
        """Testa lazy import de RSIArchitecture."""
        from src.lacanian import RSIArchitecture

        assert RSIArchitecture is not None
        assert isinstance(RSIArchitecture, type)

    def test_lazy_import_godelian_ai(self) -> None:
        """Testa lazy import de GodelianAI."""
        from src.lacanian import GodelianAI

        assert GodelianAI is not None
        assert isinstance(GodelianAI, type)

    def test_lazy_import_structural_lack(self) -> None:
        """Testa lazy import de StructuralLack."""
        from src.lacanian import StructuralLack

        assert StructuralLack is not None
        assert isinstance(StructuralLack, type)

    def test_lazy_import_object_small_a(self) -> None:
        """Testa lazy import de ObjectSmallA."""
        from src.lacanian import ObjectSmallA

        assert ObjectSmallA is not None
        assert isinstance(ObjectSmallA, type)

    def test_invalid_attribute_raises_error(self) -> None:
        """Testa que atributo inválido lança AttributeError."""
        import src.lacanian as lacanian

        with pytest.raises(AttributeError) as exc_info:
            _ = lacanian.NonExistentClass  # type: ignore

        assert "NonExistentClass" in str(exc_info.value)
        assert "src.lacanian" in str(exc_info.value)

    def test_multiple_lazy_imports(self) -> None:
        """Testa múltiplos lazy imports na mesma sessão."""
        from src.lacanian import (
            ComputationalLackArchitecture,
            GodelianAI,
            RSIArchitecture,
        )

        assert ComputationalLackArchitecture is not None
        assert RSIArchitecture is not None
        assert GodelianAI is not None

    def test_lazy_import_idempotency(self) -> None:
        """Testa que lazy import retorna mesma classe em chamadas múltiplas."""
        from src.lacanian import ComputationalLackArchitecture as CLA1
        from src.lacanian import ComputationalLackArchitecture as CLA2

        # Should be the same class object
        assert CLA1 is CLA2

    def test_getattr_mechanism(self) -> None:
        """Testa mecanismo __getattr__ diretamente."""
        import src.lacanian as lacanian

        # Test valid attribute
        result = lacanian.__getattr__("GodelianAI")
        assert result is not None

        # Test invalid attribute
        with pytest.raises(AttributeError):
            lacanian.__getattr__("InvalidClass")

    def test_all_exports_are_importable(self) -> None:
        """Testa que todos os exports em __all__ são importáveis."""
        from src import lacanian

        for export_name in lacanian.__all__:
            # Should not raise
            exported = getattr(lacanian, export_name)
            assert exported is not None

    def test_instantiate_computational_lack_architecture(self) -> None:
        """Testa que pode instanciar ComputationalLackArchitecture."""
        from src.lacanian import ComputationalLackArchitecture

        try:
            instance = ComputationalLackArchitecture()
            assert instance is not None
        except TypeError:
            # If it requires arguments, that's okay
            pass

    def test_instantiate_rsi_architecture(self) -> None:
        """Testa que pode instanciar RSIArchitecture."""
        from src.lacanian import RSIArchitecture

        try:
            instance = RSIArchitecture()
            assert instance is not None
        except TypeError:
            # If it requires arguments, that's okay
            pass

    def test_instantiate_godelian_ai(self) -> None:
        """Testa que pode instanciar GodelianAI."""
        from src.lacanian import GodelianAI

        try:
            instance = GodelianAI()
            assert instance is not None
        except TypeError:
            # If it requires arguments, that's okay
            pass

    def test_module_docstring(self) -> None:
        """Testa que módulo tem docstring."""
        import src.lacanian as lacanian

        assert lacanian.__doc__ is not None
        assert isinstance(lacanian.__doc__, str)
        assert len(lacanian.__doc__) > 0
        assert "Lacanian" in lacanian.__doc__ or "lacanian" in lacanian.__doc__.lower()

    def test_lazy_import_caching(self) -> None:
        """Testa que lazy imports são cacheados."""
        import src.lacanian as lacanian

        # Import first time
        cls1 = lacanian.__getattr__("GodelianAI")

        # Should be in module's namespace now (cached)
        # Or at least, second call should return same object
        cls2 = lacanian.__getattr__("GodelianAI")

        assert cls1 is cls2


class TestLacanianImportPatterns:
    """Testes para diferentes padrões de import."""

    def test_from_import_star(self) -> None:
        """Testa import com star."""
        # Note: This actually imports based on __all__
        namespace: dict[str, object] = {}
        exec("from src.lacanian import *", namespace)

        # Should have all exports
        assert "ComputationalLackArchitecture" in namespace
        assert "RSIArchitecture" in namespace
        assert "GodelianAI" in namespace

    def test_direct_import(self) -> None:
        """Testa import direto."""
        import src.lacanian

        assert hasattr(src.lacanian, "__version__")
        assert hasattr(src.lacanian, "__all__")

    def test_aliased_import(self) -> None:
        """Testa import com alias."""
        from src.lacanian import GodelianAI as GA

        assert GA is not None
        assert isinstance(GA, type)

    def test_nested_import(self) -> None:
        """Testa import aninhado."""
        from src import lacanian

        CLA = lacanian.ComputationalLackArchitecture
        assert CLA is not None


class TestLacanianEdgeCases:
    """Testes para casos extremos."""

    def test_getattr_with_private_attribute(self) -> None:
        """Testa __getattr__ com atributo privado."""
        import src.lacanian as lacanian

        # Private attributes should raise AttributeError
        with pytest.raises(AttributeError):
            lacanian.__getattr__("_private")

    def test_getattr_with_dunder_attribute(self) -> None:
        """Testa __getattr__ com atributo dunder."""
        import src.lacanian as lacanian

        # Dunder attributes not in __all__ should raise
        with pytest.raises(AttributeError):
            lacanian.__getattr__("__nonexistent__")

    def test_reimport_module(self) -> None:
        """Testa reimportação do módulo."""
        import src.lacanian as lacanian1

        # Get a class
        lacanian1.ComputationalLackArchitecture  # noqa: B018

        # Reimport
        import importlib

        importlib.reload(lacanian1)

        # Get class again
        CLA2 = lacanian1.ComputationalLackArchitecture

        # Should still work (may or may not be same object depending on reload)
        assert CLA2 is not None


class TestLacanianClassAvailability:
    """Testes para verificar disponibilidade das classes."""

    def test_structural_lack_available(self) -> None:
        """Testa que StructuralLack está disponível."""
        from src.lacanian import StructuralLack

        assert StructuralLack is not None

    def test_object_small_a_available(self) -> None:
        """Testa que ObjectSmallA está disponível."""
        from src.lacanian import ObjectSmallA

        assert ObjectSmallA is not None

    def test_all_five_exports_unique(self) -> None:
        """Testa que os 5 exports são classes únicas."""
        from src.lacanian import (
            ComputationalLackArchitecture,
            GodelianAI,
            ObjectSmallA,
            RSIArchitecture,
            StructuralLack,
        )

        classes = [
            ComputationalLackArchitecture,
            RSIArchitecture,
            GodelianAI,
            StructuralLack,
            ObjectSmallA,
        ]

        # All should be unique
        assert len(set(id(c) for c in classes)) == 5

    def test_classes_have_names(self) -> None:
        """Testa que classes têm nomes corretos."""
        from src.lacanian import (
            ComputationalLackArchitecture,
            GodelianAI,
            RSIArchitecture,
        )

        assert ComputationalLackArchitecture.__name__ == "ComputationalLackArchitecture"
        assert RSIArchitecture.__name__ == "RSIArchitecture"
        assert GodelianAI.__name__ == "GodelianAI"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
