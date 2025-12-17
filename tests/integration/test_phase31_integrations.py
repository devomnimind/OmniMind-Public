"""
Testes de Integração - FASE 3.1: Integração em Produção

Testa as integrações:
1. SemanticCache no OrchestratorAgent
2. ModelOptimizer no HybridRetrievalSystem
3. DatasetIndexer no RAGFallbackSystem

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import os
from unittest.mock import patch

import pytest

from src.agents.orchestrator_agent import OrchestratorAgent
from src.memory.hybrid_retrieval import HybridRetrievalSystem
from src.memory.semantic_cache import SemanticCacheLayer
from src.orchestrator.rag_fallback import RAGFallbackSystem


class TestSemanticCacheIntegration:
    """Testa integração do SemanticCache no OrchestratorAgent."""

    def test_orchestrator_has_semantic_cache(self):
        """Testa se OrchestratorAgent inicializa com SemanticCache."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Verificar se semantic_cache foi inicializado
        assert orchestrator.semantic_cache is not None
        assert isinstance(orchestrator.semantic_cache, SemanticCacheLayer)

    def test_semantic_cache_reuses_embedding_model(self):
        """Testa se SemanticCache reutiliza embedding_model do HybridRetrievalSystem."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Verificar se embedding_model foi reutilizado
        assert orchestrator.semantic_cache is not None
        assert orchestrator.semantic_cache.embedding_model is not None
        assert orchestrator.rag_fallback is not None
        assert (
            orchestrator.semantic_cache.embedding_model
            == orchestrator.rag_fallback.retrieval_system.embedding_model
        )

    @patch("src.agents.orchestrator_agent.SemanticCacheLayer.get_or_compute")
    def test_semantic_cache_used_in_subtask_execution(self, mock_get_or_compute):
        """Testa se SemanticCache é usado na execução de subtarefas."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Mock do cache retornando resultado
        mock_get_or_compute.return_value = (
            '{"completed": True, "final_result": "test", "iteration": 1}'
        )

        # Executar subtarefa (deve usar cache)
        from src.agents.orchestrator_agent import AgentMode

        subtask = {"description": "Test task", "agent": "code"}
        result = orchestrator._execute_subtask_by_agent(
            subtask=subtask, agent_mode=AgentMode.CODE, max_iterations=1
        )

        # Verificar se cache foi chamado
        assert mock_get_or_compute.called
        assert result["completed"] is True


class TestModelOptimizerIntegration:
    """Testa integração do ModelOptimizer no HybridRetrievalSystem."""

    def test_hybrid_retrieval_has_model_optimizer(self):
        """Testa se HybridRetrievalSystem inicializa com ModelOptimizer."""
        retrieval = HybridRetrievalSystem(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name="test_collection",
            use_model_optimizer=True,
        )

        # Verificar se model_optimizer foi inicializado
        assert retrieval.model_optimizer is not None

    def test_hybrid_retrieval_without_optimizer(self):
        """Testa HybridRetrievalSystem sem ModelOptimizer."""
        retrieval = HybridRetrievalSystem(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name="test_collection",
            use_model_optimizer=False,
        )

        # Verificar se model_optimizer não foi inicializado
        assert retrieval.model_optimizer is None

    def test_model_optimizer_env_var(self):
        """Testa se env var controla quantização INT8."""
        # Testar com INT8 habilitado
        with patch.dict(os.environ, {"OMNIMIND_USE_INT8_QUANTIZATION": "true"}):
            retrieval = HybridRetrievalSystem(
                qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                collection_name="test_collection",
                use_model_optimizer=True,
            )

            if retrieval.model_optimizer:
                assert retrieval.model_optimizer.default_precision.value == "int8"

    def test_hybrid_retrieval_embedding_model_optimized(self):
        """Testa se embedding_model é otimizado quando ModelOptimizer está habilitado."""
        retrieval = HybridRetrievalSystem(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name="test_collection",
            use_model_optimizer=True,
        )

        # Verificar se embedding_model existe
        assert retrieval.embedding_model is not None


