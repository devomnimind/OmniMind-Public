"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Neural Response Cache - Phase 21.

Implementa cache inteligente com TTL e LRU para reduzir latência e custo.
"""

import hashlib
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Resposta em cache com metadados."""

    answer: str
    confidence: float
    timestamp: float
    hits: int = 0
    backend: str = "unknown"


class NeuralResponseCache:
    """
    Cache LRU com TTL para respostas neurais.

    Features:
    - LRU eviction (Least Recently Used)
    - TTL (Time To Live) configurável
    - Hash de query para lookup rápido
    - Métricas de hit rate
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600.0):
        """
        Inicializa cache.

        Args:
            max_size: Número máximo de entradas
            ttl_seconds: Tempo de vida (segundos)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CachedResponse] = OrderedDict()
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def _hash_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Gera hash único para query + context.

        Args:
            query: Query original
            context: Contexto opcional

        Returns:
            Hash SHA256
        """
        # Incluir context no hash se fornecido
        key_data = query
        if context:
            # Ordenar chaves para hash consistente
            context_str = str(sorted(context.items()))
            key_data = f"{query}|{context_str}"

        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[CachedResponse]:
        """
        Busca resposta em cache.

        Args:
            query: Query original
            context: Contexto opcional

        Returns:
            CachedResponse se existe e válida, None caso contrário
        """
        self.total_requests += 1
        key = self._hash_query(query, context)

        if key not in self.cache:
            self.cache_misses += 1
            return None

        cached = self.cache[key]

        # Verificar TTL
        age = time.time() - cached.timestamp
        if age > self.ttl_seconds:
            # Expirado - remover do cache
            del self.cache[key]
            self.cache_misses += 1
            logger.debug(
                f"Cache expired: query={query[:30]}... (age={age:.0f}s > {self.ttl_seconds}s)"
            )
            return None

        # Cache hit válido
        self.cache_hits += 1
        cached.hits += 1

        # Move para o final (LRU)
        self.cache.move_to_end(key)

        logger.debug(f"Cache HIT: query={query[:30]}... (age={age:.0f}s, hits={cached.hits})")
        return cached

    def put(
        self,
        query: str,
        answer: str,
        confidence: float,
        backend: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Armazena resposta em cache.

        Args:
            query: Query original
            answer: Resposta gerada
            confidence: Confiança da resposta
            backend: Backend que gerou a resposta
            context: Contexto opcional
        """
        key = self._hash_query(query, context)

        # Eviction LRU se cheio
        if key not in self.cache and len(self.cache) >= self.max_size:
            # Remove o mais antigo (primeiro item)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache eviction: key={oldest_key[:16]}...")

        # Adicionar/atualizar cache
        self.cache[key] = CachedResponse(
            answer=answer,
            confidence=confidence,
            timestamp=time.time(),
            backend=backend,
        )

        # Move para o final (MRU - Most Recently Used)
        self.cache.move_to_end(key)

        logger.debug(f"Cache PUT: query={query[:30]}... (backend={backend})")

    def clear(self) -> None:
        """Limpa todo o cache."""
        self.cache.clear()
        logger.info("Cache cleared")

    def evict_expired(self) -> int:
        """
        Remove entradas expiradas.

        Returns:
            Número de entradas removidas
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, cached in self.cache.items()
            if (current_time - cached.timestamp) > self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Evicted {len(expired_keys)} expired entries")

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.

        Returns:
            Dict com métricas
        """
        hit_rate = self.cache_hits / self.total_requests if self.total_requests > 0 else 0.0

        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "current_size": len(self.cache),
            "max_size": self.max_size,
            "fill_ratio": len(self.cache) / self.max_size if self.max_size > 0 else 0.0,
            "ttl_seconds": self.ttl_seconds,
        }

    def log_stats(self) -> None:
        """Loga estatísticas do cache."""
        stats = self.get_stats()
        logger.info("=" * 60)
        logger.info("NEURAL RESPONSE CACHE STATS")
        logger.info(f"Total Requests: {stats['total_requests']}")
        logger.info(f"Cache Hits: {stats['cache_hits']}")
        logger.info(f"Cache Misses: {stats['cache_misses']}")
        logger.info(f"Hit Rate: {stats['hit_rate']:.2%}")
        logger.info(f"Current Size: {stats['current_size']}/{stats['max_size']}")
        logger.info(f"Fill Ratio: {stats['fill_ratio']:.2%}")
        logger.info(f"TTL: {stats['ttl_seconds']}s")
        logger.info("=" * 60)


# Singleton global
_response_cache = NeuralResponseCache(max_size=1000, ttl_seconds=3600.0)


def get_response_cache() -> NeuralResponseCache:
    """Retorna a instância global do cache."""
    return _response_cache
