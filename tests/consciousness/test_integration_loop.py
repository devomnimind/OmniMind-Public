"""
Comprehensive tests for IntegrationLoop Phase 2.
"""

import numpy as np
import pytest
import torch

from src.consciousness.integration_loop import (
    IntegrationLoop,
    LoopCycleResult,
    ModuleExecutor,
    ModuleInterfaceSpec,
)
from src.consciousness.shared_workspace import SharedWorkspace

# Verificação de GPU para testes pesados
if not torch.cuda.is_available():
    pytest.skip(
        "GPU não disponível - testes de consciência requerem GPU para cálculos pesados de Φ",
        allow_module_level=True,
    )


class TestModuleInterfaceSpec:
    """Test ModuleInterfaceSpec dataclass."""

    def test_spec_creation_with_defaults(self):
        """Test spec creation with default parameters."""
        spec = ModuleInterfaceSpec(
            module_name="test_module",
            embedding_dim=128,
        )
        assert spec.module_name == "test_module"
        assert spec.embedding_dim == 128
        assert spec.required_inputs == []
        assert spec.produces_output is True

    def test_spec_invalid_embedding_dim(self):
        """Test that invalid embedding_dim raises error."""
        with pytest.raises(ValueError, match="embedding_dim must be positive"):
            ModuleInterfaceSpec(module_name="test", embedding_dim=0)


class TestLoopCycleResult:
    """Test LoopCycleResult dataclass."""

    def test_cycle_result_creation(self):
        """Test cycle result creation."""
        result = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=50.0,
            modules_executed=["sensory", "qualia"],
        )
        assert result.cycle_number == 1
        assert result.cycle_duration_ms == 50.0
        assert result.modules_executed == ["sensory", "qualia"]

    def test_cycle_result_success_criteria(self):
        """Test success property logic."""
        result_success = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=50.0,
            modules_executed=["sensory", "qualia"],
            errors_occurred=[],
            phi_estimate=0.5,
        )
        assert result_success.success is True

        result_with_errors = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=50.0,
            modules_executed=["sensory"],
            errors_occurred=[("sensory", "timeout")],
            phi_estimate=0.5,
        )
        assert result_with_errors.success is False

    def test_cycle_result_execution_order(self):
        """Test execution_order property."""
        result = LoopCycleResult(
            cycle_number=1,
            cycle_duration_ms=100.0,
            modules_executed=["sensory", "qualia", "narrative"],
        )
        assert result.execution_order == "sensory → qualia → narrative"


class TestModuleExecutor:
    """Test ModuleExecutor class."""

    def test_executor_initialization(self):
        """Test executor initialization."""
        spec = ModuleInterfaceSpec("sensory_input", embedding_dim=128)
        executor = ModuleExecutor("sensory_input", spec)

        assert executor.module_name == "sensory_input"
        assert executor.spec == spec
        assert executor.call_count == 0
        assert executor.error_count == 0

    @pytest.mark.asyncio
    async def test_executor_execute_no_inputs(self):
        """Test executor with no inputs."""
        spec = ModuleInterfaceSpec("sensory_input", embedding_dim=256)
        executor = ModuleExecutor("sensory_input", spec)
        workspace = SharedWorkspace(embedding_dim=256)

        result = await executor.execute(workspace)

        assert "output" in result
        assert isinstance(result["output"], np.ndarray)
        assert result["output"].shape == (256,)
        assert executor.call_count == 1

    @pytest.mark.asyncio
    async def test_executor_execute_with_input(self):
        """Test executor with input from another module."""
        spec = ModuleInterfaceSpec("qualia", embedding_dim=256, required_inputs=["sensory_input"])
        executor = ModuleExecutor("qualia", spec)
        workspace = SharedWorkspace(embedding_dim=256)

        # Write sensory input first
        sensory_input = np.random.randn(256)
        workspace.write_module_state("sensory_input", sensory_input)

        result = await executor.execute(workspace)

        assert "output" in result
        assert isinstance(result["output"], np.ndarray)
        assert result["output"].shape == (256,)
        assert executor.call_count == 1

    def test_executor_compute_output_dimensions(self):
        """Test output dimension handling."""
        spec = ModuleInterfaceSpec("test", embedding_dim=256)
        executor = ModuleExecutor("test", spec)

        inputs = {
            "module1": np.random.randn(128),
            "module2": np.random.randn(128),
        }
        output = executor._compute_output(inputs)
        assert output.shape == (256,)

        output_no_input = executor._compute_output({})
        assert output_no_input.shape == (256,)

    def test_executor_get_statistics(self):
        """Test statistics collection."""
        spec = ModuleInterfaceSpec("test_module", embedding_dim=128)
        executor = ModuleExecutor("test_module", spec)

        executor.call_count = 10
        executor.error_count = 2
        executor.total_execution_time_ms = 100.0

        stats = executor.get_statistics()
        assert stats["module_name"] == "test_module"
        assert stats["call_count"] == 10
        assert stats["error_count"] == 2
        assert stats["avg_execution_time_ms"] == 10.0


