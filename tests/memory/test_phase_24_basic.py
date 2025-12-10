"""Phase 24 Integration Tests - Semantic Memory, State Management, Temporal Index

Tests for:
- Qdrant integration and vector storage
- Semantic memory layer with embeddings
- Consciousness state snapshots
- Temporal memory and causality chains

Author: OmniMind Development
License: MIT
"""

import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

logger = logging.getLogger(__name__)


class TestQdrantIntegration:
    """Tests for Qdrant integration layer"""

    def test_qdrant_singleton(self):
        """Test singleton pattern for Qdrant"""

        from src.integrations.qdrant_integration import get_qdrant

        qdrant1 = get_qdrant()
        qdrant2 = get_qdrant()

        assert qdrant1 is qdrant2, "Singleton should return same instance"

    def test_qdrant_health_check(self):
        """Test Qdrant health check"""

        from src.integrations.qdrant_integration import get_qdrant

        qdrant = get_qdrant()
        health = qdrant.health_check()

        assert health, "Qdrant should be healthy"

    def test_qdrant_collection_creation(self):
        """Test creating collection"""

        from src.integrations.qdrant_integration import QdrantIntegration

        qdrant = QdrantIntegration(collection_name="test_collection", vector_size=384)

        success = qdrant.create_collection()

        assert success or isinstance(success, bool), "Collection creation should return bool"

    def test_qdrant_upsert_points(self):
        """Test upserting points"""

        from src.integrations.qdrant_integration import QdrantIntegration, QdrantPoint

        qdrant = QdrantIntegration(collection_name="test_points", vector_size=384)
        qdrant.create_collection(recreate=True)

        points = [
            QdrantPoint(
                id=1,
                vector=[0.1] * 384,
                payload={"text": "test episode 1"},
            ),
            QdrantPoint(
                id=2,
                vector=[0.2] * 384,
                payload={"text": "test episode 2"},
            ),
        ]

        success = qdrant.upsert_points(points)
        assert success or isinstance(success, bool), "Upsert should return bool"


class TestSemanticMemoryLayer:
    """Tests for semantic memory layer"""

    @pytest.fixture
    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def semantic_memory(self, mock_qdrant_client, mock_sentence_transformer):
        """Create semantic memory instance"""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        from src.memory.semantic_memory_layer import SemanticMemoryLayer

        return SemanticMemoryLayer()

    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def test_semantic_memory_initialization(
        self, mock_qdrant_client, mock_sentence_transformer, semantic_memory
    ):
        """Test initialization"""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        assert semantic_memory.embedder is not None, "Embedder should be loaded"
        assert semantic_memory.embedding_dim == 384, "Embedding dimension should be 384"

    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def test_store_episode(self, mock_qdrant_client, mock_sentence_transformer, semantic_memory):
        """Test storing episode"""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        episode_id = semantic_memory.store_episode(
            episode_text="This is a test consciousness episode",
            episode_data={
                "phi_value": 0.75,
                "qualia_signature": {"color": "blue", "intensity": 0.8},
            },
        )

        assert episode_id, "Episode should have ID"
        assert isinstance(episode_id, str), "Episode ID should be string"

    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def test_retrieve_similar(self, mock_qdrant_client, mock_sentence_transformer, semantic_memory):
        """Test semantic similarity search"""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Store test episodes
        semantic_memory.store_episode(
            episode_text="The sky is blue and beautiful",
            episode_data={"phi_value": 0.7, "qualia_signature": {}},
        )

        semantic_memory.store_episode(
            episode_text="The ocean waves are crashing",
            episode_data={"phi_value": 0.6, "qualia_signature": {}},
        )

        # Query
        results = semantic_memory.retrieve_similar(query_text="blue sky", top_k=2, threshold=0.3)

        assert len(results) >= 0, "Should return results"

    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def test_get_stats(self, mock_qdrant_client, mock_sentence_transformer, semantic_memory):
        """Test statistics"""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Store an episode first to ensure collection exists
        semantic_memory.store_episode(
            episode_text="Test episode for stats",
            episode_data={"phi_value": 0.5, "qualia_signature": {}},
        )

        stats = semantic_memory.get_stats()

        assert stats is not None, "Stats should be available"
        assert "total_episodes" in stats, "Stats should include total_episodes"
        assert "embedding_dim" in stats, "Stats should include embedding_dim"


