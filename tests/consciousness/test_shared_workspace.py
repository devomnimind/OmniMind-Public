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
Testes para Shared Workspace - Verificar leitura/escrita e cálculos de integração.

Author: OmniMind Development Team
Date: November 2025
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.consciousness.shared_workspace import CrossPredictionMetrics, SharedWorkspace


class TestSharedWorkspaceInit:
    """Testes de inicialização do workspace."""

    def test_init_default_params(self) -> None:
        """Testa inicialização com parâmetros padrão."""
        workspace = SharedWorkspace()

        assert workspace.embedding_dim == 256
        assert workspace.max_history_size == 10000
        assert workspace.cycle_count == 0
        assert len(workspace.embeddings) == 0
        assert len(workspace.history) == 0

    def test_init_custom_params(self) -> None:
        """Testa inicialização com parâmetros customizados."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = SharedWorkspace(
                embedding_dim=128,
                max_history_size=5000,
                workspace_dir=Path(tmpdir),
            )

            assert workspace.embedding_dim == 128
            assert workspace.max_history_size == 5000
            assert workspace.workspace_dir == Path(tmpdir)


class TestWriteReadModuleState:
    """Testes de escrita e leitura de estados de módulos."""

    @pytest.fixture
    def workspace(self) -> SharedWorkspace:
        return SharedWorkspace(embedding_dim=128)

    def test_write_module_state_basic(self, workspace: SharedWorkspace) -> None:
        """Testa escrita básica de estado."""
        embedding = np.random.randn(128)
        workspace.write_module_state("qualia", embedding)

        assert "qualia" in workspace.embeddings
        assert np.allclose(workspace.embeddings["qualia"], embedding)
        assert len(workspace.history) == 1

    def test_write_multiple_modules(self, workspace: SharedWorkspace) -> None:
        """Testa escrita de múltiplos módulos."""
        modules = ["qualia", "narrative", "meaning"]
        embeddings = {m: np.random.randn(128) for m in modules}

        for m, emb in embeddings.items():
            workspace.write_module_state(m, emb)

        assert len(workspace.embeddings) == 3
        assert len(workspace.history) == 3
        assert all(np.allclose(workspace.embeddings[m], embeddings[m]) for m in modules)

    def test_read_nonexistent_module(self, workspace: SharedWorkspace) -> None:
        """Testa leitura de módulo que não existe."""
        result = workspace.read_module_state("nonexistent")

        assert result.shape == (128,)
        assert np.allclose(result, np.zeros(128))

    def test_write_wrong_dimension_raises(self, workspace: SharedWorkspace) -> None:
        """Testa que escrita com dimensão errada lança erro."""
        embedding = np.random.randn(256)  # Dimensão errada

        with pytest.raises(ValueError):
            workspace.write_module_state("qualia", embedding)

    def test_read_module_metadata(self, workspace: SharedWorkspace) -> None:
        """Testa leitura de metadata."""
        embedding = np.random.randn(128)
        metadata = {"confidence": 0.95, "source": "sensory"}

        workspace.write_module_state("qualia", embedding, metadata)

        retrieved_metadata = workspace.read_module_metadata("qualia")
        assert retrieved_metadata == metadata


class TestModuleHistory:
    """Testes de histórico de módulos."""

    @pytest.fixture
    def workspace(self) -> SharedWorkspace:
        workspace = SharedWorkspace(embedding_dim=64)
        # Escreve 10 ciclos para cada módulo
        for i in range(10):
            emb1 = np.random.randn(64)
            emb2 = np.random.randn(64) + i * 0.1  # Muda lentamente
            workspace.write_module_state("qualia", emb1)
            workspace.write_module_state("narrative", emb2)
            workspace.advance_cycle()
        return workspace

    def test_get_module_history(self, workspace: SharedWorkspace) -> None:
        """Testa recuperação de histórico."""
        history = workspace.get_module_history("qualia")

        assert len(history) == 10
        assert all(s.module_name == "qualia" for s in history)

    def test_get_module_history_limited(self, workspace: SharedWorkspace) -> None:
        """Testa recuperação de últimos N estados."""
        history = workspace.get_module_history("qualia", last_n=5)

        assert len(history) == 5
        assert history[0].cycle == 5

    def test_all_modules_list(self, workspace: SharedWorkspace) -> None:
        """Testa lista de módulos ativos."""
        modules = workspace.get_all_modules()

        assert set(modules) == {"qualia", "narrative"}


class TestCrossPrediction:
    """Testes de predições cruzadas entre módulos."""

    @pytest.fixture
    def workspace_with_correlated_data(self) -> SharedWorkspace:
        """Workspace com dados correlacionados deliberadamente."""
        workspace = SharedWorkspace(embedding_dim=64)

        # Módulo A: série aleatória
        # Módulo B: série correlacionada com A (B = 0.8*A + noise)
        np.random.seed(42)
        for i in range(100):
            a = np.random.randn(64)
            b = 0.8 * a + 0.2 * np.random.randn(64)  # Correlacionado
            workspace.write_module_state("moduleA", a)
            workspace.write_module_state("moduleB", b)
            workspace.advance_cycle()

        return workspace

    def test_compute_cross_prediction_basic(
        self, workspace_with_correlated_data: SharedWorkspace
    ) -> None:
        """Testa cálculo básico de predição cruzada."""
        metrics = workspace_with_correlated_data.compute_cross_prediction("moduleA", "moduleB")

        assert isinstance(metrics, CrossPredictionMetrics)
        assert 0.0 <= metrics.r_squared <= 1.0
        assert 0.0 <= metrics.correlation <= 1.0
        assert 0.0 <= metrics.mutual_information <= 1.0

    def test_correlated_modules_have_high_prediction(
        self, workspace_with_correlated_data: SharedWorkspace
    ) -> None:
        """Testa que módulos correlacionados têm alta predição."""
        metrics = workspace_with_correlated_data.compute_cross_prediction("moduleA", "moduleB")

        # B é altamente determinístico a partir de A
        assert (
            metrics.r_squared > 0.3
        ), f"Expected high R² for correlated modules, got {metrics.r_squared}"

    def test_compute_cross_prediction_empty_workspace(self) -> None:
        """Testa predição cruzada em workspace vazio."""
        workspace = SharedWorkspace()
        metrics = workspace.compute_cross_prediction("A", "B")

        assert metrics.r_squared == 0.0
        assert metrics.correlation == 0.0


class TestPhiComputation:
    """Testes de cálculo de Φ (Phi)."""

    def test_phi_empty_workspace(self) -> None:
        """Testa que Φ = 0 em workspace vazio."""
        workspace = SharedWorkspace()
        phi = workspace.compute_phi_from_integrations()

        assert phi == 0.0

    def test_phi_with_predictions(self) -> None:
        """Testa que Φ aumenta com mais predições cruzadas."""
        workspace = SharedWorkspace(embedding_dim=64)

        # Simula dados correlacionados
        np.random.seed(42)
        for i in range(50):
            a = np.random.randn(64)
            b = 0.7 * a + 0.3 * np.random.randn(64)
            c = 0.6 * b + 0.4 * np.random.randn(64)

            workspace.write_module_state("A", a)
            workspace.write_module_state("B", b)
            workspace.write_module_state("C", c)
            workspace.advance_cycle()

        # Computa todas as predições cruzadas
        for source in ["A", "B", "C"]:
            for target in ["A", "B", "C"]:
                if source != target:
                    workspace.compute_cross_prediction(source, target)

        phi = workspace.compute_phi_from_integrations()

        assert phi > 0.0, f"Expected Φ > 0 with correlated modules, got {phi}"


class TestWorkspacePersistence:
    """Testes de persistência e snapshots."""

    def test_save_state_snapshot(self) -> None:
        """Testa salvamento de snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = SharedWorkspace(workspace_dir=Path(tmpdir))

            # Escreve alguns dados
            workspace.write_module_state("qualia", np.random.randn(256))
            workspace.write_module_state("narrative", np.random.randn(256))

            # Salva snapshot
            filepath = workspace.save_state_snapshot(label="test_snapshot")

            assert filepath.exists()
            assert "workspace_snapshot" in filepath.name

    def test_get_statistics(self) -> None:
        """Testa estatísticas do workspace."""
        workspace = SharedWorkspace(embedding_dim=128)

        for i in range(20):
            workspace.write_module_state("A", np.random.randn(128))
            workspace.write_module_state("B", np.random.randn(128))
            workspace.advance_cycle()

        stats = workspace.get_statistics()

        assert stats["active_modules"] == 2
        assert stats["total_cycles"] == 20
        assert stats["history_size"] == 40
        assert "phi" in stats

    def test_repr(self) -> None:
        """Testa representação em string."""
        workspace = SharedWorkspace()
        workspace.write_module_state("test", np.random.randn(256))

        repr_str = repr(workspace)

        assert "SharedWorkspace" in repr_str
        assert "modules=1" in repr_str


class TestAdvanceCycle:
    """Testes de avanço de ciclo."""

    def test_advance_cycle(self) -> None:
        """Testa avanço de ciclo."""
        workspace = SharedWorkspace()

        assert workspace.cycle_count == 0

        workspace.advance_cycle()
        assert workspace.cycle_count == 1

        workspace.advance_cycle()
        assert workspace.cycle_count == 2

    def test_cycle_recorded_in_history(self) -> None:
        """Testa que ciclo é registrado no histórico."""
        workspace = SharedWorkspace()

        for i in range(5):
            embedding = np.random.randn(256)
            workspace.write_module_state("test", embedding)
            workspace.advance_cycle()

        history = workspace.get_module_history("test")

        cycles = [s.cycle for s in history]
        assert cycles == list(range(5))


class TestHistoryCirculation:
    """Testes de circulação de histórico quando limite é atingido."""

    def test_history_max_size_respected(self) -> None:
        """Testa que histórico não ultrapassa max_history_size."""
        max_size = 100
        workspace = SharedWorkspace(embedding_dim=64, max_history_size=max_size)

        # Escreve mais que max_size
        for i in range(150):
            embedding = np.random.randn(64)
            workspace.write_module_state("test", embedding)

        assert len(workspace.history) == max_size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