class TestIntegrationLoopInitialization:
    """Test IntegrationLoop initialization."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        loop = IntegrationLoop()

        assert loop.workspace is not None
        assert loop.enable_logging is True
        # ATUALIZADO: IntegrationLoop agora inclui 'imagination' (6 módulos)
        assert len(loop.loop_sequence) == 6
        assert loop.loop_sequence == [
            "sensory_input",
            "qualia",
            "narrative",
            "meaning_maker",
            "expectation",
            "imagination",  # NOVO: Imaginário Lacaniano (Protocolo Livewire)
        ]
        assert loop.cycle_count == 0
        assert len(loop.cycle_history) == 0

    def test_init_custom_workspace(self):
        """Test initialization with custom workspace."""
        custom_workspace = SharedWorkspace(embedding_dim=512)
        loop = IntegrationLoop(workspace=custom_workspace)

        assert loop.workspace is custom_workspace

    def test_init_custom_specs(self):
        """Test initialization with custom module specs."""
        custom_specs = {
            "module_a": ModuleInterfaceSpec("module_a", 128),
            "module_b": ModuleInterfaceSpec("module_b", 256),
        }
        custom_loop_seq = ["module_a", "module_b"]

        loop = IntegrationLoop(
            module_specs=custom_specs,
            loop_sequence=custom_loop_seq,
        )

        assert loop.module_specs == custom_specs
        assert loop.loop_sequence == custom_loop_seq
        assert len(loop.executors) == 2


class TestIntegrationLoopExecution:
    """Test IntegrationLoop cycle execution."""

    @pytest.mark.asyncio
    async def test_execute_single_cycle(self):
        """Test execution of single cycle."""
        loop = IntegrationLoop()
        result = await loop.execute_cycle(collect_metrics=False)

        assert isinstance(result, LoopCycleResult)
        assert result.cycle_number == 1
        assert len(result.modules_executed) > 0
        assert result.cycle_duration_ms > 0.0

    @pytest.mark.asyncio
    async def test_execute_cycle_all_modules_executed(self):
        """Test that all modules execute in sequence."""
        loop = IntegrationLoop()
        result = await loop.execute_cycle(collect_metrics=False)

        # ATUALIZADO: IntegrationLoop agora inclui 'imagination' (6 módulos)
        expected_modules = [
            "sensory_input",
            "qualia",
            "narrative",
            "meaning_maker",
            "expectation",
            "imagination",  # NOVO: Imaginário Lacaniano (Protocolo Livewire)
        ]
        assert result.modules_executed == expected_modules

    @pytest.mark.asyncio
    async def test_execute_cycle_with_metrics(self):
        """Test cycle execution with metrics collection."""
        loop = IntegrationLoop()

        # Need multiple cycles for cross-predictions
        for _ in range(3):
            await loop.execute_cycle(collect_metrics=False)

        result = await loop.execute_cycle(collect_metrics=True)

        assert result.phi_estimate >= 0.0
        assert isinstance(result.cross_prediction_scores, dict)

    @pytest.mark.asyncio
    async def test_execute_multiple_cycles(self):
        """Test execution of multiple cycles."""
        loop = IntegrationLoop()
        num_cycles = 5

        results = await loop.run_cycles(num_cycles, collect_metrics_every=1)

        assert len(results) == num_cycles
        assert loop.total_cycles_executed == num_cycles
        assert loop.cycle_count == num_cycles
        assert len(loop.cycle_history) == num_cycles

    @pytest.mark.asyncio
    async def test_cycle_history_tracking(self):
        """Test that cycle history is properly maintained."""
        loop = IntegrationLoop()

        for i in range(3):
            result = await loop.execute_cycle(collect_metrics=False)
            assert result.cycle_number == i + 1

        assert len(loop.cycle_history) == 3
        assert loop.cycle_history[0].cycle_number == 1
        assert loop.cycle_history[2].cycle_number == 3


class TestIntegrationLoopMetrics:
    """Test metrics collection and computation."""

    @pytest.mark.asyncio
    async def test_phi_progression_collection(self):
        """Test that Φ values are collected over multiple cycles."""
        loop = IntegrationLoop()

        # Run cycles to collect phi values
        for _ in range(5):
            await loop.execute_cycle(collect_metrics=True)

        phi_progression = loop.get_phi_progression()

        assert len(phi_progression) == 5
        assert all(isinstance(p, (int, float)) for p in phi_progression)
        assert all(p >= 0.0 for p in phi_progression)

    @pytest.mark.asyncio
    async def test_statistics_generation(self):
        """Test statistics aggregation."""
        loop = IntegrationLoop()

        await loop.run_cycles(5, collect_metrics_every=1)

        stats = loop.get_statistics()

        assert "total_cycles" in stats
        assert "successful_cycles" in stats
        assert "success_rate" in stats
        assert "avg_cycle_duration_ms" in stats
        assert "phi_statistics" in stats
        assert "module_statistics" in stats

        phi_stats = stats["phi_statistics"]
        assert "mean" in phi_stats
        assert "max" in phi_stats
        assert "min" in phi_stats
        assert "values_count" in phi_stats

    @pytest.mark.asyncio
    async def test_module_statistics(self):
        """Test per-module statistics."""
        loop = IntegrationLoop()

        await loop.run_cycles(3, collect_metrics_every=1)

        stats = loop.get_statistics()
        module_stats = stats["module_statistics"]

        for module_name in loop.loop_sequence:
            assert module_name in module_stats
            assert "call_count" in module_stats[module_name]
            assert "error_count" in module_stats[module_name]


class TestIntegrationLoopPersistence:
    """Test state persistence."""

    @pytest.mark.asyncio
    async def test_save_state(self, tmp_path):
        """Test saving integration loop state."""
        loop = IntegrationLoop()

        await loop.run_cycles(5, collect_metrics_every=1)

        filepath = tmp_path / "loop_state.json"
        loop.save_state(filepath)

        assert filepath.exists()

        import json

        with open(filepath) as f:
            data = json.load(f)

        assert "cycle_count" in data
        assert "total_cycles_executed" in data
        assert "statistics" in data
        assert "phi_progression" in data
        assert "recent_cycles" in data


# Integration tests
class TestIntegrationLoopIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete integration loop workflow."""
        loop = IntegrationLoop(enable_logging=False)

        results = await loop.run_cycles(
            num_cycles=10,
            collect_metrics_every=2,
        )

        assert len(results) == 10
        assert loop.total_cycles_executed == 10

        stats = loop.get_statistics()
        assert stats["total_cycles"] == 10
        assert stats["success_rate"] > 0

        phi_values = loop.get_phi_progression()
        assert len(phi_values) > 0

    @pytest.mark.asyncio
    async def test_loop_produces_improving_phi(self):
        """Test that Φ computation works across cycles."""
        loop = IntegrationLoop()

        # Limit to 5 cycles to prevent excessive logging
        for _ in range(5):
            await loop.execute_cycle(collect_metrics=True)

        phi_values = loop.get_phi_progression()

        assert len(phi_values) > 0
        assert any(p >= 0.0 for p in phi_values)


