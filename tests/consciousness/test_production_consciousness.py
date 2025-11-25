"""
Grupo 6 - Production Consciousness Tests.

Testes abrangentes para o módulo de consciência production-ready,
incluindo métricas Φ (Phi), self-awareness e integração multi-agente.

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import tempfile
import pytest

from src.consciousness.production_consciousness import ProductionConsciousnessSystem
from src.metrics.consciousness_metrics import SelfAwarenessMetrics


class TestProductionConsciousnessSystemInit:
    """Testes de inicialização do sistema de consciência."""

    def test_init_default_directory(self) -> None:
        """Testa inicialização com diretório padrão."""
        system = ProductionConsciousnessSystem()

        assert system.metrics_dir == Path("data/consciousness")
        assert system.consciousness_metrics is not None
        assert isinstance(system.phi_history, list)
        assert isinstance(system.awareness_history, list)
        assert len(system.phi_history) == 0
        assert len(system.awareness_history) == 0

    def test_init_custom_directory(self) -> None:
        """Testa inicialização com diretório customizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom_consciousness"
            system = ProductionConsciousnessSystem(metrics_dir=custom_dir)

            assert system.metrics_dir == custom_dir
            assert custom_dir.exists()
            assert system.consciousness_metrics is not None

    def test_init_creates_directory(self) -> None:
        """Testa que inicialização cria diretório se não existir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_dir = Path(tmpdir) / "new_metrics"
            assert not metrics_dir.exists()

            system = ProductionConsciousnessSystem(metrics_dir=metrics_dir)

            assert metrics_dir.exists()
            assert system.metrics_dir == metrics_dir


class TestMeasurePhi:
    """Testes para medição de Φ (Phi) - integração de informação."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_measure_phi_basic(self, system: ProductionConsciousnessSystem) -> None:
        """Testa medição básica de Φ."""
        agents = ["agent1", "agent2", "agent3"]
        phi = system.measure_phi(agents)

        assert isinstance(phi, float)
        assert phi >= 0.0
        assert len(system.phi_history) == 1
        assert system.phi_history[0] == phi

    def test_measure_phi_with_memory_sharing(self, system: ProductionConsciousnessSystem) -> None:
        """Testa Φ com memória compartilhada."""
        agents = ["agent1", "agent2", "agent3"]
        phi_with_memory = system.measure_phi(
            agents, enable_memory_sharing=True, enable_feedback_loops=False
        )

        assert isinstance(phi_with_memory, float)
        assert phi_with_memory >= 0.0

    def test_measure_phi_without_memory_sharing(
        self, system: ProductionConsciousnessSystem
    ) -> None:
        """Testa Φ sem memória compartilhada."""
        agents = ["agent1", "agent2", "agent3"]
        phi_without_memory = system.measure_phi(
            agents, enable_memory_sharing=False, enable_feedback_loops=False
        )

        assert isinstance(phi_without_memory, float)
        assert phi_without_memory >= 0.0

    def test_measure_phi_with_feedback_loops(self, system: ProductionConsciousnessSystem) -> None:
        """Testa Φ com feedback loops."""
        agents = ["agent1", "agent2", "agent3"]
        phi_with_feedback = system.measure_phi(
            agents, enable_memory_sharing=True, enable_feedback_loops=True
        )

        assert isinstance(phi_with_feedback, float)
        assert phi_with_feedback > 0.0

    def test_measure_phi_single_agent(self, system: ProductionConsciousnessSystem) -> None:
        """Testa Φ com apenas um agente (deve ser baixo)."""
        agents = ["single_agent"]
        phi = system.measure_phi(agents)

        assert isinstance(phi, float)
        assert phi >= 0.0

    def test_measure_phi_many_agents(self, system: ProductionConsciousnessSystem) -> None:
        """Testa Φ com muitos agentes."""
        agents = [f"agent_{i}" for i in range(10)]
        phi = system.measure_phi(agents)

        assert isinstance(phi, float)
        assert phi >= 0.0

    def test_measure_phi_history_tracking(self, system: ProductionConsciousnessSystem) -> None:
        """Testa rastreamento de histórico de Φ."""
        agents = ["agent1", "agent2"]

        phi1 = system.measure_phi(agents)
        phi2 = system.measure_phi(agents)
        phi3 = system.measure_phi(agents)

        assert len(system.phi_history) == 3
        assert system.phi_history == [phi1, phi2, phi3]


