"""
Testes para HybridRetrievalSystem.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock, patch

from src.memory.hybrid_retrieval import HybridRetrievalSystem, RetrievalResult


class TestHybridRetrievalSystem:
    """Testes para HybridRetrievalSystem."""

    def test_init(self):
        """Testa inicialização."""
        retrieval = HybridRetrievalSystem(
            qdrant_url="http://localhost:6333",
            collection_name="test_collection",
        )
        assert retrieval.collection_name == "test_collection"
        assert retrieval.top_k_dense == 20
        assert retrieval.top_k_sparse == 20
        assert retrieval.top_k_final == 5

    def test_tokenize(self):
        """Testa tokenização."""
        retrieval = HybridRetrievalSystem(collection_name="test")
        tokens = retrieval._tokenize("Hello world! This is a test.")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "!" not in tokens  # Pontuação removida

    def test_build_bm25_index(self):
        """Testa construção de índice BM25."""
        retrieval = HybridRetrievalSystem(collection_name="test")
        documents = [
            {"id": "doc1", "content": "hello world"},
            {"id": "doc2", "content": "world test"},
        ]
        index = retrieval._build_bm25_index(documents)
        assert "doc_freqs" in index
        assert "doc_lengths" in index
        assert "term_doc_freq" in index
        assert index["total_docs"] == 2

    def test_bm25_score(self):
        """Testa cálculo de score BM25."""
        retrieval = HybridRetrievalSystem(collection_name="test")
        documents = [
            {"id": "doc1", "content": "hello world"},
            {"id": "doc2", "content": "world test"},
        ]
        index = retrieval._build_bm25_index(documents)
        score = retrieval._bm25_score("hello", "doc1", index)
        assert score > 0

    def test_sparse_search(self):
        """Testa busca esparsa."""
        retrieval = HybridRetrievalSystem(collection_name="test")
        documents = [
            {"id": "doc1", "content": "hello world", "source": "test"},
            {"id": "doc2", "content": "world test", "source": "test"},
        ]
        results = retrieval._sparse_search("hello", documents, top_k=1)
        assert len(results) > 0
        assert results[0].retrieval_method == "sparse"
        assert "hello" in results[0].content.lower()

    @patch("src.memory.hybrid_retrieval.QdrantClient")
    def test_dense_search(self, mock_qdrant_client):
        """Testa busca densa."""
        # Mock Qdrant
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Mock search result
        mock_hit = MagicMock()
        mock_hit.score = 0.95
        mock_hit.payload = {"content": "test content", "source": "test"}
        mock_client.search.return_value = [mock_hit]

        retrieval = HybridRetrievalSystem(collection_name="test")
        retrieval.client = mock_client

        results = retrieval._dense_search("test query")
        assert len(results) > 0
        assert results[0].retrieval_method == "dense"
        assert results[0].score == 0.95

    def test_rerank_without_model(self):
        """Testa reranking sem modelo (deve retornar top-K ordenado)."""
        retrieval = HybridRetrievalSystem(collection_name="test")
        retrieval.reranker_model = None

        results = [
            RetrievalResult("doc1", 0.5, "test", {}, "dense"),
            RetrievalResult("doc2", 0.9, "test", {}, "dense"),
            RetrievalResult("doc3", 0.3, "test", {}, "dense"),
        ]

        reranked = retrieval._rerank("query", results, top_k=2)
        assert len(reranked) == 2
        assert reranked[0].score >= reranked[1].score  # Ordenado

    def test_retrieve_hybrid(self):
        """Testa retrieval híbrido completo."""
        retrieval = HybridRetrievalSystem(collection_name="test")

        # Mock dense search
        with patch.object(retrieval, "_dense_search") as mock_dense:
            mock_dense.return_value = [
                RetrievalResult("content1", 0.8, "test", {}, "dense"),
            ]

            # Mock sparse search
            with patch.object(retrieval, "_sparse_search") as mock_sparse:
                mock_sparse.return_value = [
                    RetrievalResult("content2", 0.7, "test", {}, "sparse"),
                ]

                results = retrieval.retrieve("test query", top_k=5)
                assert len(results) > 0
