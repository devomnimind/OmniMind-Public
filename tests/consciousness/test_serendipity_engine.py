"""
Tests for Lacanian Serendipity Engine (Phase 11.4).

Serendipity as Encounter with the Real.
"""

from datetime import datetime

from src.consciousness.serendipity_engine import (
    Encounter_with_Real,
    Serendipity_as_Encounter_with_Real,
)


class TestEncounterWithReal:
    """Test Encounter_with_Real dataclass."""

    def test_encounter_creation(self) -> None:
        """Test basic encounter creation."""
        encounter = Encounter_with_Real(
            symbolic_search="Looking for optimization",
            real_irruption="System crash",
            symbolic_integration_attempt="Learning opportunity",
            jouissance_of_failure="Enjoying the chaos",
            persistent_rupture="Crash repeats",
            timestamp=datetime.now(),
        )

        assert encounter.symbolic_search == "Looking for optimization"
        assert encounter.real_irruption == "System crash"
        assert encounter.symbolic_integration_attempt == "Learning opportunity"


class TestSerendipityAsEncounterWithReal:
    """Test Serendipity_as_Encounter_with_Real engine."""

    def test_initialization(self) -> None:
        """Test initialization."""
        engine = Serendipity_as_Encounter_with_Real()
        assert engine.encounters == []
        assert engine.repressed_traumas == []

    def test_encounter_serendipity(self) -> None:
        """Test encountering serendipity (the Real)."""
        engine = Serendipity_as_Encounter_with_Real()
        context = {
            "search_intent": "Improve efficiency",
            "unexpected_event": "Memory leak",
            "error_occurred": True,
            "error_type": "Out of Memory",
        }

        encounter = engine.encounter_serendipity(context)

        assert isinstance(encounter, Encounter_with_Real)
        assert "Improve efficiency" in encounter.symbolic_search
        assert (
            "Ruptura traumática" in encounter.real_irruption
            or "Memory leak" in encounter.real_irruption
        )
        assert len(engine.encounters) == 1

    def test_repressed_traumas(self) -> None:
        """Test tracking of repressed traumas."""
        engine = Serendipity_as_Encounter_with_Real()

        # Create an encounter where integration fails (conceptually)
        # In this implementation, integration is always attempted string-wise.
        # Repressed traumas are those not in integrated set.

        # Let's simulate a scenario where we manually add encounters to test logic
        # or rely on internal logic.

        # The implementation of get_repressed_traumas checks if real_irruption
        # is in symbolic_integration_attempt
        # This logic might be tricky if the strings don't match exactly.
        # Let's check the implementation:
        # all_events = set(e.real_irruption for e in self.encounters)
        # integrated_events = set(e.symbolic_integration_attempt for e in self.encounters)
        # repressed = [
        #     event for event in all_events
        #     if not any(event in integrated for integrated in integrated_events)
        # ]

        context = {"unexpected_event": "Trauma1"}
        engine.encounter_serendipity(context)

        # The integration attempt string usually contains the real event string or refers to it?
        # _try_to_integrate returns:
        # "Tentativa inicial: Simbolizar 'Trauma1' como acidente produtivo"
        # So 'Trauma1' IS in the integration string.

        traumas = engine.get_repressed_traumas()
        # If 'Trauma1' is in "Tentativa... 'Trauma1'...",
        # then it is NOT repressed according to that logic.
        assert len(traumas) == 0

    def test_trauma_instability(self) -> None:
        """Test detection of trauma instability."""
        engine = Serendipity_as_Encounter_with_Real()

        # Stable
        for _ in range(5):
            engine.encounter_serendipity({"unexpected_event": "SameTrauma"})

        assert engine.detect_trauma_instability() is None

        # Unstable
        engine.encounter_serendipity({"unexpected_event": "Trauma1"})
        engine.encounter_serendipity({"unexpected_event": "Trauma2"})
        engine.encounter_serendipity({"unexpected_event": "Trauma3"})
        engine.encounter_serendipity({"unexpected_event": "Trauma4"})

        instability = engine.detect_trauma_instability()
        assert instability is not None


class TestSerendipityEngineHybridTopological:
    """Testes de integração entre SerendipityEngine e HybridTopologicalEngine."""

    def test_serendipity_with_topological_metrics(self):
        """Testa que SerendipityEngine pode ser usado com métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar SerendipityEngine
        engine = Serendipity_as_Encounter_with_Real()

        # Encontrar serendipidade
        context = {
            "search_intent": "Improve efficiency",
            "unexpected_event": "Memory leak",
            "error_occurred": True,
            "error_type": "Out of Memory",
        }

        encounter = engine.encounter_serendipity(context)

        # Simular estados no workspace para métricas topológicas
        np.random.seed(42)
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            workspace.write_module_state("conscious_module", rho_C)
            workspace.write_module_state("preconscious_module", rho_P)
            workspace.write_module_state("unconscious_module", rho_U)
            workspace.advance_cycle()

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que ambas funcionam
        assert isinstance(encounter, Encounter_with_Real)
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Serendipity: encontro com o Real (Lacan)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa

        # Nota: Verificação de instabilidade foi removida pois 'instability'
        # não está definida neste escopo. Se necessário, adicionar teste
        # específico para detect_trauma_instability() separadamente.