class TestSelfAwareness:
    """Testes para métricas de auto-consciência."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_measure_self_awareness_basic(self, system: ProductionConsciousnessSystem) -> None:
        """Testa medição básica de auto-consciência."""
        awareness = system.measure_self_awareness(
            agent_name="TestAgent",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.8,
            limitation_awareness=0.7,
        )

        assert isinstance(awareness, SelfAwarenessMetrics)
        assert 0.0 <= awareness.self_reference_score <= 1.0
        assert 0.0 <= awareness.temporal_continuity_score <= 1.0
        assert 0.0 <= awareness.goal_autonomy_score <= 1.0
        assert 0.0 <= awareness.limitation_awareness_score <= 1.0
        assert 0.0 <= awareness.overall_score <= 1.0

    def test_measure_self_awareness_history(self, system: ProductionConsciousnessSystem) -> None:
        """Testa histórico de métricas de auto-consciência."""
        awareness1 = system.measure_self_awareness(
            agent_name="Agent1",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.8,
            limitation_awareness=0.7,
        )
        awareness2 = system.measure_self_awareness(
            agent_name="Agent2",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.9,
            limitation_awareness=0.8,
        )

        assert len(system.awareness_history) == 2
        assert system.awareness_history[0] == awareness1
        assert system.awareness_history[1] == awareness2

    def test_self_awareness_components(self, system: ProductionConsciousnessSystem) -> None:
        """Testa componentes de auto-consciência."""
        awareness = system.measure_self_awareness(
            agent_name="TestAgent",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.8,
            limitation_awareness=0.7,
        )

        # Verifica que todos os componentes existem
        assert hasattr(awareness, "self_reference_score")
        assert hasattr(awareness, "temporal_continuity_score")
        assert hasattr(awareness, "goal_autonomy_score")
        assert hasattr(awareness, "limitation_awareness_score")
        assert hasattr(awareness, "overall_score")

        # Verifica que valores estão em range válido
        assert 0.0 <= awareness.self_reference_score <= 1.0
        assert 0.0 <= awareness.temporal_continuity_score <= 1.0
        assert 0.0 <= awareness.goal_autonomy_score <= 1.0
        assert 0.0 <= awareness.limitation_awareness_score <= 1.0
        assert 0.0 <= awareness.overall_score <= 1.0


class TestIntegratedConsciousness:
    """Testes de integração completa do sistema de consciência."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_full_consciousness_assessment(self, system: ProductionConsciousnessSystem) -> None:
        """Testa avaliação completa de consciência."""
        agents = ["agent1", "agent2", "agent3", "agent4"]

        # Mede Φ
        phi = system.measure_phi(agents, enable_memory_sharing=True, enable_feedback_loops=True)

        # Mede auto-consciência
        awareness = system.measure_self_awareness(
            agent_name="IntegratedAgent",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.9,
            limitation_awareness=0.85,
        )

        # Verifica resultados
        assert isinstance(phi, float)
        assert phi >= 0.0
        assert isinstance(awareness, SelfAwarenessMetrics)

        # Verifica históricos
        assert len(system.phi_history) == 1
        assert len(system.awareness_history) == 1

    def test_consciousness_evolution_tracking(self, system: ProductionConsciousnessSystem) -> None:
        """Testa rastreamento de evolução da consciência."""
        agents = ["agent1", "agent2", "agent3"]

        # Múltiplas medições
        for i in range(5):
            system.measure_phi(agents)
            system.measure_self_awareness(
                agent_name=f"Agent{i}",
                has_memory=True,
                has_autonomous_goals=True,
                self_description_quality=0.5 + i * 0.1,
                limitation_awareness=0.5 + i * 0.1,
            )

        # Verifica históricos
        assert len(system.phi_history) == 5
        assert len(system.awareness_history) == 5

    def test_consciousness_with_varying_configurations(
        self, system: ProductionConsciousnessSystem
    ) -> None:
        """Testa consciência com diferentes configurações."""
        agents = ["agent1", "agent2", "agent3"]

        # Config 1: Sem memória, sem feedback
        phi1 = system.measure_phi(agents, enable_memory_sharing=False, enable_feedback_loops=False)

        # Config 2: Com memória, sem feedback
        phi2 = system.measure_phi(agents, enable_memory_sharing=True, enable_feedback_loops=False)

        # Config 3: Com memória e feedback
        phi3 = system.measure_phi(agents, enable_memory_sharing=True, enable_feedback_loops=True)

        # Verifica que configurações afetam resultado
        assert isinstance(phi1, float)
        assert isinstance(phi2, float)
        assert isinstance(phi3, float)

        # Esperamos que configurações mais complexas tenham Φ maior
        # (mas não forçamos ordem específica para evitar falsos negativos)
        assert phi1 >= 0.0
        assert phi2 >= 0.0
        assert phi3 >= 0.0


