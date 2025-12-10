"""
Testes para HybridRetrievalSystem.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock, patch

import pytest

from src.memory.hybrid_retrieval import HybridRetrievalSystem, RetrievalResult


class TestHybridRetrievalSystem:
    """Testes para HybridRetrievalSystem."""

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_init(self, mock_sentence_transformer):
        """Testa inicialização."""
        # Mock do modelo para evitar problemas de meta tensor
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        retrieval = HybridRetrievalSystem(
            qdrant_url="http://localhost:6333",
            collection_name="test_collection",
        )
        assert retrieval.collection_name == "test_collection"
        assert retrieval.top_k_dense == 20
        assert retrieval.top_k_sparse == 20
        assert retrieval.top_k_final == 5

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_tokenize(self, mock_sentence_transformer):
        """Testa tokenização."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        retrieval = HybridRetrievalSystem(collection_name="test")
        tokens = retrieval._tokenize("Hello world! This is a test.")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "!" not in tokens  # Pontuação removida

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_build_bm25_index(self, mock_sentence_transformer):
        """Testa construção de índice BM25."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

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

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_bm25_score(self, mock_sentence_transformer):
        """Testa cálculo de score BM25."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        retrieval = HybridRetrievalSystem(collection_name="test")
        documents = [
            {"id": "doc1", "content": "hello world"},
            {"id": "doc2", "content": "world test"},
        ]
        index = retrieval._build_bm25_index(documents)
        score = retrieval._bm25_score("hello", "doc1", index)
        assert score > 0

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_sparse_search(self, mock_sentence_transformer):
        """Testa busca esparsa."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

        retrieval = HybridRetrievalSystem(collection_name="test")
        documents = [
            {"id": "doc1", "content": "hello world", "source": "test"},
            {"id": "doc2", "content": "world test", "source": "test"},
        ]
        results = retrieval._sparse_search("hello", documents, top_k=1)
        assert len(results) > 0
        assert results[0].retrieval_method == "sparse"
        assert "hello" in results[0].content.lower()

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    @patch("src.memory.hybrid_retrieval.QdrantClient")
    def test_dense_search(self, mock_qdrant_client, mock_sentence_transformer):
        """Testa busca densa."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

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


class TestHybridRetrievalHybridTopological:
    """Testes de integração entre HybridRetrievalSystem e HybridTopologicalEngine."""

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_hybrid_retrieval_with_topological_metrics(self, mock_sentence_transformer):
        """Testa que HybridRetrievalSystem pode ser usado com métricas topológicas."""
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

        # Criar HybridRetrievalSystem
        retrieval = HybridRetrievalSystem(collection_name="test")

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
        assert retrieval.collection_name == "test"
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # HybridRetrieval: busca híbrida (dense + sparse)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_rerank_without_model(self, mock_sentence_transformer):
        """Testa reranking sem modelo (deve retornar top-K ordenado)."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

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

    @patch("src.memory.hybrid_retrieval.SentenceTransformer")
    def test_retrieve_hybrid(self, mock_sentence_transformer):
        """Testa retrieval híbrido completo."""
        # Mock do modelo
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model

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
