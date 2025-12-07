"""
Testes para SemanticCacheLayer.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock, patch

from src.memory.semantic_cache import SemanticCacheLayer


class TestSemanticCacheLayer:
    """Testes para SemanticCacheLayer."""

    def test_init(self):
        """Testa inicialização."""
        cache = SemanticCacheLayer(
            qdrant_url="http://localhost:6333",
            collection_name="test_cache",
            similarity_threshold=0.95,
        )
        assert cache.collection_name == "test_cache"
        assert cache.similarity_threshold == 0.95
        assert cache.stats["total_queries"] == 0

    def test_generate_embedding(self):
        """Testa geração de embedding."""
        cache = SemanticCacheLayer(collection_name="test_cache")
        embedding = cache._generate_embedding("test task")
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        assert all(isinstance(x, float) for x in embedding)

    def test_generate_id(self):
        """Testa geração de ID."""
        cache = SemanticCacheLayer(collection_name="test_cache")
        id1 = cache._generate_id("task1", "agent1")
        id2 = cache._generate_id("task1", "agent1")
        id3 = cache._generate_id("task2", "agent1")

        # Mesma tarefa e agente = mesmo ID
        assert id1 == id2
        # Tarefa diferente = ID diferente (provavelmente)
        assert id1 != id3

    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_or_compute_cache_miss(self, mock_qdrant_client):
        """Testa get_or_compute com cache miss."""
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

    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_or_compute_cache_hit(self, mock_qdrant_client):
        """Testa get_or_compute com cache hit."""
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

    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_or_compute_force_compute(self, mock_qdrant_client):
        """Testa get_or_compute com force_compute=True."""
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

    @patch("src.memory.semantic_cache.QdrantClient")
    def test_get_effectiveness(self, mock_qdrant_client):
        """Testa get_effectiveness."""
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

    @patch("src.memory.semantic_cache.QdrantClient")
    def test_clear_cache(self, mock_qdrant_client):
        """Testa clear_cache."""
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