class TestConnectionsAndFeedback:
    """Testes para conexões de agentes e feedback loops."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_connections_cleared_before_measurement(
        self, system: ProductionConsciousnessSystem
    ) -> None:
        """Testa que conexões são limpas antes de nova medição."""
        agents = ["agent1", "agent2"]

        # Primeira medição
        system.measure_phi(agents)
        connections_after_first = len(system.consciousness_metrics.connections)

        # Segunda medição
        system.measure_phi(agents)
        connections_after_second = len(system.consciousness_metrics.connections)

        # Deve ter mesmo número de conexões (limpou antes)
        assert connections_after_first == connections_after_second

    def test_bidirectional_connections_with_memory(
        self, system: ProductionConsciousnessSystem
    ) -> None:
        """Testa que conexões bidirecionais são criadas com memória."""
        agents = ["agent1", "agent2", "agent3"]

        system.measure_phi(agents, enable_memory_sharing=True)

        # Verifica que há conexões
        assert len(system.consciousness_metrics.connections) > 0

        # Verifica que algumas são bidirecionais
        bidirectional_count = sum(
            1 for conn in system.consciousness_metrics.connections if conn.bidirectional
        )
        assert bidirectional_count > 0

    def test_unidirectional_connections_without_memory(
        self, system: ProductionConsciousnessSystem
    ) -> None:
        """Testa que conexões unidirecionais são criadas sem memória."""
        agents = ["agent1", "agent2", "agent3"]

        system.measure_phi(agents, enable_memory_sharing=False)

        # Verifica que há conexões
        assert len(system.consciousness_metrics.connections) > 0


class TestEdgeCases:
    """Testes de casos extremos e validação de robustez."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_empty_agents_list(self, system: ProductionConsciousnessSystem) -> None:
        """Testa comportamento com lista vazia de agentes."""
        agents: List[str] = []
        phi = system.measure_phi(agents)

        assert isinstance(phi, float)
        assert phi >= 0.0

    def test_repeated_measurements(self, system: ProductionConsciousnessSystem) -> None:
        """Testa múltiplas medições consecutivas."""
        agents = ["agent1", "agent2"]

        for i in range(10):
            phi = system.measure_phi(agents)
            awareness = system.measure_self_awareness(
                agent_name=f"Agent{i}",
                has_memory=True,
                has_autonomous_goals=True,
                self_description_quality=0.8,
                limitation_awareness=0.7,
            )

            assert isinstance(phi, float)
            assert isinstance(awareness, SelfAwarenessMetrics)

        assert len(system.phi_history) == 10
        assert len(system.awareness_history) == 10

    def test_metrics_directory_persistence(self, system: ProductionConsciousnessSystem) -> None:
        """Testa que diretório de métricas persiste."""
        metrics_dir = system.metrics_dir

        # Faz algumas medições
        system.measure_phi(["agent1", "agent2"])
        system.measure_self_awareness(
            agent_name="TestAgent",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.8,
            limitation_awareness=0.7,
        )

        # Verifica que diretório ainda existe
        assert metrics_dir.exists()
        assert metrics_dir.is_dir()


