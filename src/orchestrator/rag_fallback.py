"""
RAG Fallback System - Fallback Inteligente quando Agentes Falham

Quando um agente falha, usa RAG retrieval para buscar conhecimento relevante
dos datasets indexados e reexecuta com contexto aumentado.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..memory.dataset_indexer import DatasetIndexer
from ..memory.hybrid_retrieval import HybridRetrievalSystem, RetrievalResult
from ..observability.module_logger import get_module_logger
from ..observability.module_metrics import get_metrics_collector
from ..orchestrator.error_analyzer import ErrorAnalyzer, ErrorAnalysis

logger = logging.getLogger(__name__)
structured_logger = get_module_logger("RAGFallbackSystem")
metrics = get_metrics_collector()


@dataclass
class RAGFallbackResult:
    """Resultado do RAG fallback."""

    success: bool
    retrieved_docs: List[RetrievalResult]
    augmented_context: str
    query_generated: str
    num_docs: int
    retrieval_time: float
    reexecution_result: Optional[Any] = None


class RAGFallbackSystem:
    """
    Sistema de fallback RAG quando agentes falham.

    Características:
    - Analisa erro para gerar query de retrieval
    - Busca conhecimento relevante nos datasets indexados
    - Aumenta contexto com documentos recuperados
    - Reexecuta tarefa com contexto aumentado
    """

    def __init__(
        self,
        retrieval_system: HybridRetrievalSystem,
        error_analyzer: Optional[ErrorAnalyzer] = None,
        collections: Optional[List[str]] = None,
        dataset_indexer: Optional[DatasetIndexer] = None,
        auto_index_datasets: bool = True,
    ):
        """
        Inicializa RAGFallbackSystem.

        Args:
            retrieval_system: Sistema de retrieval híbrido
            error_analyzer: Analisador de erros (opcional)
            collections: Lista de coleções para buscar (default: todas)
            dataset_indexer: DatasetIndexer para indexar datasets (FASE 3.1)
            auto_index_datasets: Se True, indexa datasets automaticamente na inicialização
        """
        self.retrieval_system = retrieval_system
        self.error_analyzer = error_analyzer or ErrorAnalyzer()
        self.collections = collections or [
            "scientific_papers_kb",
            "qa_knowledge_kb",
            "code_examples_kb",
            "ontology_knowledge_kb",
            "reasoning_patterns_kb",
            "training_examples_kb",
        ]

        # Inicializar DatasetIndexer (FASE 3.1: Integração em Produção)
        if dataset_indexer is not None:
            self.dataset_indexer = dataset_indexer
        else:
            # Criar DatasetIndexer reutilizando embedding_model do retrieval_system
            self.dataset_indexer = DatasetIndexer(
                qdrant_url=retrieval_system.qdrant_url,
                embedding_model=retrieval_system.embedding_model,  # Reutilizar modelo
            )

        # Indexar datasets automaticamente se habilitado (FASE 3.1)
        if auto_index_datasets:
            try:
                indexed = self.dataset_indexer.get_indexed_datasets()
                if not indexed:
                    logger.info("Nenhum dataset indexado. Iniciando indexação automática...")
                    index_result = self.dataset_indexer.index_all_datasets()
                    logger.info(
                        f"Indexação automática concluída: "
                        f"{index_result.get('total_chunks', 0)} chunks indexados"
                    )
                else:
                    logger.info(f"Datasets já indexados: {len(indexed)} datasets")
            except Exception as e:
                logger.warning(f"Erro ao indexar datasets automaticamente: {e}")

        logger.info(f"RAGFallbackSystem inicializado: {len(self.collections)} coleções disponíveis")
        if structured_logger:
            structured_logger.info(
                "RAGFallbackSystem inicializado",
                {
                    "collections": self.collections,
                    "num_collections": len(self.collections),
                    "dataset_indexer_available": self.dataset_indexer is not None,
                },
            )
        metrics.record_metric(
            "RAGFallbackSystem",
            "initialized",
            1,
            {
                "num_collections": len(self.collections),
                "dataset_indexer_available": self.dataset_indexer is not None,
            },
        )

    def retrieve_on_failure(
        self,
        task: str,
        error: Exception,
        num_docs: int = 5,
        context: Optional[Dict[str, Any]] = None,
    ) -> RAGFallbackResult:
        """
        Retrieval quando agente falha.

        Args:
            task: Tarefa original que falhou
            error: Erro ocorrido
            num_docs: Número de documentos a recuperar
            context: Contexto adicional

        Returns:
            RAGFallbackResult
        """
        import time

        start_time = time.time()
        context = context or {}

        logger.info(f"RAG Fallback ativado para tarefa: {task[:100]}...")

        # 1. Analisar erro para gerar query
        error_analysis = self.error_analyzer.analyze_error(error, context={"task": task})
        query = self._generate_retrieval_query(task, error, error_analysis)

        logger.debug(f"Query gerada para retrieval: {query}")

        # 2. Buscar documentos relevantes
        retrieved_docs: List[RetrievalResult] = []
        for collection in self.collections:
            try:
                # Usar retrieval system para buscar na coleção
                # Nota: HybridRetrievalSystem precisa ser configurado para cada coleção
                # Por enquanto, usar a coleção padrão
                results = self.retrieval_system.retrieve(query, top_k=num_docs)
                retrieved_docs.extend(results)
            except Exception as e:
                logger.warning(f"Erro ao buscar na coleção {collection}: {e}")

        # Limitar número de documentos
        retrieved_docs = retrieved_docs[:num_docs]

        retrieval_time = time.time() - start_time

        # 3. Aumentar contexto
        augmented_context = self.augment_context(task, retrieved_docs, error_analysis)

        retrieval_time = time.time() - start_time
        logger.info(
            f"RAG Fallback: {len(retrieved_docs)} documentos recuperados em "
            f"{retrieval_time:.2f}s"
        )

        return RAGFallbackResult(
            success=len(retrieved_docs) > 0,
            retrieved_docs=retrieved_docs,
            augmented_context=augmented_context,
            query_generated=query,
            num_docs=len(retrieved_docs),
            retrieval_time=retrieval_time,
        )

    def _generate_retrieval_query(
        self, task: str, error: Exception, error_analysis: ErrorAnalysis
    ) -> str:
        """
        Gera query de retrieval baseado na tarefa e erro.

        Args:
            task: Tarefa original
            error: Erro ocorrido
            error_analysis: Análise do erro

        Returns:
            Query para retrieval
        """
        error_message = str(error)

        # Construir query combinando tarefa, tipo de erro e mensagem
        query_parts = [task]

        # Adicionar contexto baseado no tipo de erro
        if error_analysis.error_type.value == "syntax_error":
            query_parts.append("syntax error correction")
        elif error_analysis.error_type.value == "dependency_missing":
            query_parts.append("dependency installation")
        elif error_analysis.error_type.value == "path_error":
            query_parts.append("file path resolution")
        elif error_analysis.error_type.value == "tool_failure":
            query_parts.append("tool alternative implementation")
        else:
            query_parts.append("error resolution")

        # Adicionar palavras-chave do erro (primeiras palavras)
        error_words = error_message.split()[:5]
        query_parts.extend(error_words)

        query = " ".join(query_parts)

        return query

    def augment_context(
        self,
        task: str,
        retrieved_docs: List[RetrievalResult],
        error_analysis: Optional[ErrorAnalysis] = None,
    ) -> str:
        """
        Aumenta prompt com contexto recuperado.

        Args:
            task: Tarefa original
            retrieved_docs: Documentos recuperados
            error_analysis: Análise do erro (opcional)

        Returns:
            Contexto aumentado
        """
        if not retrieved_docs:
            return task

        # Construir contexto aumentado
        context_parts = [f"Tarefa original: {task}"]

        if error_analysis:
            context_parts.append(
                f"\nErro detectado: {error_analysis.error_type.value} - "
                f"{error_analysis.error_message}"
            )
            if error_analysis.suggested_actions:
                context_parts.append(
                    f"\nAções sugeridas: {', '.join(error_analysis.suggested_actions[:3])}"
                )

        context_parts.append("\n\nConhecimento relevante recuperado:")

        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"\n[{i}] {doc.content[:200]}...")
            if doc.metadata:
                source = doc.metadata.get("source", "unknown")
                context_parts.append(f"    (Fonte: {source})")

        context_parts.append("\n\nUse o conhecimento acima para resolver a tarefa corretamente.")

        augmented_context = "\n".join(context_parts)

        logger.debug(f"Contexto aumentado: {len(augmented_context)} caracteres")

        return augmented_context

    def reexecute_with_context(
        self,
        task: str,
        error: Exception,
        agent_callable: Any,
        num_docs: int = 5,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Reexecuta tarefa com contexto aumentado via RAG.

        Args:
            task: Tarefa original
            error: Erro ocorrido
            agent_callable: Função do agente para reexecutar
            num_docs: Número de documentos a recuperar
            context: Contexto adicional

        Returns:
            Resultado da reexecução
        """
        # 1. Retrieval
        fallback_result = self.retrieve_on_failure(task, error, num_docs, context)

        if not fallback_result.success:
            logger.warning("RAG Fallback não recuperou documentos relevantes")
            return {
                "status": "failed",
                "error": "RAG fallback não recuperou documentos",
                "fallback_result": fallback_result,
            }

        # 2. Reexecutar com contexto aumentado
        try:
            augmented_task = fallback_result.augmented_context
            reexecution_result = agent_callable(augmented_task, context)

            fallback_result.reexecution_result = reexecution_result

            logger.info("Reexecução com contexto RAG bem-sucedida")

            return {
                "status": "success",
                "result": reexecution_result,
                "fallback_result": {
                    "retrieved_docs": len(fallback_result.retrieved_docs),
                    "query": fallback_result.query_generated,
                    "retrieval_time": fallback_result.retrieval_time,
                },
            }

        except Exception as e:
            logger.error(f"Reexecução com contexto RAG falhou: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "fallback_result": {
                    "retrieved_docs": len(fallback_result.retrieved_docs),
                    "query": fallback_result.query_generated,
                },
            }

    def get_fallback_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de fallback."""
        # Em produção, rastrear estatísticas
        return {
            "collections_available": len(self.collections),
            "retrieval_system": "HybridRetrievalSystem",
            "error_analyzer_enabled": self.error_analyzer is not None,
        }
