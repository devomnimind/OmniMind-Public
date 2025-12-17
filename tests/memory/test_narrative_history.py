"""Tests for Narrative History - Lacanian Memory"""

from __future__ import annotations

from memory.narrative_history import NarrativeHistory


class TestNarrativeHistory:
    """Test Narrative History (Lacanian)"""

    def test_init(self):
        """Test initialization"""
        history = NarrativeHistory()
        assert history is not None
        assert len(history.retroactive_significations) == 0

    def test_inscribe_event(self):
        """Test inscribing an event without meaning"""
        history = NarrativeHistory()

        event = {
            "task": "test_task",
            "action": "test_action",
            "result": "test_result",
        }

        event_id = history.inscribe_event(event, without_meaning=True)

        assert event_id is not None
        assert event_id in history.retroactive_significations

    def test_retroactive_signification(self):
        """Test retroactive signification (Nachträglichkeit)"""
        history = NarrativeHistory()

        event = {"task": "test", "action": "test", "result": "test"}
        event_id = history.inscribe_event(event, without_meaning=True)

        history.retroactive_signification(
            event_id, "This event now means understanding", {"trigger": "new_event"}
        )

        signification = history.retroactive_significations[event_id]
        assert signification["awaiting"] is False
        assert "retroactive_meaning" in signification

    def test_construct_narrative(self):
        """Test narrative construction"""
        history = NarrativeHistory()

        # Inscribe some events
        event1 = {"task": "learn", "action": "read", "result": "understood"}
        event2 = {"task": "apply", "action": "implement", "result": "success"}

        history.inscribe_event(event1, without_meaning=True)
        history.inscribe_event(event2, without_meaning=True)

        # Construct narrative
        narrative = history.construct_narrative("learning process")

        assert "narrative" in narrative
        assert "coherence" in narrative


class TestNarrativeHistoryHybridTopological:
    """Testes de integração entre NarrativeHistory e HybridTopologicalEngine."""

    def test_narrative_history_with_topological_metrics(self):
        """Testa que NarrativeHistory pode ser usado com métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar NarrativeHistory
        history = NarrativeHistory()

        # Inscrição de eventos
        event1 = {"task": "learn", "action": "read", "result": "understood"}
        event2 = {"task": "apply", "action": "implement", "result": "success"}

        history.inscribe_event(event1, without_meaning=True)
        history.inscribe_event(event2, without_meaning=True)

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

        # Construir narrativa
        narrative = history.construct_narrative("learning process")

        # Verificar que ambas funcionam
        assert "narrative" in narrative
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # NarrativeHistory: reconstrução retroativa (Lacan)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa
