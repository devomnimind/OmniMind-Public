"""Tests for SemanticSearchEngine - Phase 26B

DEPRECATED: Módulo intelligence.semantic_search_engine não existe mais.

SUBSTITUIÇÃO:
- ✅ Substituído por: src.memory.hybrid_retrieval.HybridRetrievalSystem
- ✅ Arquivo: src/memory/hybrid_retrieval.py
- ✅ Funcionalidade: Busca semântica híbrida (associativa + vetorial)
- ✅ Status: Implementado e operacional (Phase 24)

MIGRAÇÃO:
```python
# ANTES (deprecated):
from intelligence.semantic_search_engine import SemanticSearchEngine
engine = SemanticSearchEngine()
results = engine.search(query, ...)

# DEPOIS (atual):
from src.memory.hybrid_retrieval import HybridRetrievalSystem
retrieval = HybridRetrievalSystem()
results = retrieval.retrieve(query, top_k=10)
# Busca semântica híbrida integrada com Phase 24
```

Este teste foi marcado como skip até que seja atualizado para usar HybridRetrievalSystem.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason=(
        "Módulo intelligence.semantic_search_engine foi substituído por "
        "src.memory.hybrid_retrieval"
    )
)

# Import removido - módulo não existe
# from intelligence.semantic_search_engine import SemanticSearchEngine
#
# SUBSTITUIÇÃO: Use src.memory.hybrid_retrieval.HybridRetrievalSystem


class TestSemanticSearchEngine:
    """Test SemanticSearchEngine - DEPRECATED: Use HybridRetrievalSystem instead"""

    @pytest.fixture
    def mock_semantic_memory(self):
        """Mock SemanticMemoryLayer - DEPRECATED"""
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.retrieve_similar.return_value = [
            {"content": "test content", "score": 0.9},
            {"content": "another content", "score": 0.8},
        ]
        return mock

    @pytest.fixture
    def mock_knowledge_integrator(self):
        """Mock KnowledgeIntegrator - DEPRECATED"""
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.query.return_value = {
            "concepts": [{"name": "concept1", "definition": "def1"}],
            "rules": [{"name": "rule1", "description": "desc1"}],
            "episodes": [{"event": "episode1"}],
        }
        return mock

    def test_init_default(self):
        """Test initialization with defaults - DEPRECATED"""
        # Nota: SemanticSearchEngine foi substituído por HybridRetrievalSystem
        # from unittest.mock import MagicMock, patch
        # with (
        #     patch("memory.semantic_memory_layer.get_semantic_memory") as mock_get,
        #     patch("intelligence.semantic_search_engine.KnowledgeIntegrator"),
        # ):
        #     mock_memory = MagicMock()
        #     mock_get.return_value = mock_memory
        #     engine = SemanticSearchEngine()  # DEPRECATED
        #     assert engine.semantic_memory is not None
        #     assert engine.knowledge_integrator is not None
        pytest.skip("Use test_hybrid_retrieval.py instead")

    def test_init_with_dependencies(self, mock_semantic_memory, mock_knowledge_integrator):
        """Test initialization with provided dependencies - DEPRECATED"""
        # Nota: SemanticSearchEngine foi substituído por HybridRetrievalSystem
        # engine = SemanticSearchEngine(  # DEPRECATED
        #     semantic_memory=mock_semantic_memory,
        #     knowledge_integrator=mock_knowledge_integrator,
        # )
        # assert engine.semantic_memory == mock_semantic_memory
        # assert engine.knowledge_integrator == mock_knowledge_integrator
        pytest.skip("Use test_hybrid_retrieval.py instead")

    def test_search(self, mock_semantic_memory, mock_knowledge_integrator):
        """Test basic search - DEPRECATED"""
        # Nota: SemanticSearchEngine foi substituído por HybridRetrievalSystem
        # engine = SemanticSearchEngine(  # DEPRECATED
        #     semantic_memory=mock_semantic_memory,
        #     knowledge_integrator=mock_knowledge_integrator,
        # )
        # results = engine.search("test query", top_k=5)
        # assert "semantic_memory" in results
        # assert "declarative" in results
        # assert "procedural" in results
        # assert "episodic" in results
        # assert "total_results" in results
        # assert results["total_results"] > 0
        # mock_semantic_memory.retrieve_similar.assert_called_once_with("test query", top_k=5)
        # mock_knowledge_integrator.query.assert_called_once_with("test query", layers=None)
        pytest.skip("Use test_hybrid_retrieval.py instead")

    def test_search_with_layers(self, mock_semantic_memory, mock_knowledge_integrator):
        """Test search with specific layers - DEPRECATED"""
        # Nota: SemanticSearchEngine foi substituído por HybridRetrievalSystem
        # engine = SemanticSearchEngine(  # DEPRECATED
        #     semantic_memory=mock_semantic_memory,
        #     knowledge_integrator=mock_knowledge_integrator,
        # )
        # results = engine.search("test query", top_k=10, layers=["declarative", "procedural"])
        # assert results["total_results"] > 0
        # mock_knowledge_integrator.query.assert_called_once_with(
        #     "test query", layers=["declarative", "procedural"]
        # )
        pytest.skip("Use test_hybrid_retrieval.py instead")

    def test_search_with_context(self, mock_semantic_memory, mock_knowledge_integrator):
        """Test search with context filters - DEPRECATED"""
        # Nota: SemanticSearchEngine foi substituído por HybridRetrievalSystem
        # engine = SemanticSearchEngine(  # DEPRECATED
        #     semantic_memory=mock_semantic_memory,
        #     knowledge_integrator=mock_knowledge_integrator,
        # )
        # mock_knowledge_integrator.query.return_value = {...}
        # context = {"category": "system", "rule_type": "process"}
        # results = engine.search_with_context("test query", context, top_k=10)
        # assert "declarative" in results
        # assert "procedural" in results
        pytest.skip("Use test_hybrid_retrieval.py instead")

    def test_search_with_context_no_filters(self, mock_semantic_memory, mock_knowledge_integrator):
        """Test search with context but no filters - DEPRECATED"""
        # Nota: SemanticSearchEngine foi substituído por HybridRetrievalSystem
        # engine = SemanticSearchEngine(  # DEPRECATED
        #     semantic_memory=mock_semantic_memory,
        #     knowledge_integrator=mock_knowledge_integrator,
        # )
        # context = {"other_key": "value"}
        # results = engine.search_with_context("test query", context, top_k=10)
        # assert results["total_results"] > 0
        pytest.skip("Use test_hybrid_retrieval.py instead")