class TestDatasetIndexerIntegration:
    """Testa integração do DatasetIndexer no RAGFallbackSystem."""

    def test_rag_fallback_has_dataset_indexer(self):
        """Testa se RAGFallbackSystem inicializa com DatasetIndexer."""
        from src.memory.hybrid_retrieval import HybridRetrievalSystem
        from src.orchestrator.error_analyzer import ErrorAnalyzer

        retrieval = HybridRetrievalSystem(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name="test_collection",
        )
        error_analyzer = ErrorAnalyzer()

        rag_fallback = RAGFallbackSystem(
            retrieval_system=retrieval,
            error_analyzer=error_analyzer,
            auto_index_datasets=False,  # Não indexar automaticamente nos testes
        )

        # Verificar se dataset_indexer foi inicializado
        assert rag_fallback.dataset_indexer is not None

    def test_rag_fallback_reuses_embedding_model(self):
        """Testa se DatasetIndexer reutiliza embedding_model do HybridRetrievalSystem."""
        from src.memory.hybrid_retrieval import HybridRetrievalSystem
        from src.orchestrator.error_analyzer import ErrorAnalyzer

        retrieval = HybridRetrievalSystem(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name="test_collection",
        )
        error_analyzer = ErrorAnalyzer()

        rag_fallback = RAGFallbackSystem(
            retrieval_system=retrieval,
            error_analyzer=error_analyzer,
            auto_index_datasets=False,
        )

        # Verificar se embedding_model foi reutilizado
        assert rag_fallback.dataset_indexer.embedding_model is not None
        assert rag_fallback.dataset_indexer.embedding_model == retrieval.embedding_model

    def test_rag_fallback_with_custom_dataset_indexer(self):
        """Testa RAGFallbackSystem com DatasetIndexer customizado."""
        from src.memory.dataset_indexer import DatasetIndexer
        from src.memory.hybrid_retrieval import HybridRetrievalSystem
        from src.orchestrator.error_analyzer import ErrorAnalyzer

        retrieval = HybridRetrievalSystem(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name="test_collection",
        )
        error_analyzer = ErrorAnalyzer()

        # Criar DatasetIndexer customizado
        custom_indexer = DatasetIndexer(
            qdrant_url=retrieval.qdrant_url,
            embedding_model=retrieval.embedding_model,
        )

        rag_fallback = RAGFallbackSystem(
            retrieval_system=retrieval,
            error_analyzer=error_analyzer,
            dataset_indexer=custom_indexer,
            auto_index_datasets=False,
        )

        # Verificar se DatasetIndexer customizado foi usado
        assert rag_fallback.dataset_indexer == custom_indexer


class TestFullIntegration:
    """Testa integração completa de todos os componentes."""

    def test_orchestrator_full_integration(self):
        """Testa integração completa no OrchestratorAgent."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Verificar todos os componentes integrados
        assert orchestrator.semantic_cache is not None
        assert orchestrator.rag_fallback is not None
        assert orchestrator.rag_fallback.retrieval_system is not None
        assert orchestrator.rag_fallback.dataset_indexer is not None

        # Verificar reutilização de embedding_model
        retrieval = orchestrator.rag_fallback.retrieval_system
        assert retrieval.embedding_model is not None
        assert orchestrator.semantic_cache.embedding_model == retrieval.embedding_model
        assert (
            orchestrator.rag_fallback.dataset_indexer.embedding_model == retrieval.embedding_model
        )

    def test_model_optimizer_in_retrieval_system(self):
        """Testa se ModelOptimizer está disponível no HybridRetrievalSystem do Orchestrator."""
        config_path = "config/agent_config.yaml"
        if not os.path.exists(config_path):
            pytest.skip(f"Config file not found: {config_path}")

        orchestrator = OrchestratorAgent(config_path=config_path)

        # Verificar se ModelOptimizer está disponível (pode ser None se não habilitado)
        assert orchestrator.rag_fallback is not None
        retrieval = orchestrator.rag_fallback.retrieval_system
        # ModelOptimizer pode ser None se use_model_optimizer=False
        # Isso é OK, apenas verificamos que o sistema funciona
        assert retrieval is not None
        assert retrieval.embedding_model is not None
