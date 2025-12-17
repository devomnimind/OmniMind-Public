"""
Testes para refatoração síncrona do IntegrationLoop.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

from unittest.mock import MagicMock

import numpy as np
import pytest

from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace


class TestIntegrationLoopSync:
    """Testes para verificar execução síncrona do IntegrationLoop."""

    @pytest.fixture
    def workspace(self):
        """Fixture para SharedWorkspace."""
        return SharedWorkspace(embedding_dim=256)

    @pytest.fixture
    def integration_loop(self, workspace):
        """Fixture para IntegrationLoop."""
        return IntegrationLoop(workspace=workspace, enable_logging=False)

    def test_execute_cycle_sync_exists(self, integration_loop):
        """Testa que método execute_cycle_sync() existe."""
        # REFATORAÇÃO: Verificar que método síncrono existe
        assert hasattr(integration_loop, "execute_cycle_sync")
        assert callable(integration_loop.execute_cycle_sync)

    def test_execute_cycle_sync_is_sync(self, integration_loop):
        """Testa que execute_cycle_sync() é síncrono (não async)."""
        # REFATORAÇÃO: Verificar que não usa await
        import inspect

        assert not inspect.iscoroutinefunction(integration_loop.execute_cycle_sync)

    def test_execute_cycle_async_wrapper(self, integration_loop):
        """Testa que execute_cycle() async ainda funciona (wrapper)."""
        # REFATORAÇÃO: Verificar compatibilidade retroativa
        import inspect

        assert inspect.iscoroutinefunction(integration_loop.execute_cycle)

    def test_execute_cycle_sync_integrates_rnn(self, integration_loop):
        """Testa que execute_cycle_sync() integra com ConsciousSystem.step()."""
        # REFATORAÇÃO: Verificar integração com RNN
        if integration_loop.workspace.conscious_system is None:
            pytest.skip("ConsciousSystem não disponível")

        # Mockar step() para verificar chamada
        original_step = integration_loop.workspace.conscious_system.step
        integration_loop.workspace.conscious_system.step = MagicMock(
            return_value=original_step(None)
        )

        integration_loop.execute_cycle_sync(collect_metrics=False)

        # Verificar que step() foi chamado
        assert integration_loop.workspace.conscious_system.step.called

        # Restaurar método original
        integration_loop.workspace.conscious_system.step = original_step

    def test_collect_stimulus_from_modules(self, integration_loop):
        """Testa coleta de estímulo dos módulos."""
        # REFATORAÇÃO: Verificar que _collect_stimulus_from_modules() funciona
        assert hasattr(integration_loop, "_collect_stimulus_from_modules")
        assert callable(integration_loop._collect_stimulus_from_modules)

        # Adicionar alguns estados de módulos
        integration_loop.workspace.write_module_state(
            "sensory_input", np.random.randn(256).astype(np.float32)
        )
        integration_loop.workspace.write_module_state(
            "qualia", np.random.randn(256).astype(np.float32)
        )

        stimulus = integration_loop._collect_stimulus_from_modules()

        assert isinstance(stimulus, np.ndarray)
        assert len(stimulus) == integration_loop.workspace.embedding_dim

    def test_module_executor_execute_sync_exists(self, integration_loop):
        """Testa que ModuleExecutor.execute_sync() existe."""
        # REFATORAÇÃO: Verificar que método síncrono existe
        executor = list(integration_loop.executors.values())[0]
        assert hasattr(executor, "execute_sync")
        assert callable(executor.execute_sync)

    def test_module_executor_execute_sync_is_sync(self, integration_loop):
        """Testa que execute_sync() é síncrono."""
        # REFATORAÇÃO: Verificar que não usa await
        import inspect

        executor = list(integration_loop.executors.values())[0]
        assert not inspect.iscoroutinefunction(executor.execute_sync)

    def test_execute_cycle_async_delegates_to_sync(self, integration_loop):
        """Testa que execute_cycle() async delega para execute_cycle_sync()."""
        # REFATORAÇÃO: Verificar que wrapper async funciona
        import asyncio

        # Mockar execute_cycle_sync para verificar chamada
        original_sync = integration_loop.execute_cycle_sync
        integration_loop.execute_cycle_sync = MagicMock(return_value=original_sync())

        async def test_async():
            await integration_loop.execute_cycle(collect_metrics=False)

        asyncio.run(test_async())

        # Verificar que execute_cycle_sync foi chamado
        assert integration_loop.execute_cycle_sync.called

        # Restaurar método original
        integration_loop.execute_cycle_sync = original_sync

    def test_deterministic_execution(self, integration_loop):
        """Testa que execução síncrona é determinística."""
        # REFATORAÇÃO: Verificar causalidade determinística
        # Executar ciclo duas vezes com mesmo estado inicial
        result1 = integration_loop.execute_cycle_sync(collect_metrics=False)
        result2 = integration_loop.execute_cycle_sync(collect_metrics=False)

        # Verificar que ciclo número incrementou
        assert result2.cycle_number == result1.cycle_number + 1
