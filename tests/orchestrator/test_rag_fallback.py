"""
Testes para RAGFallbackSystem.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock

import pytest

from src.memory.hybrid_retrieval import HybridRetrievalSystem, RetrievalResult
from src.orchestrator.error_analyzer import (
    ErrorAnalysis,
    ErrorAnalyzer,
    ErrorType,
    RecoveryStrategy,
)
from src.orchestrator.rag_fallback import RAGFallbackSystem


class TestRAGFallbackSystem:
    """Testes para RAGFallbackSystem."""

    @pytest.fixture
    def mock_retrieval_system(self):
        """Fixture para mockar HybridRetrievalSystem."""
        mock = MagicMock(spec=HybridRetrievalSystem)
        # Adicionar atributos necessários que o código real acessa
        mock.qdrant_url = "http://localhost:6333"
        mock.collection_name = "test_collection"
        mock.retrieve.return_value = [
            RetrievalResult(
                content="Test document content",
                score=0.95,
                source="test_source",
                metadata={"source": "test"},
                retrieval_method="dense",
            )
        ]
        return mock

    @pytest.fixture
    def rag_fallback(self, mock_retrieval_system):
        """Fixture para RAGFallbackSystem."""
        return RAGFallbackSystem(
            retrieval_system=mock_retrieval_system,
            error_analyzer=ErrorAnalyzer(),
        )

    def test_init(self, rag_fallback):
        """Testa inicialização."""
        assert rag_fallback.retrieval_system is not None
        assert rag_fallback.error_analyzer is not None
        assert len(rag_fallback.collections) > 0

    def test_generate_retrieval_query(self, rag_fallback):
        """Testa geração de query de retrieval."""
        task = "Process file data"
        error = ValueError("Invalid format")
        error_analysis = ErrorAnalysis(
            error_type=ErrorType.SYNTAX_ERROR,
            error_message="Invalid format",
            error_class="ValueError",
            pattern="syntax_error_invalid_format",
            recovery_strategy=RecoveryStrategy.VALIDATE_AND_FIX_SYNTAX,
            confidence=0.8,
            context={},
            suggested_actions=["validate format"],
            alternative_strategies=[],
        )

        query = rag_fallback._generate_retrieval_query(task, error, error_analysis)

        assert task in query
        assert "syntax" in query.lower() or "error" in query.lower()

    def test_augment_context(self, rag_fallback):
        """Testa aumento de contexto."""
        task = "Test task"
        retrieved_docs = [
            RetrievalResult(
                content="Relevant knowledge content here",
                score=0.9,
                source="test",
                metadata={"source": "test"},
                retrieval_method="dense",
            )
        ]

        augmented = rag_fallback.augment_context(task, retrieved_docs)

        assert task in augmented
        assert "Relevant knowledge" in augmented
        assert "Conhecimento relevante" in augmented

    def test_retrieve_on_failure(self, rag_fallback, mock_retrieval_system):
        """Testa retrieval quando agente falha."""
        task = "Process data"
        error = FileNotFoundError("File not found")

        result = rag_fallback.retrieve_on_failure(task, error, num_docs=3)

        assert result.success is True
        assert len(result.retrieved_docs) > 0
        assert result.query_generated is not None
        assert result.augmented_context is not None
        mock_retrieval_system.retrieve.assert_called()

    def test_reexecute_with_context(self, rag_fallback, mock_retrieval_system):
        """Testa reexecução com contexto."""
        task = "Process file"
        error = ValueError("Invalid input")

        def mock_agent(task, context):
            return {"status": "success", "result": "processed"}

        result = rag_fallback.reexecute_with_context(
            task=task, error=error, agent_callable=mock_agent
        )

        assert result["status"] in ["success", "failed"]
        assert "fallback_result" in result

    def test_get_fallback_stats(self, rag_fallback):
        """Testa obtenção de estatísticas."""
        stats = rag_fallback.get_fallback_stats()

        assert "collections_available" in stats
        assert "retrieval_system" in stats
        assert stats["collections_available"] > 0
