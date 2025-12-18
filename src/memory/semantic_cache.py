"""
Semantic Cache Layer - Cache Semântico de Respostas de Agentes

Cache semântico usando Qdrant para armazenar e recuperar respostas de agentes
baseado em similaridade semântica, não apenas match exato.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de cache semântico."""

    task: str
    response: str
    agent_name: str
    similarity_score: float
    cached_at: datetime
    hit_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SemanticCacheLayer:
    """
    Cache semântico de respostas de agentes.

    Usa Qdrant para armazenar respostas e recuperar baseado em similaridade
    semântica (não apenas match exato). Integra com SystemicMemoryTrace.

    Características:
    - Similarity threshold configurável (default: 0.95)
    - TTL configurável (default: 30 dias)
    - Estatísticas de hit/miss
    - Integração com embeddings existente (all-MiniLM-L6-v2)
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "agent_semantic_cache",
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.95,
        ttl_days: int = 30,
        embedding_model: Optional[SentenceTransformer] = None,
    ):
        """
        Inicializa cache semântico.

        Args:
            qdrant_url: URL do Qdrant
            collection_name: Nome da coleção no Qdrant
            model_name: Nome do modelo de embeddings
            similarity_threshold: Threshold de similaridade (0.0 a 1.0)
            ttl_days: Tempo de vida em dias
            embedding_model: Modelo de embeddings opcional (reutilizar se disponível)
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.ttl_days = ttl_days

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

            # Resolve model name for offline compatibility
            try:
                from src.utils.offline_mode import resolve_sentence_transformer_name

                resolved_model_name = resolve_sentence_transformer_name(model_name)
            except ImportError:
                resolved_model_name = model_name

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

        # Inicializar Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # Criar coleção se não existir
        self._ensure_collection()

        # Estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "cache_size": 0,
        }

        logger.info(
            f"SemanticCacheLayer inicializado: collection={collection_name}, "
            f"threshold={similarity_threshold}, ttl={ttl_days}d"
        )

    def _ensure_collection(self) -> None:
        """Cria coleção no Qdrant se não existir."""
        try:
            self.client.get_collection(collection_name=self.collection_name)
            logger.debug(f"Coleção {self.collection_name} já existe")
        except Exception:
            logger.info(f"Criando coleção {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=self.embedding_dim, distance=qdrant_models.Distance.COSINE
                ),
            )

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para texto.

        Args:
            text: Texto para embedar

        Returns:
            Lista de floats (embedding)
        """
        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            # Fallback: hash-based embedding
            return self._hash_based_embedding(text)

    def _hash_based_embedding(self, text: str) -> List[float]:
        """
        Fallback: embedding baseado em hash.

        Args:
            text: Texto

        Returns:
            Lista de floats (embedding determinístico)
        """
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        embedding = []
        for i in range(self.embedding_dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding.append((byte_val / 255.0) * 2 - 1)
        return embedding

    def _generate_id(self, task: str, agent_name: str) -> int:
        """
        Gera ID único para entrada de cache.

        Args:
            task: Tarefa
            agent_name: Nome do agente

        Returns:
            ID inteiro
        """
        combined = f"{agent_name}:{task}"
        hash_obj = hashlib.md5(combined.encode())
        # Usa primeiros 8 bytes do hash como int
        return int(hash_obj.hexdigest()[:16], 16) % (2**31)

    def get_or_compute(
        self,
        task: str,
        agent_callable: Callable[[], str],
        agent_name: str = "unknown",
        force_compute: bool = False,
    ) -> str:
        """
        Tenta recuperar do cache, ou computa e armazena.

        Args:
            task: Tarefa/query do agente
            agent_callable: Função que computa resposta (chamada se cache miss)
            agent_name: Nome do agente (para metadata)
            force_compute: Se True, força computação mesmo com cache hit

        Returns:
            Resposta (do cache ou computada)
        """
        self.stats["total_queries"] += 1

        if force_compute:
            logger.debug(f"Forçando computação para: {task[:50]}...")
            response = agent_callable()
            self._store(task, response, agent_name)
            self.stats["misses"] += 1
            return response

        # Buscar no cache
        cached = self._search_cache(task, agent_name)

        if cached and cached["similarity_score"] >= self.similarity_threshold:
            # Cache hit
            self.stats["hits"] += 1
            logger.debug(
                f"Cache HIT: similarity={cached['similarity_score']:.3f}, " f"task={task[:50]}..."
            )
            return cached["response"]

        # Cache miss - computar
        self.stats["misses"] += 1
        logger.debug(f"Cache MISS: task={task[:50]}...")
        response = agent_callable()

        # Armazenar no cache
        self._store(task, response, agent_name)

        return response

    def _search_cache(
        self, task: str, agent_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Busca no cache por similaridade semântica.

        Args:
            task: Tarefa/query
            agent_name: Nome do agente (opcional, para filtrar)

        Returns:
            Entrada de cache se encontrada, None caso contrário
        """
        try:
            # Gerar embedding da query
            query_embedding = self._generate_embedding(task)

            # Buscar no Qdrant
            # QdrantClient.search retorna uma lista de ScoredPoint
            # mypy não reconhece método dinâmico do QdrantClient (precisa de stubs)
            results = self.client.search(  # type: ignore[attr-defined]
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=1,
                score_threshold=self.similarity_threshold,
                with_payload=True,
            )

            if not results:
                return None

            # Pegar melhor resultado
            best_match = results[0]

            # Verificar TTL
            payload = best_match.payload or {}
            cached_at_str = payload.get("cached_at")
            if cached_at_str:
                try:
                    cached_at = datetime.fromisoformat(cached_at_str)
                    age = datetime.now() - cached_at
                    if age > timedelta(days=self.ttl_days):
                        logger.debug(f"Cache entry expirada (age: {age.days}d)")
                        return None
                except Exception:
                    pass  # Ignora erro de parsing

            # Filtrar por agente se especificado
            if agent_name and payload.get("agent_name") != agent_name:
                return None

            return {
                "response": payload.get("response", ""),
                "similarity_score": best_match.score or 0.0,
                "agent_name": payload.get("agent_name", "unknown"),
                "cached_at": payload.get("cached_at"),
            }

        except Exception as e:
            logger.warning(f"Erro ao buscar no cache: {e}")
            return None

    def _store(self, task: str, response: str, agent_name: str) -> None:
        """
        Armazena entrada no cache.

        Args:
            task: Tarefa/query
            response: Resposta do agente
            agent_name: Nome do agente
        """
        try:
            # Gerar embedding da tarefa
            task_embedding = self._generate_embedding(task)

            # Gerar ID único
            cache_id = self._generate_id(task, agent_name)

            # Payload
            payload = {
                "task": task,
                "response": response,
                "agent_name": agent_name,
                "cached_at": datetime.now().isoformat(),
                "hit_count": 0,
            }

            # Upsert no Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=cache_id,
                        vector=task_embedding,
                        payload=payload,
                    )
                ],
            )

            self.stats["cache_size"] += 1
            logger.debug(f"Cache armazenado: id={cache_id}, agent={agent_name}")

        except Exception as e:
            logger.warning(f"Erro ao armazenar no cache: {e}")

    def get_effectiveness(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de efetividade do cache.

        Returns:
            Dicionário com estatísticas
        """
        total = self.stats["total_queries"]
        if total == 0:
            hit_rate = 0.0
        else:
            hit_rate = self.stats["hits"] / total

        # Atualizar tamanho do cache
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            points_count = (
                collection_info.points_count
                if hasattr(collection_info, "points_count")
                and collection_info.points_count is not None
                else 0
            )
            self.stats["cache_size"] = int(points_count)
        except Exception:
            pass

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "total_queries": total,
            "hit_rate": hit_rate,
            "cache_size": self.stats["cache_size"],
            "similarity_threshold": self.similarity_threshold,
            "ttl_days": self.ttl_days,
        }

    def clear_cache(self, agent_name: Optional[str] = None) -> int:
        """
        Limpa cache (opcionalmente filtrado por agente).

        Args:
            agent_name: Nome do agente (opcional, se None limpa tudo)

        Returns:
            Número de entradas removidas
        """
        try:
            if agent_name:
                # Filtrar por agente
                # Nota: Qdrant não suporta filtro direto, precisaria buscar e deletar
                # Por enquanto, limpa tudo
                logger.warning("Filtro por agente não implementado, limpando tudo")

            # Limpar coleção
            self.client.delete_collection(collection_name=self.collection_name)
            self._ensure_collection()

            removed = self.stats["cache_size"]
            self.stats["cache_size"] = 0
            logger.info(f"Cache limpo: {removed} entradas removidas")
            return removed
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return 0