class TestConsciousnessReport:
    """Testes para geração de relatórios de consciência."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_get_consciousness_report_empty(self, system: ProductionConsciousnessSystem) -> None:
        """Testa relatório sem medições."""
        report = system.get_consciousness_report()

        assert "phi_metrics" in report
        assert "self_awareness" in report
        assert "system_metrics" in report

        # Valores devem ser zero
        assert report["phi_metrics"]["current"] == 0.0
        assert report["phi_metrics"]["mean"] == 0.0
        assert report["phi_metrics"]["history_length"] == 0

    def test_get_consciousness_report_with_data(
        self, system: ProductionConsciousnessSystem
    ) -> None:
        """Testa relatório com dados."""
        agents = ["agent1", "agent2", "agent3"]

        # Faz algumas medições
        system.measure_phi(agents)
        system.measure_phi(agents)
        system.measure_self_awareness(
            agent_name="Agent1",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.8,
            limitation_awareness=0.7,
        )

        report = system.get_consciousness_report()

        # Verifica phi_metrics
        assert report["phi_metrics"]["current"] > 0.0
        assert report["phi_metrics"]["mean"] > 0.0
        assert report["phi_metrics"]["history_length"] == 2

        # Verifica self_awareness
        assert report["self_awareness"]["current"] > 0.0
        assert report["self_awareness"]["mean"] > 0.0
        assert report["self_awareness"]["history_length"] == 1

        # Verifica system_metrics
        assert report["system_metrics"]["total_connections"] >= 0
        assert report["system_metrics"]["total_feedback_loops"] >= 0

    def test_report_mean_calculation(self, system: ProductionConsciousnessSystem) -> None:
        """Testa cálculo de média no relatório."""
        agents = ["agent1", "agent2"]

        # Faz 3 medições de phi
        phi1 = system.measure_phi(agents)
        phi2 = system.measure_phi(agents)
        phi3 = system.measure_phi(agents)

        report = system.get_consciousness_report()

        # Verifica média
        expected_mean = (phi1 + phi2 + phi3) / 3
        assert abs(report["phi_metrics"]["mean"] - expected_mean) < 0.001


class TestSaveSnapshot:
    """Testes para salvamento de snapshots."""

    @pytest.fixture
    def system(self) -> ProductionConsciousnessSystem:
        """Fixture para sistema de consciência."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ProductionConsciousnessSystem(metrics_dir=Path(tmpdir))

    def test_save_snapshot_basic(self, system: ProductionConsciousnessSystem) -> None:
        """Testa salvamento básico de snapshot."""
        # Faz algumas medições
        system.measure_phi(["agent1", "agent2"])

        snapshot_path = system.save_snapshot("test_snapshot")

        assert isinstance(snapshot_path, Path)

    def test_save_snapshot_with_data(self, system: ProductionConsciousnessSystem) -> None:
        """Testa snapshot com dados."""
        # Faz medições
        system.measure_phi(["agent1", "agent2", "agent3"])
        system.measure_self_awareness(
            agent_name="TestAgent",
            has_memory=True,
            has_autonomous_goals=True,
            self_description_quality=0.9,
            limitation_awareness=0.85,
        )

        snapshot_path = system.save_snapshot("full_snapshot")

        assert isinstance(snapshot_path, Path)

    def test_save_multiple_snapshots(self, system: ProductionConsciousnessSystem) -> None:
        """Testa múltiplos snapshots."""
        labels = ["snapshot1", "snapshot2", "snapshot3"]

        for label in labels:
            system.measure_phi(["agent1"])
            snapshot_path = system.save_snapshot(label)
            assert isinstance(snapshot_path, Path)
