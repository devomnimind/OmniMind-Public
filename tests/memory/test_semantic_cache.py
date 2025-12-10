"""
Testes para SemanticCacheLayer.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock, patch

import pytest

from src.memory.semantic_cache import SemanticCacheLayer


class TestSemanticCacheLayer:
    """Testes para SemanticCacheLayer."""

    @patch("src.memory.semantic_cache.SentenceTransformer")
    def test_init(self, mock_sentence_transformer):
        """Testa inicialização."""
        # Mock do modelo para evitar problemas de meta tensor
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        cache = SemanticCacheLayer(
            qdrant_url="http://localhost:6333",
            collection_name="test_cache",
            similarity_threshold=0.95,
        )
        assert cache.collection_name == "test_cache"
        assert cache.similarity_threshold == 0.95
        assert cache.stats["total_queries"] == 0

    @patch("src.memory.semantic_cache.SentenceTransformer")
    def test_generate_embedding(self, mock_sentence_transformer):
        """Testa geração de embedding."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = [0.1] * 384  # Mock embedding
        mock_sentence_transformer.return_value = mock_model

        cache = SemanticCacheLayer(collection_name="test_cache")
        embedding = cache._generate_embedding("test task")
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        assert all(isinstance(x, float) for x in embedding)

    @patch("src.memory.semantic_cache.SentenceTransformer")
    def test_generate_id(self, mock_sentence_transformer):
        """Testa geração de ID."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        cache = SemanticCacheLayer(collection_name="test_cache")
        id1 = cache._generate_id("task1", "agent1")
        id2 = cache._generate_id("task1", "agent1")
        id3 = cache._generate_id("task2", "agent1")

        # Mesma tarefa e agente = mesmo ID
        assert id1 == id2
        # Tarefa diferente = ID diferente (provavelmente)
        assert id1 != id3

    @patch("src.memory.semantic_cache.SentenceTransformer")
    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_or_compute_cache_miss(self, mock_qdrant_client, mock_sentence_transformer):
        """Testa get_or_compute com cache miss."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = [0.1] * 384
        mock_sentence_transformer.return_value = mock_model

        # Mock Qdrant
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Mock search retorna vazio (cache miss)
        mock_client.search.return_value = []
        mock_client.get_collection.side_effect = Exception("Not found")

        cache = SemanticCacheLayer(collection_name="test_cache")
        cache.client = mock_client

        # Função que computa resposta
        def compute_response():
            return "computed response"

        # Primeira chamada (cache miss)
        result = cache.get_or_compute("test task", compute_response, "test_agent")

        assert result == "computed response"
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0
        # Deve ter chamado upsert para armazenar
        assert mock_client.upsert.called

    @patch("src.memory.semantic_cache.SentenceTransformer")
    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_or_compute_cache_hit(self, mock_qdrant_client, mock_sentence_transformer):
        """Testa get_or_compute com cache hit."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = [0.1] * 384
        mock_sentence_transformer.return_value = mock_model

        # Mock Qdrant
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Mock search retorna resultado (cache hit)
        mock_result = MagicMock()
        mock_result.score = 0.98  # Acima do threshold
        mock_result.payload = {
            "response": "cached response",
            "agent_name": "test_agent",
            "cached_at": "2025-12-06T00:00:00",
        }
        mock_client.search.return_value = [mock_result]
        mock_client.get_collection.side_effect = Exception("Not found")

        cache = SemanticCacheLayer(collection_name="test_cache", similarity_threshold=0.95)
        cache.client = mock_client

        # Função que computa resposta (não deve ser chamada)
        compute_called = False

        def compute_response():
            nonlocal compute_called
            compute_called = True
            return "computed response"

        # Chamada (cache hit)
        result = cache.get_or_compute("test task", compute_response, "test_agent")

        assert result == "cached response"
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 0
        assert not compute_called  # Não deve ter computado


class TestSemanticCacheHybridTopological:
    """Testes de integração entre SemanticCacheLayer e HybridTopologicalEngine."""

    @patch("src.memory.semantic_cache.SentenceTransformer")
    def test_semantic_cache_with_topological_metrics(self, mock_sentence_transformer):
        """Testa que SemanticCacheLayer pode ser usado com métricas topológicas."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar SemanticCacheLayer
        cache = SemanticCacheLayer(collection_name="test_cache")

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
        assert cache.collection_name == "test_cache"
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # SemanticCache: cache semântico (Qdrant)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa

    @patch("src.memory.semantic_cache.SentenceTransformer")
    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_or_compute_force_compute(self, mock_qdrant_client, mock_sentence_transformer):
        """Testa get_or_compute com force_compute=True."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = [0.1] * 384
        mock_sentence_transformer.return_value = mock_model

        # Mock Qdrant
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_client.get_collection.side_effect = Exception("Not found")

        cache = SemanticCacheLayer(collection_name="test_cache")
        cache.client = mock_client

        compute_called = False

        def compute_response():
            nonlocal compute_called
            compute_called = True
            return "forced response"

        # Chamada com force_compute
        result = cache.get_or_compute(
            "test task", compute_response, "test_agent", force_compute=True
        )

        assert result == "forced response"
        assert compute_called
        assert cache.stats["misses"] == 1

    @patch("src.memory.semantic_cache.SentenceTransformer")
    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_effectiveness(self, mock_qdrant_client, mock_sentence_transformer):
        """Testa get_effectiveness."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        # Mock Qdrant
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 10
        mock_client.get_collection.return_value = mock_collection_info
        mock_client.get_collection.side_effect = Exception("Not found")

        cache = SemanticCacheLayer(collection_name="test_cache")
        cache.client = mock_client
        cache.stats["hits"] = 3
        cache.stats["misses"] = 7
        cache.stats["total_queries"] = 10

        effectiveness = cache.get_effectiveness()

        assert effectiveness["hits"] == 3
        assert effectiveness["misses"] == 7
        assert effectiveness["total_queries"] == 10
        assert effectiveness["hit_rate"] == 0.3

    @patch("src.memory.semantic_cache.SentenceTransformer")
    @patch("src.memory.semantic_cache.QdrantClient")
    def test_clear_cache(self, mock_qdrant_client, mock_sentence_transformer):
        """Testa clear_cache."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        # Mock Qdrant
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_client.get_collection.side_effect = Exception("Not found")

        cache = SemanticCacheLayer(collection_name="test_cache")
        cache.client = mock_client
        cache.stats["cache_size"] = 5

        removed = cache.clear_cache()

        assert removed == 5
        assert cache.stats["cache_size"] == 0
        # Deve ter deletado e recriado coleção
        assert mock_client.delete_collection.called
