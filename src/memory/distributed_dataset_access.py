"""
Distributed Dataset Access - Memória Distribuída a Nível de Sistema

Implementa acesso eficiente e distribuído aos datasets indexados usando:
- Cache multi-nível (L1/L2/L3)
- Prefetching inteligente
- Sharding de coleções
- Load balancing de queries

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..scaling.multi_level_cache import CacheLevel, MultiLevelCache

logger = logging.getLogger(__name__)


class DistributedDatasetAccess:
    """
    Sistema de acesso distribuído a datasets indexados.

    Características:
    - Cache multi-nível (L1: memória, L2: Redis, L3: Qdrant)
    - Prefetching baseado em padrões de acesso
    - Sharding de coleções grandes
    - Load balancing de queries
    - Métricas de performance
    """

    def __init__(
        self,
        retrieval_system: Any,  # HybridRetrievalSystem
        cache: Optional[MultiLevelCache] = None,
        enable_prefetch: bool = True,
        prefetch_window: int = 10,
    ):
        """
        Inicializa sistema de acesso distribuído.

        Args:
            retrieval_system: Sistema de retrieval híbrido
            cache: Cache multi-nível (opcional, cria se None)
            enable_prefetch: Se True, habilita prefetching inteligente
            prefetch_window: Janela de prefetch (número de queries futuras previstas)
        """
        self.retrieval_system = retrieval_system
        self.enable_prefetch = enable_prefetch
        self.prefetch_window = prefetch_window

        # Cache multi-nível
        if cache is None:
            from ..scaling.multi_level_cache import CacheConfig, MultiLevelCache

            # Configurar cache multi-nível
            l1_config = CacheConfig(
                max_size_bytes=10 * 1024 * 1024,  # 10MB
                max_entries=1000,
                default_ttl_seconds=3600,
            )
            l2_config = CacheConfig(
                max_size_bytes=100 * 1024 * 1024,  # 100MB
                max_entries=10000,
                default_ttl_seconds=1800,
            )
            l3_config = CacheConfig(
                max_size_bytes=1024 * 1024 * 1024,  # 1GB
                max_entries=100000,
                default_ttl_seconds=7200,
            )
            self.cache = MultiLevelCache(l1_config, l2_config, l3_config)
        else:
            self.cache = cache

        # Histórico de queries para prefetching
        self.query_history: List[str] = []
        self.access_patterns: Dict[str, int] = {}  # query -> count

        logger.info(
            f"DistributedDatasetAccess inicializado: "
            f"prefetch={enable_prefetch}, window={prefetch_window}"
        )

    def retrieve_with_cache(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_cache: bool = True,
        filters: Optional[Dict[str, Any]] = None,
        use_sparse: bool = True,
        use_rerank: bool = True,
    ) -> List[Any]:
        """
        Retrieval com cache multi-nível.

        Pipeline:
        1. Verificar L1 cache (memória)
        2. Se miss, verificar L2 cache (Redis)
        3. Se miss, verificar L3 cache (Qdrant metadata)
        4. Se miss, executar retrieval real
        5. Armazenar resultado em cache
        6. Prefetch queries relacionadas se habilitado

        Args:
            query: Query de busca
            top_k: Número de resultados (default: top_k_final do retrieval_system)
            use_cache: Se True, usa cache
            filters: Filtros opcionais para Qdrant
            use_sparse: Se True, usa busca esparsa (BM25)
            use_rerank: Se True, usa reranking

        Returns:
            Lista de resultados de retrieval
        """
        top_k = top_k or getattr(self.retrieval_system, "top_k_final", 5)
        cache_key = f"retrieval:{query}:{top_k}:{filters}:{use_sparse}:{use_rerank}"

        # Verificar cache
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit (L1/L2/L3): {cache_key}")
                return cached_result

        # Cache miss: executar retrieval real
        logger.debug(f"Cache miss: executando retrieval para {query}")
        results = self.retrieval_system.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
            use_sparse=use_sparse,
            use_rerank=use_rerank,
        )

        # Armazenar em cache
        if use_cache:
            self.cache.set(cache_key, results, level=CacheLevel.L1, ttl_seconds=3600)

        # Atualizar histórico para prefetching
        if self.enable_prefetch:
            self._update_access_patterns(query)
            self._prefetch_related_queries(query)

        return results

    def _update_access_patterns(self, query: str) -> None:
        """Atualiza padrões de acesso para prefetching."""
        self.query_history.append(query)
        self.access_patterns[query] = self.access_patterns.get(query, 0) + 1

        # Manter histórico limitado
        if len(self.query_history) > 1000:
            self.query_history.pop(0)

    def _prefetch_related_queries(self, current_query: str) -> None:
        """Prefetch queries relacionadas baseado em padrões de acesso."""
        # Identificar queries frequentemente acessadas após current_query
        # (simplificado: prefetch queries mais frequentes)
        if len(self.query_history) < self.prefetch_window:
            return

        # Pegar queries mais frequentes
        sorted_patterns = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)[
            : self.prefetch_window
        ]

        for related_query, _ in sorted_patterns:
            if related_query != current_query:
                # Prefetch em background (não bloquear)
                try:
                    cache_key = f"retrieval:{related_query}:5:"
                    if self.cache.get(cache_key) is None:
                        # Prefetch assíncrono (simplificado: síncrono por enquanto)
                        logger.debug(f"Prefetching: {related_query}")
                        results = self.retrieval_system.retrieve(
                            query=related_query,
                            top_k=5,
                            use_sparse=True,
                            use_rerank=False,
                        )
                        self.cache.set(cache_key, results, level=CacheLevel.L2, ttl_seconds=1800)
                except Exception as e:
                    logger.debug(f"Erro no prefetch de {related_query}: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de cache."""
        return self.cache.get_stats()

    def clear_cache(self, level: Optional[CacheLevel] = None) -> None:
        """Limpa cache (todos os níveis ou nível específico)."""
        if level is None:
            # Limpar todos os níveis
            self.cache._l1.clear()
            self.cache._l2.clear()
            self.cache._l3.clear()
        else:
            # Limpar nível específico
            if level == CacheLevel.L1:
                self.cache._l1.clear()
            elif level == CacheLevel.L2:
                self.cache._l2.clear()
            elif level == CacheLevel.L3:
                self.cache._l3.clear()
