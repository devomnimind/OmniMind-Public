import pytest
        from src.attention import __all__
        from src.attention import MultiHeadThermodynamicAttention
        import src.attention as attention
        import src.attention
        from src.attention import __all__

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
Testes para src/attention/__init__.py.

Testa lazy imports e atributos do módulo.
"""



class TestAttentionInit:
    """Testes para módulo attention.__init__."""

    def test_module_all_attribute(self) -> None:
        """Testa que __all__ contém as classes corretas."""

        assert "ThermodynamicAttention" in __all__
        assert "MultiHeadThermodynamicAttention" in __all__
        assert len(__all__) == 2

    def test_lazy_import_thermodynamic_attention(self) -> None:
        """Testa lazy import de ThermodynamicAttention."""
        # Import should work via lazy loading
        from src.attention import ThermodynamicAttention

        assert ThermodynamicAttention is not None
        assert hasattr(ThermodynamicAttention, "__name__")

    def test_lazy_import_multihead_thermodynamic_attention(self) -> None:
        """Testa lazy import de MultiHeadThermodynamicAttention."""

        assert MultiHeadThermodynamicAttention is not None
        assert hasattr(MultiHeadThermodynamicAttention, "__name__")

    def test_getattr_with_invalid_name(self) -> None:
        """Testa que __getattr__ levanta AttributeError para nome inválido."""
        import src.attention as attention

        with pytest.raises(AttributeError, match="has no attribute"):
            _ = attention.NonExistentClass  # type: ignore

    def test_getattr_thermodynamic_attention(self) -> None:
        """Testa que __getattr__ retorna ThermodynamicAttention."""

        ThermodynamicAttention = attention.ThermodynamicAttention
        assert ThermodynamicAttention is not None

    def test_getattr_multihead_thermodynamic_attention(self) -> None:
        """Testa que __getattr__ retorna MultiHeadThermodynamicAttention."""
        import src.attention as attention

        MultiHeadThermodynamicAttention = attention.MultiHeadThermodynamicAttention
        assert MultiHeadThermodynamicAttention is not None

    def test_type_checking_imports(self) -> None:
        """Testa que TYPE_CHECKING imports estão corretos."""
        # This test verifies the structure is correct
        # The actual imports are only evaluated during type checking

        # Check module has the __getattr__ function
        assert hasattr(src.attention, "__getattr__")

    def test_multiple_imports_same_class(self) -> None:
        """Testa que múltiplos imports retornam a mesma classe."""
        from src.attention import ThermodynamicAttention as TA1
        from src.attention import ThermodynamicAttention as TA2

        # Should be the same class
        assert TA1 is TA2

    def test_import_all_classes(self) -> None:
        """Testa que todas as classes em __all__ podem ser importadas."""

        for class_name in __all__:
            # Dynamic import
            module = __import__("src.attention", fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls is not None
            assert hasattr(cls, "__name__")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