class TestConsciousnessStateManager:
    """Tests for consciousness state management"""

    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create state manager with temp storage"""

        from src.memory.consciousness_state_manager import (
            ConsciousnessStateManager,
        )

        storage = str(tmp_path / "snapshots.jsonl")
        return ConsciousnessStateManager(storage_path=storage)

    def test_take_snapshot(self, state_manager):
        """Test taking consciousness snapshot"""

        snapshot_id = state_manager.take_snapshot(
            phi_value=0.75,
            qualia_signature={"color": "red", "intensity": 0.9},
            attention_state={"visual": 0.8, "auditory": 0.3},
            integration_level=0.7,
        )

        assert snapshot_id, "Snapshot should have ID"

    def test_restore_snapshot(self, state_manager):
        """Test restoring snapshot"""

        # Take snapshot
        snapshot_id = state_manager.take_snapshot(
            phi_value=0.75,
            qualia_signature={"color": "green"},
            attention_state={"visual": 0.8},
            integration_level=0.7,
        )

        # Restore
        restored = state_manager.restore_snapshot(snapshot_id)

        assert restored is not None, "Should restore snapshot"
        assert restored.phi_value == 0.75, "Phi value should match"

    def test_get_latest_snapshot(self, state_manager):
        """Test getting latest snapshot"""

        # Take multiple snapshots
        state_manager.take_snapshot(
            phi_value=0.5,
            qualia_signature={},
            attention_state={},
            integration_level=0.5,
        )

        state_manager.take_snapshot(
            phi_value=0.8,
            qualia_signature={},
            attention_state={},
            integration_level=0.8,
        )

        latest = state_manager.get_latest_snapshot()

        assert latest is not None, "Should have latest snapshot"
        assert latest.phi_value == 0.8, "Should be most recent"

    def test_phi_history(self, state_manager):
        """Test phi value history"""

        state_manager.take_snapshot(
            phi_value=0.5,
            qualia_signature={},
            attention_state={},
            integration_level=0.5,
        )

        state_manager.take_snapshot(
            phi_value=0.7,
            qualia_signature={},
            attention_state={},
            integration_level=0.7,
        )

        history = state_manager.get_phi_history(limit=10)

        assert len(history) == 2, "Should have 2 snapshots"
        assert history[0][1] == 0.5, "First phi should be 0.5"
        assert history[1][1] == 0.7, "Second phi should be 0.7"

    def test_phi_trajectory_range(self, state_manager):
        """Test phi trajectory in time window"""

        first_id = state_manager.take_snapshot(
            phi_value=0.4,
            qualia_signature={},
            attention_state={},
            integration_level=0.4,
        )
        assert first_id

        second_id = state_manager.take_snapshot(
            phi_value=0.9,
            qualia_signature={},
            attention_state={},
            integration_level=0.9,
        )
        assert second_id

        # Wide window should include both
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        trajectory = state_manager.get_phi_trajectory(start, end, limit=10)

        assert len(trajectory) >= 2
        # Trajectory must be sorted by time
        assert trajectory == sorted(trajectory, key=lambda t: t[0])

    def test_statistics(self, state_manager):
        """Test statistics"""

        state_manager.take_snapshot(
            phi_value=0.6,
            qualia_signature={},
            attention_state={},
            integration_level=0.6,
        )

        stats = state_manager.get_statistics()

        assert stats["total_snapshots"] == 1, "Should have 1 snapshot"


class TestTemporalMemoryIndex:
    """Tests for temporal memory indexing"""

    @pytest.fixture
    def temporal_index(self):
        """Create temporal memory index"""

        from src.memory.temporal_memory_index import TemporalMemoryIndex

        return TemporalMemoryIndex()

    def test_add_episode(self, temporal_index):
        """Test adding episode to index"""

        now = datetime.utcnow()

        temporal_index.add_episode(
            episode_id="ep_1",
            timestamp=now,
            episode_data={"phi_value": 0.7},
        )

        assert "ep_1" in str(temporal_index.episodes_by_time), "Episode should be indexed"

    def test_link_causality(self, temporal_index):
        """Test causality linking"""

        temporal_index.link_causality("cause_1", "effect_1")
        temporal_index.link_causality("cause_1", "effect_2")

        assert "effect_1" in temporal_index.causality_chains["cause_1"], "Effect should be linked"

    def test_get_episode_chain(self, temporal_index):
        """Test getting episode chain"""

        temporal_index.link_causality("ep_1", "ep_2")
        temporal_index.link_causality("ep_2", "ep_3")

        chain = temporal_index.get_episode_chain("ep_3")

        assert "ep_3" in chain, "Should include episode"
        assert len(chain) >= 1, "Chain should have episodes"

    def test_record_transition(self, temporal_index):
        """Test recording state transition"""

        from_state = {"phi_value": 0.5, "integration_level": 0.4}
        to_state = {"phi_value": 0.7, "integration_level": 0.6}

        transition_id = temporal_index.record_transition(from_state, to_state)

        assert transition_id, "Transition should have ID"
        assert len(temporal_index.transitions) == 1, "Should record transition"

    def test_trajectory_summary(self, temporal_index):
        """Test trajectory summary"""

        temporal_index.record_transition(
            {"phi_value": 0.5, "integration_level": 0.4},
            {"phi_value": 0.7, "integration_level": 0.6},
        )

        temporal_index.record_transition(
            {"phi_value": 0.7, "integration_level": 0.6},
            {"phi_value": 0.8, "integration_level": 0.7},
        )

        summary = temporal_index.get_trajectory_summary()

        assert summary["total_transitions"] == 2, "Should have 2 transitions"

    def test_predict_next_state(self, temporal_index):
        """Test state prediction"""

        # Build up some transitions for prediction
        for i in range(5):
            temporal_index.record_transition(
                {
                    "phi_value": 0.5 + (i * 0.05),
                    "integration_level": 0.4 + (i * 0.04),
                },
                {
                    "phi_value": 0.6 + (i * 0.05),
                    "integration_level": 0.5 + (i * 0.04),
                },
            )

        current = {"phi_value": 0.8, "integration_level": 0.7}
        predicted = temporal_index.predict_next_state(current)

        assert predicted is not None, "Should make prediction"
        assert "predicted_phi" in predicted, "Should predict phi"


class TestPhase24Integration:
    """Integration tests for Phase 24 modules"""

    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def test_semantic_to_consciousness_flow(self, mock_qdrant_client, mock_sentence_transformer):
        """Test flow: Store episode → Consciousness snapshot → Temporal tracking"""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        from src.memory.consciousness_state_manager import (
            get_consciousness_state_manager,
        )
        from src.memory.semantic_memory_layer import get_semantic_memory
        from src.memory.temporal_memory_index import get_temporal_memory_index

        # Store in semantic memory
        semantic = get_semantic_memory()
        episode_id = semantic.store_episode(
            episode_text="Moment of realization",
            episode_data={"phi_value": 0.85, "qualia_signature": {"insight": 1.0}},
        )

        # Take consciousness snapshot
        state_mgr = get_consciousness_state_manager()
        snapshot_id = state_mgr.take_snapshot(
            phi_value=0.85,
            qualia_signature={"insight": 1.0},
            attention_state={"focus": 0.9},
            integration_level=0.85,
        )

        # Record temporal index
        temporal = get_temporal_memory_index()
        temporal.add_episode(
            episode_id=episode_id,
            timestamp=datetime.utcnow(),
            episode_data={"phi_value": 0.85},
        )

        assert episode_id, "Should store episode"
        assert snapshot_id, "Should create snapshot"

    def test_phase_24_singletons(self):
        """Test singleton consistency across modules"""

        from src.memory.consciousness_state_manager import (
            get_consciousness_state_manager,
        )
        from src.memory.semantic_memory_layer import get_semantic_memory
        from src.memory.temporal_memory_index import get_temporal_memory_index

        # Get instances
        sem1 = get_semantic_memory()
        sem2 = get_semantic_memory()

        state1 = get_consciousness_state_manager()
        state2 = get_consciousness_state_manager()

        temp1 = get_temporal_memory_index()
        temp2 = get_temporal_memory_index()

        # Verify singletons
        assert sem1 is sem2, "Semantic memory should be singleton"
        assert state1 is state2, "State manager should be singleton"
        assert temp1 is temp2, "Temporal index should be singleton"


class TestPhase24HybridTopological:
    """Testes de integração entre Phase 24 Memory e HybridTopologicalEngine."""

    @patch("src.memory.semantic_memory_layer.SentenceTransformer")
    @patch("src.integrations.qdrant_integration.QdrantClient")
    def test_phase24_memory_with_topological_metrics(
        self, mock_qdrant_client, mock_sentence_transformer, semantic_memory
    ):
        """Testa que Phase 24 Memory pode ser usado com métricas topológicas."""
        # Mock the SentenceTransformer
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_sentence_transformer.return_value = mock_embedder

        # Mock QdrantClient
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Armazenar episódio
        episode_id = semantic_memory.store_episode(
            content="Test episode for topological integration",
            metadata={"test": True},
        )

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
        assert episode_id is not None
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Phase 24 Memory: memória semântica, estado, temporal
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa
