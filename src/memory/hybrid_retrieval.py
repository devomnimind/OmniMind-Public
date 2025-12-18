"""
Hybrid Retrieval System - Sistema de Retrieval Híbrido para RAG

Combina busca densa (semantic search via Qdrant) com busca esparsa
(keyword/BM25) e reranking com Cross-Encoder para melhor qualidade.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import logging
import os
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Resultado de retrieval com metadados."""

    content: str
    score: float
    source: str
    metadata: Dict[str, Any]
    retrieval_method: str  # "dense", "sparse", "reranked"


class HybridRetrievalSystem:
    """
    Sistema de retrieval híbrido para RAG.

    Combina:
    1. Dense search (semantic via Qdrant)
    2. Sparse search (keyword/BM25)
    3. Reranking (Cross-Encoder)

    Pipeline:
    Query → Dense (top-20) + Sparse (top-20) → Merge → Rerank (top-5) → Return
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_embeddings",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        reranker_model_name: Optional[str] = None,
        embedding_model: Optional[SentenceTransformer] = None,
        top_k_dense: int = 20,
        top_k_sparse: int = 20,
        top_k_final: int = 5,
        use_model_optimizer: bool = True,
    ):
        """
        Inicializa sistema de retrieval híbrido.

        Args:
            qdrant_url: URL do Qdrant
            collection_name: Nome da coleção no Qdrant
            embedding_model_name: Nome do modelo de embeddings
            reranker_model_name: Nome do modelo reranker (opcional)
            embedding_model: Modelo de embeddings opcional (reutilizar)
            top_k_dense: Top-K para busca densa
            top_k_sparse: Top-K para busca esparsa
            top_k_final: Top-K final após reranking
            use_model_optimizer: Se True, usa ModelOptimizer para otimizar modelos (FASE 3.1)
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model_name
        self.reranker_model_name = reranker_model_name
        self.top_k_dense = top_k_dense
        self.top_k_sparse = top_k_sparse
        self.top_k_final = top_k_final
        self.use_model_optimizer = use_model_optimizer

        # Inicializar ModelOptimizer se habilitado (FASE 3.1: Integração em Produção)
        self.model_optimizer = None
        if use_model_optimizer:
            try:
                from ..memory.model_optimizer import ModelOptimizer, ModelPrecision

                # Verificar se deve usar quantização INT8 (via env var)
                use_int8 = os.getenv("OMNIMIND_USE_INT8_QUANTIZATION", "false").lower() == "true"
                default_precision = ModelPrecision.INT8 if use_int8 else ModelPrecision.FP32

                self.model_optimizer = ModelOptimizer(
                    default_precision=default_precision,
                    enable_kv_cache=True,
                    kv_cache_size=512,
                )
                logger.info(
                    f"ModelOptimizer habilitado: precision={default_precision.value}, "
                    f"kv_cache=enabled"
                )
            except Exception as e:
                logger.warning(
                    f"Erro ao inicializar ModelOptimizer: {e}. Continuando sem otimização."
                )
                self.model_optimizer = None

        # Inicializar modelo de embeddings
        if embedding_model is not None:
            self.embedding_model = embedding_model
            embedding_dim_raw = self.embedding_model.get_sentence_embedding_dimension()
            self.embedding_dim = int(embedding_dim_raw) if embedding_dim_raw is not None else 384
        else:
            from src.utils.device_utils import (
                ensure_tensor_on_real_device,
                get_sentence_transformer_device,
            )

            # Resolve model name for offline compatibility (resolve short names to full paths)
            try:
                from src.utils.offline_mode import resolve_sentence_transformer_name

                resolved_model_name = resolve_sentence_transformer_name(embedding_model_name)
            except ImportError:
                resolved_model_name = embedding_model_name

            device = get_sentence_transformer_device()
            logger.info(f"Carregando modelo de embeddings: {resolved_model_name} (device={device})")

            # CORREÇÃO (2025-12-17): Carregar SEMPRE em CPU primeiro para evitar meta tensor
            embedding_model = SentenceTransformer(resolved_model_name, device="cpu")

            # Garantir que o modelo está em dispositivo real (não meta)
            ensure_tensor_on_real_device(embedding_model)

            # Se device desejado não é CPU, tentar mover
            if device != "cpu":
                try:
                    # Verificação explícita de meta tensors
                    has_meta_tensors = any(
                        p.device.type == "meta" for p in embedding_model.parameters()
                    )

                    if has_meta_tensors:
                        logger.warning("Meta tensors detectados, usando to_empty()")
                        embedding_model = embedding_model.to_empty(device=device)
                    else:
                        embedding_model = embedding_model.to(device)

                    logger.debug(f"✓ Modelo movido para {device}")
                except Exception as e:
                    logger.warning(f"Erro ao mover para {device}: {e}, mantendo em CPU")
                    # Se falhou ao mover (ex: meta tensor não resolvido), tenta recuperar em CPU
                    if "meta" in str(e).lower():
                        try:
                            embedding_model = embedding_model.to_empty(device="cpu")
                        except Exception:
                            pass
                    else:
                        embedding_model = embedding_model.to("cpu")

            self.embedding_model = embedding_model
            embedding_dim_raw = self.embedding_model.get_sentence_embedding_dimension()
            self.embedding_dim = int(embedding_dim_raw) if embedding_dim_raw is not None else 384
            logger.info(f"Modelo carregado. Dimensões: {self.embedding_dim}, Device: {device}")

        # Otimizar modelo de embeddings se ModelOptimizer disponível (FASE 3.1)
        if self.model_optimizer and self.embedding_model:
            try:
                optimized_model = self.model_optimizer.optimize_embedding_model(
                    model_name=embedding_model_name,
                    model=self.embedding_model,
                    precision=self.model_optimizer.default_precision,
                    use_kv_cache=True,
                )
                if optimized_model:
                    self.embedding_model = optimized_model
                    precision_value = self.model_optimizer.default_precision.value
                    logger.info(f"Modelo de embeddings otimizado: {precision_value}")
            except Exception as e:
                logger.warning(
                    f"Erro ao otimizar modelo de embeddings: {e}. Usando modelo original."
                )

        # Inicializar reranker (opcional, lazy load)
        self.reranker_model: Optional[SentenceTransformer] = None
        if reranker_model_name:
            try:
                from src.utils.device_utils import get_sentence_transformer_device

                # Resolve model name for offline compatibility
                try:
                    from src.utils.offline_mode import resolve_sentence_transformer_name

                    resolved_reranker_name = resolve_sentence_transformer_name(reranker_model_name)
                except ImportError:
                    resolved_reranker_name = reranker_model_name

                device = get_sentence_transformer_device()
                logger.info(f"Carregando reranker: {resolved_reranker_name} (device={device})")
                self.reranker_model = SentenceTransformer(resolved_reranker_name, device=device)
                logger.info(f"Reranker carregado (device={device})")
            except Exception as e:
                logger.warning(f"Erro ao carregar reranker: {e}. Continuando sem reranking.")

        # Inicializar Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # Cache de documentos para BM25 (será populado conforme necessário)
        self._document_cache: Dict[str, str] = {}
        self._bm25_index: Optional[Dict[str, Any]] = None

        logger.info(
            f"HybridRetrievalSystem inicializado: "
            f"collection={collection_name}, "
            f"dense_k={top_k_dense}, sparse_k={top_k_sparse}, final_k={top_k_final}"
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para texto."""
        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return [0.0] * self.embedding_dim

    def _dense_search(self, query: str, top_k: Optional[int] = None) -> List[RetrievalResult]:
        """
        Busca densa (semantic search) via Qdrant.

        Args:
            query: Query de busca
            top_k: Top-K resultados (default: self.top_k_dense)

        Returns:
            Lista de RetrievalResult
        """
        top_k = top_k or self.top_k_dense

        try:
            # Gerar embedding da query
            query_embedding = self._generate_embedding(query)

            # Buscar no Qdrant
            # Prefer newer query_points API, fallback to older search/search_points
            query_points = getattr(self.client, "query_points", None)
            if callable(query_points):
                # Nova API do Qdrant (v1.7+)
                search_result = query_points(  # type: ignore[attr-defined]
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=top_k,
                    with_payload=True,
                    with_vectors=False,
                )
                results = (
                    search_result.points if hasattr(search_result, "points") else search_result
                )
            else:
                # Fallback para API antiga
                search_fn = getattr(self.client, "search", None)
                if callable(search_fn):
                    results = search_fn(  # type: ignore[attr-defined]
                        collection_name=self.collection_name,
                        query_vector=query_embedding,
                        limit=top_k,
                        with_payload=True,
                    )
                else:
                    # Último fallback: search_points
                    search_points = getattr(self.client, "search_points", None)
                    if not callable(search_points):
                        raise AttributeError("QdrantClient query/search APIs indisponíveis")
                    results = search_points(  # type: ignore[attr-defined]
                        collection_name=self.collection_name,
                        vector=query_embedding,
                        limit=top_k,
                        with_payload=True,
                    )

            retrieval_results = []
            for hit in results:
                payload = hit.payload or {}
                content = payload.get("content", payload.get("text", ""))
                if not content:
                    continue

                retrieval_results.append(
                    RetrievalResult(
                        content=content,
                        score=hit.score or 0.0,
                        source=payload.get("source", "unknown"),
                        metadata=payload,
                        retrieval_method="dense",
                    )
                )

            logger.debug(f"Busca densa retornou {len(retrieval_results)} resultados")
            return retrieval_results

        except Exception as e:
            logger.warning(f"Erro na busca densa: {e}")
            return []

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto para BM25."""
        # Normalizar e tokenizar
        text_lower = text.lower()
        # Remover pontuação e dividir
        tokens = re.findall(r"\b\w+\b", text_lower)
        return tokens

    def _build_bm25_index(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Constrói índice BM25 simples.

        Args:
            documents: Lista de documentos {id: str, content: str}

        Returns:
            Índice BM25
        """
        # Parâmetros BM25
        k1 = 1.5
        b = 0.75

        # Coletar todos os termos
        doc_freqs: Dict[str, int] = Counter()  # Term frequency por documento
        doc_lengths: Dict[str, int] = {}  # Comprimento de cada documento
        term_doc_freq: Dict[str, int] = Counter()  # Número de docs com termo

        for doc in documents:
            doc_id = doc["id"]
            content = doc["content"]
            tokens = self._tokenize(content)

            doc_lengths[doc_id] = len(tokens)
            doc_freqs_local = Counter(tokens)

            for term, freq in doc_freqs_local.items():
                doc_freqs[f"{doc_id}:{term}"] = freq
                term_doc_freq[term] += 1

        avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 1.0

        return {
            "doc_freqs": doc_freqs,
            "doc_lengths": doc_lengths,
            "term_doc_freq": term_doc_freq,
            "avg_doc_length": avg_doc_length,
            "total_docs": len(documents),
            "k1": k1,
            "b": b,
        }

    def _bm25_score(self, query: str, doc_id: str, index: Dict[str, Any]) -> float:
        """
        Calcula score BM25 para query e documento.

        Args:
            query: Query de busca
            doc_id: ID do documento
            index: Índice BM25

        Returns:
            Score BM25
        """
        query_tokens = self._tokenize(query)
        doc_freqs = index["doc_freqs"]
        doc_lengths = index["doc_lengths"]
        term_doc_freq = index["term_doc_freq"]
        avg_doc_length = index["avg_doc_length"]
        total_docs = index["total_docs"]
        k1 = index["k1"]
        b = index["b"]

        score = 0.0
        doc_length = doc_lengths.get(doc_id, 1)

        for term in query_tokens:
            if term not in term_doc_freq:
                continue

            # Term frequency no documento
            tf = doc_freqs.get(f"{doc_id}:{term}", 0)
            if tf == 0:
                continue

            # Inverse document frequency
            idf = (total_docs - term_doc_freq[term] + 0.5) / (term_doc_freq[term] + 0.5)
            idf = max(0.0, idf)  # Evitar negativo

            # BM25 score
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            score += idf * (numerator / denominator)

        return score

    def _sparse_search(
        self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Busca esparsa (BM25 keyword search).

        Args:
            query: Query de busca
            documents: Lista de documentos {id: str, content: str, source: str, metadata: dict}
            top_k: Top-K resultados (default: self.top_k_sparse)

        Returns:
            Lista de RetrievalResult
        """
        top_k = top_k or self.top_k_sparse

        if not documents:
            return []

        try:
            # Construir índice BM25
            index = self._build_bm25_index(documents)

            # Calcular scores
            scores: List[tuple[str, float]] = []
            for doc in documents:
                doc_id = doc["id"]
                score = self._bm25_score(query, doc_id, index)
                if score > 0:
                    scores.append((doc_id, score))

            # Ordenar por score
            scores.sort(key=lambda x: x[1], reverse=True)

            # Retornar top-K
            retrieval_results = []
            for doc_id, score in scores[:top_k]:
                # Encontrar documento original
                found_doc: Dict[str, Any] | None = next(
                    (d for d in documents if d.get("id") == doc_id), None
                )
                if not found_doc:
                    continue

                # Garantir que metadata é dict
                metadata: Dict[str, Any] = found_doc.get("metadata", {})
                if isinstance(metadata, str):
                    metadata = {}

                retrieval_results.append(
                    RetrievalResult(
                        content=found_doc["content"],
                        score=score,
                        source=found_doc.get("source", "unknown"),
                        metadata=metadata,
                        retrieval_method="sparse",
                    )
                )

            logger.debug(f"Busca esparsa retornou {len(retrieval_results)} resultados")
            return retrieval_results

        except Exception as e:
            logger.warning(f"Erro na busca esparsa: {e}")
            return []

    def _rerank(
        self, query: str, results: List[RetrievalResult], top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Reranking com Cross-Encoder (se disponível).

        Args:
            query: Query original
            results: Resultados para rerankear
            top_k: Top-K final (default: self.top_k_final)

        Returns:
            Lista de RetrievalResult rerankeada
        """
        top_k = top_k or self.top_k_final

        if not self.reranker_model or not results:
            # Sem reranker, retornar top-K por score original
            results_sorted = sorted(results, key=lambda x: x.score, reverse=True)
            return results_sorted[:top_k]

        try:
            # Preparar pares (query, document)
            pairs = [(query, result.content) for result in results]

            # Rerankear
            scores = self.reranker_model.predict(pairs)

            # Atualizar scores e ordenar
            for i, result in enumerate(results):
                result.score = float(scores[i]) if hasattr(scores, "__getitem__") else float(scores)
                result.retrieval_method = "reranked"

            results_sorted = sorted(results, key=lambda x: x.score, reverse=True)
            logger.debug(f"Reranking retornou {len(results_sorted[:top_k])} resultados")
            return results_sorted[:top_k]

        except Exception as e:
            logger.warning(f"Erro no reranking: {e}. Retornando resultados originais.")
            results_sorted = sorted(results, key=lambda x: x.score, reverse=True)
            return results_sorted[:top_k]

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        use_sparse: bool = True,
        use_rerank: bool = True,
    ) -> List[RetrievalResult]:
        """
        Retrieval híbrido completo.

        Args:
            query: Query de busca
            top_k: Top-K final (default: self.top_k_final)
            filters: Filtros opcionais (não implementado ainda)
            use_sparse: Se True, usa busca esparsa também
            use_rerank: Se True, usa reranking

        Returns:
            Lista de RetrievalResult
        """
        top_k = top_k or self.top_k_final

        # 1. Busca densa
        dense_results = self._dense_search(query)

        # 2. Busca esparsa (se habilitada)
        sparse_results: List[RetrievalResult] = []
        if use_sparse:
            # Converter dense_results para formato de documentos
            documents = [
                {
                    "id": f"dense_{i}",
                    "content": result.content,
                    "source": result.source,
                    "metadata": result.metadata,
                }
                for i, result in enumerate(dense_results)
            ]
            sparse_results = self._sparse_search(query, documents)

        # 3. Merge e deduplicate
        all_results: Dict[str, RetrievalResult] = {}
        for result in dense_results:
            # Usar hash do conteúdo como chave (convertido para string)
            key = str(hash(result.content))
            if key not in all_results or result.score > all_results[key].score:
                all_results[key] = result

        for result in sparse_results:
            key = str(hash(result.content))
            if key not in all_results or result.score > all_results[key].score:
                all_results[key] = result

        merged_results = list(all_results.values())

        # 4. Reranking (se habilitado)
        if use_rerank and merged_results:
            final_results = self._rerank(query, merged_results, top_k)
        else:
            # Ordenar por score e pegar top-K
            final_results = sorted(merged_results, key=lambda x: x.score, reverse=True)[:top_k]

        logger.info(
            f"Retrieval híbrido: query='{query[:50]}...', "
            f"dense={len(dense_results)}, sparse={len(sparse_results)}, "
            f"merged={len(merged_results)}, final={len(final_results)}"
        )

        return final_results