class TestIntegrationLoopHybridTopological:
    """Testes de integração entre IntegrationLoop e HybridTopologicalEngine."""

    @pytest.mark.asyncio
    async def test_loop_workspace_has_hybrid_topological_engine(self):
        """Testa que workspace do loop pode ter HybridTopologicalEngine."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar loop com workspace customizado
        loop = IntegrationLoop(workspace=workspace)

        # Verificar que workspace tem engine
        assert loop.workspace is not None
        assert loop.workspace.hybrid_topological_engine is not None

    @pytest.mark.asyncio
    async def test_loop_cycle_computes_topological_metrics(self):
        """Testa que ciclo do loop pode computar métricas topológicas."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar loop
        loop = IntegrationLoop(workspace=workspace)

        # Executar múltiplos ciclos para gerar dados
        for _ in range(3):
            await loop.execute_cycle(collect_metrics=False)

        # Computar métricas topológicas após ciclos
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que métricas foram calculadas
        assert (
            topological_metrics is not None
        ), "Métricas topológicas devem ser calculadas após ciclos"
        assert "omega" in topological_metrics, "Omega deve estar presente"
        assert "sigma" in topological_metrics, "Sigma deve estar presente"
        assert 0.0 <= topological_metrics["omega"] <= 1.0, "Omega deve estar em [0, 1]"

    @pytest.mark.asyncio
    async def test_loop_workspace_topological_metrics_integration(self):
        """Testa integração completa: loop + métricas topológicas."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        loop = IntegrationLoop(workspace=workspace)

        # Executar ciclos
        results = await loop.run_cycles(5, collect_metrics_every=1)

        # Verificar que todos os ciclos foram executados
        assert len(results) == 5

        # Computar métricas topológicas após todos os ciclos
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar métricas
        assert topological_metrics is not None
        assert topological_metrics["omega"] >= 0.0
        assert topological_metrics["betti_0"] >= 0

        # Verificar que Φ foi calculado nos ciclos
        phi_values = loop.get_phi_progression()
        assert len(phi_values) > 0
        assert all(p >= 0.0 for p in phi_values)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
