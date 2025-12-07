"""Consciousness Metrics Indexer - Indexação de Métricas de Consciência no Qdrant

Indexa históricos de Φ, Ψ, σ do ModuleMetricsCollector no Qdrant para:
- Busca por similaridade de tríade
- Análise temporal de consciência
- RAG retrieval de estados de consciência similares

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


logger = logging.getLogger(__name__)


class ConsciousnessMetricsIndexer:
    """
    Indexa métricas de consciência (Φ, Ψ, σ) no Qdrant.

    Características:
    - Indexa históricos de ModuleMetricsCollector
    - Cria embeddings da tríade (normalização para vetor 3D)
    - Permite busca por similaridade de tríade
    - Suporta queries temporais
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "consciousness_metrics",
        metrics_dir: str = "data/monitor/consciousness_metrics",
    ):
        """
        Inicializa ConsciousnessMetricsIndexer.

        Args:
            qdrant_url: URL do Qdrant
            collection_name: Nome da coleção Qdrant
            metrics_dir: Diretório com arquivos JSONL de métricas
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Inicializar cliente Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # Criar coleção se não existir (vetor 3D para tríade normalizada)
        self._ensure_collection()

        logger.info(f"ConsciousnessMetricsIndexer inicializado: collection={collection_name}")

    def _ensure_collection(self) -> None:
        """Garante que a coleção existe no Qdrant."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Criando coleção: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=3,  # Vetor 3D: [phi, psi, sigma] normalizado
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"✅ Coleção {self.collection_name} criada")
            else:
                logger.debug(f"Coleção {self.collection_name} já existe")
        except Exception as e:
            logger.error(f"Erro ao criar/verificar coleção: {e}")
            raise

    def _normalize_triad(self, phi: float, psi: float, sigma: float) -> List[float]:
        """
        Normaliza tríade para vetor 3D unitário.

        Args:
            phi: Valor de Φ [0, 1]
            psi: Valor de Ψ [0, 1]
            sigma: Valor de σ [0, 1]

        Returns:
            Vetor 3D normalizado [phi_norm, psi_norm, sigma_norm]
        """
        import numpy as np

        # Clamp valores para [0, 1]
        phi = max(0.0, min(1.0, phi))
        psi = max(0.0, min(1.0, psi))
        sigma = max(0.0, min(1.0, sigma))

        # Normalizar para vetor unitário
        triad_vector = np.array([phi, psi, sigma])
        norm = np.linalg.norm(triad_vector)

        if norm > 0:
            normalized = triad_vector / norm
        else:
            normalized = np.array([0.0, 0.0, 0.0])

        return normalized.tolist()

    def index_triad_entry(
        self,
        step_id: str,
        phi: float,
        psi: float,
        sigma: float,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Indexa uma entrada de tríade no Qdrant.

        Args:
            step_id: ID do passo/evento
            phi: Valor de Φ
            psi: Valor de Ψ
            sigma: Valor de σ
            timestamp: Timestamp (opcional)
            metadata: Metadados adicionais (opcional)

        Returns:
            True se indexado com sucesso
        """
        try:
            # Normalizar tríade para vetor 3D
            vector = self._normalize_triad(phi, psi, sigma)

            # Preparar payload
            if timestamp is None:
                timestamp = __import__("time").time()

            payload = {
                "step_id": step_id,
                "phi": float(phi),
                "psi": float(psi),
                "sigma": float(sigma),
                "timestamp": float(timestamp),
                "timestamp_iso": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
                "metadata": json.dumps(metadata) if metadata else "{}",
            }

            # Gerar ID único (hash do step_id)
            point_id = hash(step_id) & 0x7FFFFFFFFFFFFFFF

            # Indexar no Qdrant
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.debug(
                f"✅ Tríade indexada: step_id={step_id}, Φ={phi:.4f}, Ψ={psi:.4f}, σ={sigma:.4f}"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao indexar tríade: {e}")
            return False

    def index_from_jsonl(self, jsonl_file: Optional[Path] = None) -> int:
        """
        Indexa métricas de arquivo JSONL do ModuleMetricsCollector.

        Args:
            jsonl_file: Caminho do arquivo JSONL (opcional, usa padrão)

        Returns:
            Número de entradas indexadas
        """
        if jsonl_file is None:
            # Tentar encontrar arquivo de consciência completa
            consciousness_file = self.metrics_dir / "consciousness_triad_history.jsonl"
            if not consciousness_file.exists():
                logger.warning(f"Arquivo não encontrado: {consciousness_file}")
                return 0
            jsonl_file = consciousness_file

        if not jsonl_file.exists():
            logger.warning(f"Arquivo não encontrado: {jsonl_file}")
            return 0

        indexed_count = 0
        try:
            with open(jsonl_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        step_id = data.get("step_id", f"line_{line_num}")
                        phi = float(data.get("phi", 0.0))
                        psi = float(data.get("psi", 0.0))
                        sigma = float(data.get("sigma", 0.0))
                        timestamp = data.get("timestamp", __import__("time").time())
                        metadata = data.get("metadata", {})

                        if self.index_triad_entry(
                            step_id=step_id,
                            phi=phi,
                            psi=psi,
                            sigma=sigma,
                            timestamp=timestamp,
                            metadata=metadata,
                        ):
                            indexed_count += 1

                    except Exception as e:
                        logger.warning(f"Erro ao processar linha {line_num}: {e}")
                        continue

            logger.info(f"✅ {indexed_count} entradas indexadas de {jsonl_file}")
            return indexed_count

        except Exception as e:
            logger.error(f"Erro ao ler arquivo JSONL: {e}")
            return 0

    def search_similar_triad(
        self,
        phi: float,
        psi: float,
        sigma: float,
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Busca tríades similares por similaridade de cosseno.

        Args:
            phi: Valor de Φ de referência
            psi: Valor de Ψ de referência
            sigma: Valor de σ de referência
            top_k: Número de resultados
            threshold: Threshold de similaridade (0-1)

        Returns:
            Lista de tríades similares com scores
        """
        try:
            # Normalizar tríade de referência
            query_vector = self._normalize_triad(phi, psi, sigma)

            # Buscar no Qdrant (com fallback para diferentes APIs)
            # mypy não reconhece método dinâmico do QdrantClient (precisa de stubs)
            query_points = getattr(self.client, "query_points", None)
            if callable(query_points):
                results = query_points(  # type: ignore[attr-defined]
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=threshold,
                    with_payload=True,
                )
                results = results.points if hasattr(results, "points") else results
            else:
                results = self.client.search(  # type: ignore[attr-defined]
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=threshold,
                )

            # Formatar resultados
            formatted_results = []
            for result in results:
                payload = result.payload or {}
                formatted_results.append(
                    {
                        "step_id": payload.get("step_id", "unknown"),
                        "phi": float(payload.get("phi", 0.0)),
                        "psi": float(payload.get("psi", 0.0)),
                        "sigma": float(payload.get("sigma", 0.0)),
                        "timestamp": float(payload.get("timestamp", 0.0)),
                        "timestamp_iso": payload.get("timestamp_iso", ""),
                        "similarity": float(result.score),
                        "metadata": json.loads(payload.get("metadata", "{}")),
                    }
                )

            logger.info(f"✅ {len(formatted_results)} tríades similares encontradas")
            return formatted_results

        except Exception as e:
            logger.error(f"Erro ao buscar tríades similares: {e}")
            return []

    def get_triad_history_range(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Obtém histórico de tríades em um range temporal.

        Args:
            start_time: Início do range (opcional)
            end_time: Fim do range (opcional)
            limit: Limite de resultados

        Returns:
            Lista de tríades no range
        """
        try:
            # Scroll todos os pontos
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
            )

            results = []
            for point in points:
                if not point.payload:
                    continue

                timestamp = point.payload.get("timestamp", 0.0)
                timestamp_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

                # Filtrar por range temporal se especificado
                if start_time and timestamp_dt < start_time:
                    continue
                if end_time and timestamp_dt > end_time:
                    continue

                results.append(
                    {
                        "step_id": point.payload.get("step_id", "unknown"),
                        "phi": float(point.payload.get("phi", 0.0)),
                        "psi": float(point.payload.get("psi", 0.0)),
                        "sigma": float(point.payload.get("sigma", 0.0)),
                        "timestamp": float(timestamp),
                        "timestamp_iso": point.payload.get("timestamp_iso", ""),
                        "metadata": json.loads(point.payload.get("metadata", "{}")),
                    }
                )

            # Ordenar por timestamp
            results.sort(key=lambda x: x["timestamp"])

            logger.info(f"✅ {len(results)} tríades no range temporal")
            return results

        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas da coleção.

        Returns:
            Dict com estatísticas
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": info.points_count,
                "vectors_count": getattr(info, "vectors_count", info.indexed_vectors_count),
                "indexed_vectors_count": info.indexed_vectors_count,
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"error": str(e)}


# Singleton instance
_consciousness_metrics_indexer_instance: Optional[ConsciousnessMetricsIndexer] = None


def get_consciousness_metrics_indexer(
    qdrant_url: str = "http://localhost:6333",
    collection_name: str = "consciousness_metrics",
) -> ConsciousnessMetricsIndexer:
    """
    Obtém instância singleton de ConsciousnessMetricsIndexer.

    Args:
        qdrant_url: URL do Qdrant
        collection_name: Nome da coleção

    Returns:
        ConsciousnessMetricsIndexer: Instância singleton
    """
    global _consciousness_metrics_indexer_instance
    if _consciousness_metrics_indexer_instance is None:
        _consciousness_metrics_indexer_instance = ConsciousnessMetricsIndexer(
            qdrant_url=qdrant_url, collection_name=collection_name
        )
    return _consciousness_metrics_indexer_instance
