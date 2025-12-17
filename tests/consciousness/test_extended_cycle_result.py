"""
Testes para ExtendedLoopCycleResult e componentes relacionados.

Valida compatibilidade e funcionalidade básica.
"""

import numpy as np
import pytest

from src.consciousness.cycle_result_builder import LoopCycleResultBuilder
from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult
from src.consciousness.integration_loop import IntegrationLoop, LoopCycleResult
from src.consciousness.shared_workspace import SharedWorkspace


class TestExtendedLoopCycleResult:
    """Testes para ExtendedLoopCycleResult."""

    def test_from_base_result(self):
        """Testa criação a partir de LoopCycleResult base."""
        base = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=100.0,
            modules_executed=["sensory_input", "qualia"],
            phi_estimate=0.5,
        )

        extended = ExtendedLoopCycleResult.from_base_result(
            base_result=base,
            module_outputs={"sensory_input": np.array([1.0, 2.0, 3.0])},
            module_activations={"sensory_input": 0.8},
            psi=0.6,
            sigma=0.4,
        )

        assert extended.cycle_number == 1
        assert extended.phi_estimate == 0.5
        assert extended.psi == 0.6
        assert extended.sigma == 0.4
        assert extended.has_extended_data()

    def test_compatibility_with_base(self):
        """Testa que scripts antigos continuam funcionando."""
        base = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=100.0,
            modules_executed=["sensory_input"],
            phi_estimate=0.5,
        )

        # Script antigo que só usa phi
        phi = base.phi_estimate
        assert phi == 0.5

        # Extended também funciona
        extended = ExtendedLoopCycleResult.from_base_result(base_result=base)
        assert extended.phi_estimate == 0.5
        assert extended.psi is None  # Campos opcionais são None por padrão


class TestLoopCycleResultBuilder:
    """Testes para LoopCycleResultBuilder."""

    def test_build_from_workspace(self):
        """Testa construção a partir de workspace."""
        workspace = SharedWorkspace(embedding_dim=256)

        # Escreve alguns módulos
        workspace.write_module_state("sensory_input", np.random.randn(256))
        workspace.write_module_state("qualia", np.random.randn(256))

        base = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=100.0,
            modules_executed=["sensory_input", "qualia"],
            phi_estimate=0.5,
        )

        builder = LoopCycleResultBuilder(workspace)
        extended = builder.build_from_workspace(base)

        assert extended.module_outputs is not None
        assert "sensory_input" in extended.module_outputs
        assert "qualia" in extended.module_outputs
        assert extended.module_activations is not None
        assert extended.integration_strength is not None
        assert 0.0 <= extended.integration_strength <= 1.0


class TestExtendedCycleResultHybridTopological:
    """Testes de integração entre ExtendedLoopCycleResult e HybridTopologicalEngine."""

    def test_extended_result_with_topological_metrics(self):
        """Testa que ExtendedLoopCycleResult pode incluir métricas topológicas."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Escrever estados
        workspace.write_module_state("sensory_input", np.random.randn(256))
        workspace.write_module_state("qualia", np.random.randn(256))

        base = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=100.0,
            modules_executed=["sensory_input", "qualia"],
            phi_estimate=0.5,
        )

        builder = LoopCycleResultBuilder(workspace)
        extended = builder.build_from_workspace(base)

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que extended result foi criado
        assert extended.module_outputs is not None
        assert extended.integration_strength is not None

        # Verificar que métricas topológicas podem ser acessadas separadamente
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Em produção, extended result poderia incluir topological_metrics como metadata

    def test_extended_result_integration_with_topological(self):
        """Testa integração completa: ExtendedResult + TopologicalMetrics."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Simular múltiplos ciclos
        for i in range(5):
            workspace.write_module_state("sensory_input", np.random.randn(256))
            workspace.write_module_state("qualia", np.random.randn(256))
            workspace.advance_cycle()

        base = LoopCycleResult(
            cycle_number=5,
            cycle_duration_ms=100.0,
            modules_executed=["sensory_input", "qualia"],
            phi_estimate=0.6,
        )

        builder = LoopCycleResultBuilder(workspace)
        extended = builder.build_from_workspace(base)

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar integração
        assert extended.phi_estimate == 0.6
        assert extended.integration_strength is not None
        if topological_metrics is not None:
            assert topological_metrics["omega"] >= 0.0
            # Ambas as métricas são complementares


@pytest.mark.asyncio
class TestIntegrationLoopExtended:
    """Testes para IntegrationLoop com extended results."""

    async def test_extended_results_disabled(self):
        """Testa que extended results desabilitado retorna LoopCycleResult normal."""
        loop = IntegrationLoop(enable_extended_results=False, enable_logging=False)
        result = await loop.execute_cycle(collect_metrics=True)

        # Deve ser LoopCycleResult, não ExtendedLoopCycleResult
        assert isinstance(result, LoopCycleResult)
        assert not isinstance(result, ExtendedLoopCycleResult)

    async def test_extended_results_enabled(self):
        """Testa que extended results habilitado retorna ExtendedLoopCycleResult."""
        loop = IntegrationLoop(enable_extended_results=True, enable_logging=False)
        result = await loop.execute_cycle(collect_metrics=True)

        # Deve ser ExtendedLoopCycleResult
        assert isinstance(result, ExtendedLoopCycleResult)
        assert result.has_extended_data()

        # Campos estendidos devem estar presentes
        assert result.module_outputs is not None
        assert result.module_activations is not None
        assert result.integration_strength is not None
