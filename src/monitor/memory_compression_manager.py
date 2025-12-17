"""
Memory Compression Manager
==========================
Monitora memória do sistema e comprime fluxos em embeddings quando limite atingido.
Implementa auto-aprendizado através de vetorização de histórico.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import psutil

logger = logging.getLogger("MemoryCompressionManager")


@dataclass
class CompressionMetrics:
    """Métricas de compressão de memória."""
    timestamp: str
    memory_percent_before: float
    memory_percent_after: float
    flows_compressed: int
    compression_ratio: float
    knowledge_vector_dim: int
    status: str  # "success", "in_progress", "skipped"


class MemoryCompressionManager:
    """Gerencia compressão automática de memória via vetorização."""

    def __init__(self, memory_threshold: float = 75.0, max_flows_in_memory: int = 5000):
        """
        Args:
            memory_threshold: Percentual de RAM quando iniciar compressão
            max_flows_in_memory: Máximo de fluxos antes de comprimir
        """
        self.memory_threshold = memory_threshold
        self.max_flows_in_memory = max_flows_in_memory
        self.compression_history: List[CompressionMetrics] = []
        self.knowledge_vectors: Dict[str, np.ndarray] = {}

    def check_memory_status(self) -> Dict[str, Any]:
        """Verifica status da memória do sistema."""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "used_gb": memory.used / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent": memory.percent,
            "swap_percent": psutil.swap_memory().percent,
            "needs_compression": memory.percent > self.memory_threshold,
        }

    def should_compress(self, flows_count: int, memory_status: Dict) -> bool:
        """Determina se deve comprimir memória."""
        return (
            memory_status["percent"] > self.memory_threshold
            or flows_count > self.max_flows_in_memory
        )

    def compress_flows(
        self, flows: List[Dict[str, Any]], flow_id_prefix: str = "flow"
    ) -> CompressionMetrics:
        """
        Comprime lista de fluxos em vetor de conhecimento.

        Args:
            flows: Lista de fluxos a comprimir
            flow_id_prefix: Prefixo para identificar grupo de fluxos

        Returns:
            CompressionMetrics com resultado da compressão
        """
        memory_before = psutil.virtual_memory().percent

        try:
            # 1. Extrair features dos fluxos
            features_list = []
            for flow in flows:
                features = self._extract_flow_features(flow)
                if features is not None:
                    features_list.append(features)

            if not features_list:
                logger.warning("Nenhum flow com features válidas para compressão")
                return CompressionMetrics(
                    timestamp=datetime.utcnow().isoformat(),
                    memory_percent_before=memory_before,
                    memory_percent_after=memory_before,
                    flows_compressed=0,
                    compression_ratio=0.0,
                    knowledge_vector_dim=0,
                    status="skipped",
                )

            # 2. Criar vetor de conhecimento (média + PCA simples)
            feature_array = np.array(features_list, dtype=np.float32)
            knowledge_vector = np.mean(feature_array, axis=0)  # Média agregada

            # 3. Armazenar vetor
            vector_id = f"{flow_id_prefix}_{datetime.utcnow().timestamp()}"
            self.knowledge_vectors[vector_id] = knowledge_vector

            # 4. Registrar métrica
            memory_after = psutil.virtual_memory().percent
            compression_ratio = len(flows) / (len(knowledge_vector) + 1)

            metric = CompressionMetrics(
                timestamp=datetime.utcnow().isoformat(),
                memory_percent_before=memory_before,
                memory_percent_after=memory_after,
                flows_compressed=len(flows),
                compression_ratio=compression_ratio,
                knowledge_vector_dim=len(knowledge_vector),
                status="success",
            )

            self.compression_history.append(metric)
            logger.info(
                f"✅ Compressão concluída: {len(flows)} fluxos → "
                f"vetor {len(knowledge_vector)}D | "
                f"RAM {memory_before:.1f}% → {memory_after:.1f}%"
            )

            return metric

        except Exception as e:
            logger.error(f"❌ Erro na compressão: {e}")
            return CompressionMetrics(
                timestamp=datetime.utcnow().isoformat(),
                memory_percent_before=memory_before,
                memory_percent_after=psutil.virtual_memory().percent,
                flows_compressed=0,
                compression_ratio=0.0,
                knowledge_vector_dim=0,
                status="failed",
            )

    def _extract_flow_features(self, flow: Dict[str, Any]) -> Optional[List[float]]:
        """Extrai features numéricas de um fluxo."""
        try:
            features = []

            # Features de intensidade/energia
            if "intensity" in flow:
                intensity_val = flow["intensity"]
                if isinstance(intensity_val, (int, float)):
                    features.append(float(intensity_val))
                elif hasattr(intensity_val, "value"):
                    features.append(float(intensity_val.value))

            # Features de timestamp
            if "timestamp" in flow:
                features.append(hash(str(flow["timestamp"])) % 100 / 100.0)

            # Features de origem/destino
            if "source_id" in flow:
                features.append(hash(flow["source_id"]) % 100 / 100.0)
            if "target_id" in flow:
                features.append(hash(flow["target_id"]) % 100 / 100.0)

            # Features de conteúdo (se houver)
            if "content" in flow and isinstance(flow["content"], dict):
                content_hash = hash(json.dumps(flow["content"], sort_keys=True))
                features.append((content_hash % 100) / 100.0)

            return features if len(features) > 0 else None

        except Exception as e:
            logger.debug(f"Erro extraindo features de flow: {e}")
            return None

    def get_compression_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de compressão."""
        if not self.compression_history:
            return {"compressions_count": 0, "total_flows_compressed": 0}

        total_compressed = sum(m.flows_compressed for m in self.compression_history)
        avg_ratio = np.mean([m.compression_ratio for m in self.compression_history])

        return {
            "compressions_count": len(self.compression_history),
            "total_flows_compressed": total_compressed,
            "average_compression_ratio": float(avg_ratio),
            "knowledge_vectors_stored": len(self.knowledge_vectors),
            "last_compression": (
                self.compression_history[-1].timestamp
                if self.compression_history
                else None
            ),
        }

    def save_checkpoint(self, filepath: str) -> bool:
        """Salva checkpoint de vetores de conhecimento."""
        try:
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "compression_stats": self.get_compression_stats(),
                "knowledge_vectors": {
                    k: v.tolist() for k, v in self.knowledge_vectors.items()
                },
                "compression_history": [
                    asdict(m) for m in self.compression_history[-100:]  # Últimas 100
                ],
            }
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"✅ Checkpoint salvo: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro salvando checkpoint: {e}")
            return False
            return False
