"""Testes para o módulo __init__.py do coevolution.

Cobertura de:
- Lazy imports via __getattr__
- Importação de todas as classes do módulo
- Tratamento de AttributeError para imports inválidos
"""

from __future__ import annotations

import pytest


class TestCoevolutionInit:
    """Testes para o arquivo __init__.py do módulo coevolution."""

    def test_version_attribute(self) -> None:
        """Testa que __version__ está disponível."""
        from src.coevolution import __version__

        assert isinstance(__version__, str)
        assert __version__ == "0.1.0"

    def test_all_attribute(self) -> None:
        """Testa que __all__ contém todas as classes exportadas."""
        from src.coevolution import __all__

        assert isinstance(__all__, list)
        expected_exports = [
            "HCHACFramework",
            "TrustMetrics",
            "GoalNegotiator",
            "BidirectionalFeedback",
            "BiasDetector",
            "CoevolutionMemory",
        ]
        assert set(__all__) == set(expected_exports)

    def test_lazy_import_hchac_framework(self) -> None:
        """Testa lazy import de HCHACFramework."""
        from src.coevolution import HCHACFramework

        assert HCHACFramework is not None
        assert hasattr(HCHACFramework, "__init__")

    def test_lazy_import_trust_metrics(self) -> None:
        """Testa lazy import de TrustMetrics."""
        from src.coevolution import TrustMetrics

        assert TrustMetrics is not None
        assert hasattr(TrustMetrics, "__init__")

    def test_lazy_import_goal_negotiator(self) -> None:
        """Testa lazy import de GoalNegotiator."""
        from src.coevolution import GoalNegotiator

        assert GoalNegotiator is not None
        assert hasattr(GoalNegotiator, "__init__")

    def test_lazy_import_bidirectional_feedback(self) -> None:
        """Testa lazy import de BidirectionalFeedback."""
        from src.coevolution import BidirectionalFeedback

        assert BidirectionalFeedback is not None
        assert hasattr(BidirectionalFeedback, "__init__")

    def test_lazy_import_bias_detector(self) -> None:
        """Testa lazy import de BiasDetector."""
        from src.coevolution import BiasDetector

        assert BiasDetector is not None
        assert hasattr(BiasDetector, "__init__")

    def test_lazy_import_coevolution_memory(self) -> None:
        """Testa lazy import de CoevolutionMemory."""
        from src.coevolution import CoevolutionMemory

        assert CoevolutionMemory is not None
        assert hasattr(CoevolutionMemory, "__init__")

    def test_invalid_attribute_raises_error(self) -> None:
        """Testa que atributo inválido lança AttributeError."""
        import src.coevolution as coevolution_module

        with pytest.raises(AttributeError) as exc_info:
            _ = coevolution_module.NonExistentClass

        assert "has no attribute" in str(exc_info.value)
        assert "NonExistentClass" in str(exc_info.value)

    def test_all_exports_are_importable(self) -> None:
        """Testa que todas as classes em __all__ podem ser importadas."""
        import src.coevolution as coevolution_module
        from src.coevolution import __all__

        for class_name in __all__:
            cls = getattr(coevolution_module, class_name)
            assert cls is not None
            # Verifica que é uma classe
            assert hasattr(cls, "__init__")

    def test_multiple_lazy_imports(self) -> None:
        """Testa múltiplas lazy imports consecutivas."""
        from src.coevolution import (
            GoalNegotiator,
            HCHACFramework,
            TrustMetrics,
        )

        assert HCHACFramework is not None
        assert TrustMetrics is not None
        assert GoalNegotiator is not None

    def test_lazy_import_caching(self) -> None:
        """Testa que lazy imports são cacheados corretamente."""
        from src.coevolution import HCHACFramework as HCHACFramework1
        from src.coevolution import HCHACFramework as HCHACFramework2

        # Deve ser a mesma classe
        assert HCHACFramework1 is HCHACFramework2

    def test_instantiate_lazy_imported_class(self) -> None:
        """Testa que classes lazy-imported podem ser instanciadas."""
        from src.coevolution import TrustMetrics

        # Instancia a classe
        metrics = TrustMetrics()
        assert metrics is not None

    def test_lazy_import_preserves_module_structure(self) -> None:
        """Testa que lazy imports preservam a estrutura do módulo."""
        from src.coevolution import HCHACFramework

        # Verifica que a classe tem o módulo correto
        assert HCHACFramework.__module__ == "src.coevolution.hchac_framework"

    def test_import_all_at_once(self) -> None:
        """Testa importação de todas as classes de uma vez."""
        from src.coevolution import (
            BiasDetector,
            BidirectionalFeedback,
            CoevolutionMemory,
            GoalNegotiator,
            HCHACFramework,
            TrustMetrics,
        )

        classes = [
            HCHACFramework,
            TrustMetrics,
            GoalNegotiator,
            BidirectionalFeedback,
            BiasDetector,
            CoevolutionMemory,
        ]

        for cls in classes:
            assert cls is not None
            assert callable(cls)

    def test_lazy_import_error_message_format(self) -> None:
        """Testa formato da mensagem de erro para import inválido."""
        import src.coevolution as coevolution_module

        with pytest.raises(AttributeError) as exc_info:
            _ = coevolution_module.InvalidClassName

        error_message = str(exc_info.value)
        assert "module" in error_message
        assert "src.coevolution" in error_message
        assert "InvalidClassName" in error_message

    def test_getattr_function_exists(self) -> None:
        """Testa que a função __getattr__ está definida no módulo."""
        import src.coevolution as coevolution_module

        assert hasattr(coevolution_module, "__getattr__")
        assert callable(coevolution_module.__getattr__)
